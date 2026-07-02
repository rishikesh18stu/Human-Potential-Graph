# 🧠 HUMAN-POTENTIAL-GRAPH
### Redrob Intelligent Candidate Discovery & Ranking Challenge

> *"Not what they've done — what they can do and what they'll become."*

A multi-signal AI ranking engine that reasons about **career trajectory**, **production ML evidence**, and **behavioral availability** — not keywords. Built for the Redrob hackathon as a web application with a full scoring API.

---

## The Problem With Every Other Ranker

| What they do | What we do |
|---|---|
| Count AI keywords in the skill list | Read career *descriptions* for 25 production-ML signal phrases |
| Match job title to "ML Engineer" | Detect keyword stuffers: Marketing Managers with AI skill lists |
| Ignore behavioral signals | 15% weight on recency, response rate, GitHub activity, notice period |
| Static skill matching | Proficiency × duration × platform-assessment × endorsements |
| Miss the traps | Detect consulting-only careers, wrong domains, inactive candidates, honeypots |

The Redrob JD says explicitly: *"The right answer involves reasoning about the gap between what the JD says and what the JD means."* This ranker does exactly that.

---

## Architecture: NEXUS 6-Layer Scoring Pipeline

```
Score = (skill×0.30 + career×0.40 + experience×0.10 + behavioral×0.15 + education×0.05)
        × disqualifier_penalty
```

```
L0  SIGNAL INGESTION
    ├── profile (title, headline, summary, location, YoE)
    ├── career_history (up to 10 roles with descriptions)
    ├── skills (name + proficiency + duration + endorsements)
    ├── redrob_signals (23 behavioral signals)
    └── education (institution tier + degree + field)

L1  SKILL MATCH  ·  30%
    ├── Core required skills × 2.5 weight (embeddings, vector DBs, retrieval, NLP, Python)
    ├── Bonus skills × 1.0 weight (LoRA, LTR, MLOps, etc.)
    ├── Weight = proficiency_mult × (0.7 + 0.3 × duration_ratio) × assessment_mult
    └── Implicit evidence scan: career text mined for unlisted skill terms

L2  CAREER TRAJECTORY  ·  40%  ← most important signal
    ├── Product-company vs consulting ratio (penalty for pure consulting)
    ├── 25 semantic production-ML phrase detectors in role descriptions
    │     "ranking pipeline", "vector index", "ndcg", "hybrid retrieval" …
    ├── Title-velocity: is the career trending toward AI/ML?
    ├── Current-role relevance
    └── Company-size startup/scale-up bonus

L3  EXPERIENCE FIT  ·  10%
    └── 5–9yr → 1.0 | 4–5yr → 0.85 | 9–11yr → 0.80 | 3–4yr → 0.65 | <3yr → 0.20

L4  BEHAVIORAL AVAILABILITY  ·  15%
    ├── Recency          (last_active_date)         0.25
    ├── Open to work     (boolean flag)              0.15
    ├── Response rate    (recruiter_response_rate)   0.20
    ├── Response time    (avg_response_time_hours)   0.10
    ├── GitHub activity  (github_activity_score)     0.10
    ├── Interview rate   (interview_completion_rate) 0.08
    ├── Notice period    (≤30d preferred)            0.07
    └── Location         (India/preferred cities)   0.05

L5  DISQUALIFIER DETECTION  ·  ×penalty
    ├── Keyword stuffer     (non-technical title + ML skills, no AI career) → ×0.20
    ├── Pure consulting     (entire career at TCS/Infosys/Wipro etc.)       → ×0.35
    ├── Wrong domain        (CV/Speech/Robotics, no NLP/IR evidence)        → ×0.25
    ├── Unreachable         (inactive >12mo + response rate <15%)           → ×0.30
    ├── Location mismatch   (outside India, not willing to relocate)        → ×0.70
    └── Honeypot            (impossibly perfect signal combination)         → ×0.40
```

---

## Multi-Domain Ranking

The original ranker only understood one job profile: **Senior AI Engineer**.
Every candidate — including excellent backend engineers, frontend developers,
data analysts, and product managers — was scored against embeddings/vector-DB
criteria they were never expected to have, and came out looking like bad fits.

**HUMAN-POTENTIAL-GRAPH now ranks across 8 hiring domains**, each with its own
skill dictionary, career-phrase vocabulary, and disqualifier rules:

| Domain | Core signals it looks for |
|---|---|
| **AI / ML Engineer** | embeddings, vector DBs, retrieval/ranking, NDCG/MRR |
| **Software Engineer** (Backend/Full-Stack) | REST/gRPC, system design, distributed systems, SQL |
| **Data Engineer** | Spark, Airflow, ETL/ELT, data warehousing, streaming |
| **DevOps / Cloud / SRE** | Kubernetes, Terraform, CI/CD, observability, incident response |
| **Frontend Engineer** | React/Vue/Angular, web performance, accessibility, design systems |
| **Data Analyst / BI** | SQL, Tableau/Power BI, dashboards, A/B analysis |
| **Product Manager** | roadmaps, stakeholder management, GTM, product analytics |
| **QA / Test Engineer (SDET)** | test automation, Selenium/Cypress/Playwright, CI integration |

### How domain detection works

For each candidate, the ranker scores title keywords, skill overlap, and
career-phrase overlap against **every** domain, then classifies the candidate
into their strongest match:

```python
from ranker.scorer import detect_domain

domain_id, domain_profile, all_scores = detect_domain(candidate)
# domain_id → "software_engineer"
# domain_profile["label"] → "Software Engineer (Backend / Full-Stack)"
```

The candidate is then scored (skills, career trajectory, disqualifiers — L1,
L2, L5) entirely against **that domain's own rubric**. A Java backend
engineer is no longer penalized for not knowing FAISS; a Product Manager is
no longer penalized for not knowing PyTorch.

### Two ranking modes

**Auto-detect (default)** — ranks across all 8 domains simultaneously. Best
for an open candidate pool where you don't know in advance what roles you're
hiring for.

```bash
python app.py rank candidates.jsonl submission.csv
```

**Domain-locked** — force every candidate to be scored against one domain's
rubric only. Best when you're hiring for a specific, known role.

```python
from ranker.scorer import score_candidate
result = score_candidate(candidate, domain_id="frontend_engineer")
```

In the web UI, the **Upload & Rank** tab has a domain selector — leave it on
"Auto-detect" to rank across all domains, or pick one to lock the ranking to
a single role. The **Results** tab shows a domain badge per candidate, a
domain filter dropdown, and a domain-distribution summary across the full
pool.

### Adding a new domain

Domains live in `ranker/domains.py` as plain dictionaries — no code changes
needed elsewhere:

```python
DOMAINS["mobile_engineer"] = {
    "label": "Mobile Engineer (iOS/Android)",
    "core_skills": {"swift", "kotlin", "react native", "flutter", ...},
    "bonus_skills": {"fastlane", "firebase", "app store", ...},
    "career_phrases": ["shipped to app store", "reduced crash rate", ...],
    "title_keywords": ["ios engineer", "android engineer", "mobile developer"],
    "wrong_domain_skills": {"kubernetes", "terraform"},
    "disqualified_titles": {"hr manager", "sales executive"},
}
```

The scorer and web UI both read from this dict automatically.

---

## Quickstart

### Option A — Web Application (recommended)

```bash
git clone https://github.com/YOUR_USERNAME/human-potential-graph
cd human-potential-graph

pip install -r requirements.txt

python app.py
# → http://localhost:5000
```

Upload `candidates.jsonl` in the UI, watch the progress bar, explore ranked results with score breakdowns, download `submission.csv`.

### Option B — CLI (headless ranking)

```bash
# Rank full 100K pool → submission.csv
python app.py rank candidates.jsonl submission.csv

# Validate format before submitting
python validate_submission.py submission.csv
```

### Option C — Docker

```bash
docker build -t hpg-ranker .
docker run -p 7860:7860 hpg-ranker
# → http://localhost:7860
```

---

## Project Structure

```
human-potential-graph/
├── app.py                      # Flask API + CLI entry point
├── ranker/
│   ├── __init__.py
│   ├── scorer.py               # Full 6-layer scoring pipeline (domain-aware)
│   ├── domains.py              # 8 hiring domain profiles + auto-detection
│   └── signals.py              # Domain-independent signal dictionaries
├── templates/
│   └── index.html              # React single-page web app
├── sample_candidates.json      # 50-candidate demo dataset
├── sample_submission.csv       # Pre-computed example output
├── requirements.txt
├── Dockerfile
└── .github/workflows/ci.yml    # GitHub Actions CI
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/`      | Web UI |
| `GET`  | `/api/health` | Health check |
| `GET`  | `/api/domains` | List all 8 hiring domains (for the domain selector) |
| `POST` | `/api/rank` | Upload JSONL → rank → job_id. Optional form field `domain` locks scoring to one domain; omit for auto-detect across all domains |
| `POST` | `/api/rank-sample` | Rank bundled sample (demo). Same optional `domain` field |
| `GET`  | `/api/job/<job_id>` | Poll job status + results + domain_counts |
| `GET`  | `/api/download/<job_id>` | Download submission.csv (includes a `domain` column) |

**Rank request (auto-detect across all domains):**
```bash
curl -X POST http://localhost:5000/api/rank \
  -F "file=@candidates.jsonl" | jq .
# → {"job_id": "abc12345", "total": 100000, "domain": null}
```

**Rank request (locked to one domain):**
```bash
curl -X POST http://localhost:5000/api/rank \
  -F "file=@candidates.jsonl" \
  -F "domain=frontend_engineer" | jq .
# → {"job_id": "abc12345", "total": 100000, "domain": "frontend_engineer"}
```

curl http://localhost:5000/api/job/abc12345 | jq .results[0]
```

---

## What the Top-Ranked Candidates Look Like

```
Rank  1  CAND_0018499  0.9724  Senior ML Engineer @ Zomato (Noida)
         Built RAG-based ranking pipeline serving 50M+ queries/month
         BGE embeddings + FAISS HNSW + BM25 + LLM reranker + NDCG evaluation
         GitHub: 94/100 · Response rate: 61% · Notice: 15 days · Open to work ✓

Rank  2  CAND_0002025  0.9723  Senior AI Engineer · 5.9yr
         100% product-AI career trajectory · 8 core skills verified · responsive

Rank  3  CAND_0046064  0.9697  Senior NLP Engineer · 8.9yr
         Production retrieval + ranking + evaluation framework evidence
```

---

## Trap Detection Examples

```
CAND_XXXXXX  Score: 0.06  ← was superficially "9 AI skills"
  Title: Marketing Manager  Skills: PyTorch, FAISS, LoRA, Pinecone … (keyword stuffer)
  Penalty: ×0.20 — non-technical title + ML skills + zero AI career history

CAND_XXXXXX  Score: 0.11  ← "Operations Manager, 13yr experience"
  Entire career: IT Services consulting firms
  Penalty: ×0.35 — pure consulting background

CAND_XXXXXX  Score: 0.09  ← "perfect signals"
  profile_completeness=100, recruiter_response_rate=1.0, github=100, offer_acceptance=1.0
  Penalty: ×0.40 — honeypot: 4+ impossibly perfect signals
```

---

## Scoring Methodology

### Why career trajectory is 40%

The JD says: *"If your 'AI experience' consists primarily of recent (under 12 months) projects using LangChain to call OpenAI — we will probably not move forward."* Keyword matching cannot detect this. Career description analysis can.

### Why behavioral signals are 15%

The JD says: *"A perfect-on-paper candidate who hasn't logged in for 6 months and has a 5% recruiter response rate is, for hiring purposes, not actually available."*

### Why we don't use embeddings

The evaluation runs CPU-only, no network, under 5 minutes for 100K candidates. Pure Python with no heavy models fits those constraints while delivering better signal than naive vector similarity.

---

## Compute Environment

| Property | Value |
|---|---|
| Runtime | Python 3.11, pure stdlib + Flask only |
| Memory | ~500 MB peak for 100K candidates |
| Time | ~3–4 minutes for 100K candidates on CPU |
| GPU | Not required |
| Network | Not required during ranking |

---

## AI Tools Declaration

- Claude (architecture discussion, code review, prompt design)
- All candidate data processed locally — no data sent to any LLM during ranking

---

## Team

**NEXUS** — built for the Redrob Intelligent Candidate Discovery & Ranking Challenge

> *"LinkedIn shows what you've done. HUMAN-POTENTIAL-GRAPH shows what you'll become."*
