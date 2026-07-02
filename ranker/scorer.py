"""
HUMAN-POTENTIAL-GRAPH — Core Scoring Engine (multi-domain)
Multi-signal fusion ranker. Originally built only for "Senior AI Engineer" —
now generalized to rank candidates across any hiring domain in domains.py
(AI/ML, Backend, Data Engineering, DevOps/SRE, Frontend, Data Analyst/BI,
Product Management, QA/SDET). Each candidate is auto-detected into their
best-fit domain, then scored against that domain's own rubric — an
excellent backend engineer is no longer penalized for not knowing FAISS.

Architecture:
  L0  Signal Ingestion          — parse all 8 candidate data dimensions
  L0' Domain Detection          — classify candidate into best-fit domain
  L1  Skill Match (30%)         — proficiency × duration × assessment × endorsements
  L2  Career Trajectory (40%)   — semantic career analysis, production evidence
  L3  Experience Fit (10%)      — YoE window match (5–9yr ideal)
  L4  Behavioral Availability   — recency, response rate, GitHub, notice, location
      (15%)
  L5  Education (5%)            — tier + degree + STEM field alignment
      × Disqualifier Penalty    — keyword stuffers, consulting-only, wrong domain,
                                   inactive, honeypots
"""

import re
from datetime import date, datetime

from .signals import (
    WEIGHTS, CONSULTING_GIANTS, PREFERRED_LOCATIONS,
    PROFICIENCY_MULT, TIER_SCORES, DEGREE_SCORES, STEM_FIELDS,
)
from .domains import DOMAINS, GLOBAL_NONTECH_TITLES

TODAY = date(2026, 6, 28)

# ── HELPERS ────────────────────────────────────────────────────────────────────

def _norm(text: str) -> str:
    """Lowercase, normalise separators for consistent matching."""
    if not text:
        return ""
    return re.sub(r"[_\-/]", " ", str(text).lower().strip())


def _days_since(date_str: str) -> int:
    """Days elapsed since date_str (YYYY-MM-DD). Returns 9999 on parse error."""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return max(0, (TODAY - d).days)
    except Exception:
        return 9999


def _candidate_text_blob(candidate: dict) -> tuple[str, str, str]:
    """Return (skills_text, career_text, title_text) normalised, for domain scoring."""
    skills_text = " ".join(_norm(s.get("name", "")) for s in candidate.get("skills", []))
    career_text = " ".join(_norm(j.get("description", "")) for j in candidate.get("career_history", []))
    title_text = " ".join(
        [_norm(candidate["profile"].get("current_title", ""))]
        + [_norm(j.get("title", "")) for j in candidate.get("career_history", [])]
    )
    return skills_text, career_text, title_text


# ── L0': DOMAIN DETECTION ─────────────────────────────────────────────────────

def detect_domain(candidate: dict) -> tuple[str, dict, dict]:
    """
    Classify a candidate into their best-fit hiring domain.

    Scores the candidate against every domain in DOMAINS using three signals:
      - title keyword overlap (heaviest weight — most direct signal)
      - core skill overlap
      - career-phrase overlap

    Returns:
        domain_id     — key into DOMAINS (e.g. "ai_ml_engineer")
        domain_prof   — the domain's profile dict
        domain_scores — all domains' raw match scores (for transparency/debugging)
    """
    skills_text, career_text, title_text = _candidate_text_blob(candidate)
    full_text = skills_text + " " + career_text

    domain_scores: dict[str, float] = {}

    for dom_id, prof in DOMAINS.items():
        title_hits = sum(1 for kw in prof["title_keywords"] if kw in title_text)
        skill_hits = sum(1 for kw in prof["core_skills"] if kw in full_text)
        phrase_hits = sum(1 for kw in prof["career_phrases"] if kw in career_text)

        score = title_hits * 3.0 + skill_hits * 1.0 + phrase_hits * 0.5
        domain_scores[dom_id] = score

    best_domain = max(domain_scores, key=domain_scores.get)

    return best_domain, DOMAINS[best_domain], domain_scores


# ── L1: SKILL MATCH ───────────────────────────────────────────────────────────

def score_skills(candidate: dict, domain_prof: dict) -> tuple[float, list[str]]:
    """
    Skill Match Score (0–1), scored against the candidate's detected domain.

    Key insight: Skill *listings* can be keyword-stuffed.
    We weight each skill by: proficiency × time-in-use × platform-assessment × endorsements.
    We ALSO mine career descriptions for implicit skill evidence (unlisted but demonstrated).
    """
    skills = candidate.get("skills", [])
    assessments = candidate["redrob_signals"].get("skill_assessment_scores", {})

    core_required = domain_prof["core_skills"]
    bonus_skills  = domain_prof["bonus_skills"]

    raw_score = 0.0
    core_hits: list[str] = []

    for skill in skills:
        name_raw = skill.get("name", "")
        name = _norm(name_raw)

        prof_mult = PROFICIENCY_MULT.get(skill.get("proficiency", "beginner"), 0.3)
        duration_ratio = min(skill.get("duration_months", 0), 60) / 60
        endorse_boost = min(skill.get("endorsements", 0), 50) / 500

        assess_val = assessments.get(name_raw) or assessments.get(name)
        assess_mult = (0.5 + (assess_val / 100) * 0.5) if assess_val is not None else 1.0

        skill_weight = prof_mult * (0.7 + 0.3 * duration_ratio) * assess_mult + endorse_boost

        is_core  = name in core_required or any(c in name for c in core_required)
        is_bonus = name in bonus_skills  or any(b in name for b in bonus_skills)

        if is_core:
            core_hits.append(name_raw)
            raw_score += skill_weight * 2.5
        elif is_bonus:
            raw_score += skill_weight * 1.0

    career_text  = " ".join(_norm(j.get("description", "")) for j in candidate.get("career_history", []))
    summary_text = _norm(candidate["profile"].get("summary", ""))
    full_text    = career_text + " " + summary_text
    listed_names = {_norm(s.get("name", "")) for s in skills}

    for term in core_required:
        if term in full_text and not any(term in n for n in listed_names):
            raw_score += 0.5

    for term in bonus_skills:
        if term in full_text and not any(term in n for n in listed_names):
            raw_score += 0.15

    return min(raw_score / 20.0, 1.0), core_hits[:6]


# ── L2: CAREER TRAJECTORY ─────────────────────────────────────────────────────

def score_career(candidate: dict, domain_prof: dict) -> tuple[float, str]:
    """
    Career Trajectory Score (0–1) — the most important signal, scored against
    the candidate's detected domain's own career-phrase and title vocabulary.
    """
    career  = candidate.get("career_history", [])
    profile = candidate.get("profile", {})

    if not career:
        return 0.05, "No career history"

    career_phrases = domain_prof["career_phrases"]
    title_keywords = domain_prof["title_keywords"]

    total_months = max(sum(j.get("duration_months", 0) for j in career), 1)
    career_score = 0.0
    evidence: list[str] = []

    # ── 1. Company-type analysis ───────────────────────────────────────────────
    consulting_months = 0
    domain_months = 0

    for job in career:
        company     = _norm(job.get("company", ""))
        industry    = _norm(job.get("industry", ""))
        title       = _norm(job.get("title", ""))
        duration    = job.get("duration_months", 0)
        description = _norm(job.get("description", ""))

        is_consulting   = any(giant in company for giant in CONSULTING_GIANTS)
        is_product_tech = any(x in industry for x in ["software", "ai", "fintech", "saas", "startup", "internet", "e-commerce", "ecommerce", "food delivery", "tech"])
        is_domain_title = any(kw in title for kw in title_keywords)
        is_domain_desc  = sum(1 for p in career_phrases if p in description) >= 2

        if is_consulting:
            consulting_months += duration
        if (is_product_tech or is_domain_title) and (is_domain_title or is_domain_desc):
            domain_months += duration

    consulting_ratio  = consulting_months / total_months
    domain_ratio       = domain_months / total_months
    consulting_penalty = max(0.30, 1.0 - consulting_ratio * 0.70)

    career_score += domain_ratio * 0.50

    if consulting_ratio > 0.8:
        evidence.append("⚠️ Primarily consulting background")
    elif domain_ratio > 0.40:
        evidence.append(f"✓ {int(domain_ratio * 100)}% career in target domain")

    # ── 2. Semantic description mining ────────────────────────────────────────
    all_desc  = " ".join(_norm(j.get("description", "")) for j in career)
    phrase_hits = {p for p in career_phrases if p in all_desc}
    desc_score  = min(len(phrase_hits) / 8.0, 1.0) * 0.35
    career_score += desc_score

    if len(phrase_hits) >= 3:
        evidence.append(f"✓ {len(phrase_hits)} domain-relevant signals in descriptions")
    elif phrase_hits:
        evidence.append(f"✓ {len(phrase_hits)} domain signals found")

    # ── 3. Current role relevance ──────────────────────────────────────────────
    current_title = _norm(profile.get("current_title", ""))
    if any(kw in current_title for kw in title_keywords):
        career_score += 0.15
        evidence.append(f"✓ Role: {profile.get('current_title', '')}")

    # ── 4. Title-trajectory velocity ─────────────────────────────────────────
    if len(career) >= 2:
        recent = [_norm(j.get("title", "")) for j in career[:2]]
        older  = [_norm(j.get("title", "")) for j in career[2:]]
        r_hit  = sum(1 for t in recent if any(kw in t for kw in title_keywords))
        o_hit  = sum(1 for t in older  if any(kw in t for kw in title_keywords)) if older else 0
        if r_hit > o_hit:
            career_score += 0.10
            evidence.append("✓ Career trending toward this domain")

    # ── 5. Startup/mid-size exposure ─────────────────────────────────────────
    if any(j.get("company_size", "") in ["1-10", "11-50", "51-200", "201-500"]
           for j in career[:2]):
        career_score += 0.05

    final = min(career_score * consulting_penalty, 1.0)
    return final, "; ".join(evidence) or "Limited domain-relevant career evidence"


# ── L3: EXPERIENCE FIT ────────────────────────────────────────────────────────

def score_experience(candidate: dict) -> float:
    """Experience Fit (0–1). Sweet spot: 5–9 years. Graded penalty outside the band."""
    yoe = candidate["profile"].get("years_of_experience", 0)
    if   5  <= yoe <= 9:  return 1.00
    elif 4  <= yoe <  5:  return 0.85
    elif 9  <  yoe <= 11: return 0.80
    elif 3  <= yoe <  4:  return 0.65
    elif yoe > 11:        return 0.65
    elif 2  <= yoe <  3:  return 0.40
    else:                  return 0.20


# ── L4: BEHAVIORAL AVAILABILITY ───────────────────────────────────────────────

def score_behavioral(candidate: dict) -> tuple[float, str]:
    """Behavioral Availability Score (0–1). Domain-independent."""
    sig     = candidate["redrob_signals"]
    profile = candidate["profile"]
    score   = 0.0
    signals: list[str] = []

    days_inactive = _days_since(sig.get("last_active_date", "2020-01-01"))
    recency = (1.0 if days_inactive <= 30  else
               0.85 if days_inactive <= 90  else
               0.60 if days_inactive <= 180 else
               0.30 if days_inactive <= 365 else 0.05)
    score += recency * 0.25
    if days_inactive > 365: signals.append(f"⚠️ inactive {days_inactive}d")
    elif days_inactive <= 90: signals.append(f"active {days_inactive}d ago")

    if sig.get("open_to_work_flag"):
        score += 0.15
        signals.append("open-to-work")

    rr = sig.get("recruiter_response_rate", 0)
    score += rr * 0.20
    if rr >= 0.60: signals.append(f"RR={rr:.0%}")

    rt = sig.get("avg_response_time_hours", 9999)
    rt_score = (1.0 if rt <= 4   else
                0.85 if rt <= 24  else
                0.60 if rt <= 72  else
                0.30 if rt <= 168 else 0.10)
    score += rt_score * 0.10

    gh = sig.get("github_activity_score", -1)
    score += (gh / 100.0 if gh >= 0 else 0.10) * 0.10
    if gh > 30: signals.append(f"GH={gh:.0f}")

    score += sig.get("interview_completion_rate", 0) * 0.08

    notice = sig.get("notice_period_days", 90)
    np_score = (1.0 if notice == 0  else
                0.90 if notice <= 30 else
                0.70 if notice <= 60 else
                0.50 if notice <= 90 else 0.20)
    score += np_score * 0.07
    if notice <= 30: signals.append(f"notice={notice}d")

    loc = _norm(profile.get("location", "") + " " + profile.get("country", ""))
    relocate = sig.get("willing_to_relocate", False)
    if any(pl in loc for pl in PREFERRED_LOCATIONS):
        score += 0.05
        signals.append("India ✓")
    elif relocate:
        score += 0.025

    return min(score, 1.0), "; ".join(signals) or "low engagement"


# ── L5: EDUCATION ─────────────────────────────────────────────────────────────

def score_education(candidate: dict) -> float:
    """Education signal (minor, 5%). Domain-independent tier × degree × STEM field."""
    education = candidate.get("education", [])
    if not education:
        return 0.40

    best = 0.0
    for edu in education:
        tier  = TIER_SCORES.get(edu.get("tier", "unknown"), 0.45)
        deg   = _norm(edu.get("degree", ""))
        field = _norm(edu.get("field_of_study", ""))

        deg_score = 0.50
        for d, s in DEGREE_SCORES.items():
            if d in deg:
                deg_score = s
                break

        field_bonus = 0.15 if any(sf in field for sf in STEM_FIELDS) else 0.0
        best = max(best, min(tier * 0.5 + deg_score * 0.5 + field_bonus, 1.0))

    return best


# ── DISQUALIFIER DETECTION ────────────────────────────────────────────────────

def compute_disqualifier(candidate: dict, domain_prof: dict) -> tuple[float, str]:
    """
    Detect the traps a naive keyword-matcher would miss, scored against the
    candidate's detected domain.
    """
    profile = candidate.get("profile", {})
    career  = candidate.get("career_history", [])
    skills  = candidate.get("skills", [])
    sig     = candidate.get("redrob_signals", {})

    core_required        = domain_prof["core_skills"]
    wrong_domain_skills  = domain_prof["wrong_domain_skills"]
    disqualified_titles  = domain_prof["disqualified_titles"] | GLOBAL_NONTECH_TITLES
    career_phrases       = domain_prof["career_phrases"]
    title_keywords       = domain_prof["title_keywords"]

    penalty = 1.0
    reasons: list[str] = []

    # 1. Keyword stuffer
    current_title = _norm(profile.get("current_title", ""))
    skill_names   = [_norm(s.get("name", "")) for s in skills]
    all_titles    = [_norm(j.get("title", "")) for j in career]

    is_nontechnical = any(t in current_title for t in disqualified_titles)
    has_domain_skills = sum(1 for sn in skill_names if any(c in sn for c in core_required)) >= 3
    ever_domain_role  = any(any(kw in t for kw in title_keywords) for t in all_titles)

    if is_nontechnical and has_domain_skills and not ever_domain_role:
        penalty *= 0.20
        reasons.append("keyword stuffer: non-technical title with domain skills, no domain career history")

    # 2. Pure consulting
    all_companies = [_norm(j.get("company", "")) for j in career]
    consulting_n  = sum(1 for c in all_companies if any(g in c for g in CONSULTING_GIANTS))

    if career and consulting_n == len(career):
        penalty *= 0.35
        reasons.append("entire career at consulting firms")
    elif consulting_n > 0 and len(career) > 1:
        penalty *= max(0.50, 1.0 - (consulting_n / len(career)) * 0.60)

    # 3. Wrong domain (skills that signal a DIFFERENT domain, with no evidence of this one)
    all_text = (
        " ".join(_norm(j.get("description", "")) for j in career)
        + " " + " ".join(skill_names)
    )
    wrong_hits = sum(1 for d in wrong_domain_skills if d in all_text)
    domain_hits = sum(1 for p in career_phrases if p in all_text)

    if wrong_hits >= 3 and domain_hits == 0:
        penalty *= 0.25
        reasons.append("primary skills/experience belong to a different domain")

    # 4. Unreachable
    days_inactive = _days_since(sig.get("last_active_date", "2020-01-01"))
    rr = sig.get("recruiter_response_rate", 0)

    if days_inactive > 365:
        penalty *= 0.35
        reasons.append(f"inactive >12 months ({days_inactive}d)")
    elif days_inactive > 270 and rr < 0.15:
        penalty *= 0.30
        reasons.append(f"inactive {days_inactive}d + response rate {rr:.0%}")

    # 5. Location mismatch
    country  = _norm(profile.get("country", ""))
    relocate = sig.get("willing_to_relocate", False)
    if country not in ["india"] and not relocate:
        penalty *= 0.70

    # 6. Honeypot detection
    honeypot_flags = sum([
        sig.get("profile_completeness_score", 0) == 100.0,
        sig.get("recruiter_response_rate", 0) == 1.0,
        sig.get("interview_completion_rate", 0) == 1.0,
        sig.get("offer_acceptance_rate", -1) == 1.0,
        sig.get("github_activity_score", -1) == 100.0,
    ])
    if honeypot_flags >= 4:
        penalty *= 0.40
        reasons.append("honeypot: impossibly perfect signals")

    return penalty, "; ".join(reasons)


# ── REASONING GENERATOR ───────────────────────────────────────────────────────

def build_reasoning(candidate: dict, components: dict, disq_reason: str, domain_label: str) -> str:
    """Generate 1–2 sentence reasoning for the submission CSV."""
    profile = candidate["profile"]
    sig     = candidate["redrob_signals"]

    title  = profile.get("current_title", "Unknown")
    yoe    = profile.get("years_of_experience", 0)
    rr     = sig.get("recruiter_response_rate", 0)
    gh     = sig.get("github_activity_score", -1)
    notice = sig.get("notice_period_days", 90)

    positives: list[str] = []
    if components.get("career", 0) > 0.50:
        positives.append(f"strong {domain_label} trajectory")
    if components.get("skill_hits", 0) >= 4:
        positives.append(f"{components['skill_hits']} core {domain_label} skills verified")
    elif components.get("skill_hits", 0) > 0:
        positives.append(f"{components['skill_hits']} core skills matched")
    if rr >= 0.60:
        positives.append(f"responsive ({rr:.0%})")
    if gh > 30:
        positives.append(f"active GitHub ({gh:.0f}/100)")
    if notice <= 30:
        positives.append(f"{notice}d notice period")

    pos_str = "; ".join(positives) if positives else "partial skill match"

    if disq_reason:
        return f"[{domain_label}] {title}, {yoe:.1f}yr — {pos_str}. ⚠️ {disq_reason[:90]}."
    return f"[{domain_label}] {title}, {yoe:.1f}yr — {pos_str}."


# ── MAIN PIPELINE ─────────────────────────────────────────────────────────────

def score_candidate(candidate: dict, domain_id: str | None = None) -> dict:
    """
    Full HUMAN-POTENTIAL-GRAPH scoring pipeline.

    Args:
        candidate  — parsed candidate dict
        domain_id  — optional: force scoring against a specific domain
                     (key from ranker.domains.DOMAINS). If None, the
                     candidate's best-fit domain is auto-detected.

    Returns a dict with candidate_id, score (0–1), reasoning, domain,
    and component breakdown.
    """
    if domain_id and domain_id in DOMAINS:
        detected_domain = domain_id
        domain_prof = DOMAINS[domain_id]
    else:
        detected_domain, domain_prof, _ = detect_domain(candidate)

    skill_score, skill_hits    = score_skills(candidate, domain_prof)
    career_score, career_ev    = score_career(candidate, domain_prof)
    exp_score                  = score_experience(candidate)
    behav_score, behav_ev      = score_behavioral(candidate)
    edu_score                  = score_education(candidate)
    disq_penalty, disq_reason  = compute_disqualifier(candidate, domain_prof)

    raw = (
        skill_score  * WEIGHTS["skill"]      +
        career_score * WEIGHTS["career"]     +
        exp_score    * WEIGHTS["experience"] +
        behav_score  * WEIGHTS["behavioral"] +
        edu_score    * WEIGHTS["education"]
    )

    final = max(0.0, min(raw * disq_penalty, 1.0))

    components = {
        "skill":      round(skill_score,  3),
        "career":     round(career_score, 3),
        "experience": round(exp_score,    3),
        "behavioral": round(behav_score,  3),
        "education":  round(edu_score,    3),
        "disq":       round(disq_penalty, 3),
        "skill_hits": len(skill_hits),
    }

    return {
        "candidate_id": candidate["candidate_id"],
        "score":        round(final, 6),
        "reasoning":    build_reasoning(candidate, components, disq_reason, domain_prof["label"]),
        "components":   components,
        "career_ev":    career_ev,
        "behav_ev":     behav_ev,
        "disq_reason":  disq_reason,
        "domain":       detected_domain,
        "domain_label": domain_prof["label"],
        "profile_summary": {
            "title":     candidate["profile"].get("current_title", ""),
            "yoe":       candidate["profile"].get("years_of_experience", 0),
            "location":  candidate["profile"].get("location", ""),
            "country":   candidate["profile"].get("country", ""),
            "headline":  candidate["profile"].get("headline", ""),
            "company":   candidate["profile"].get("current_company", ""),
            "industry":  candidate["profile"].get("current_industry", ""),
        },
    }
