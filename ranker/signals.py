"""
HUMAN-POTENTIAL-GRAPH — Shared Signal Dictionaries
Domain-agnostic knowledge used across every job domain.
Domain-specific skills/phrases/disqualifiers now live in ranker/domains.py.
"""

# ── WEIGHTS ────────────────────────────────────────────────────────────────────
# Score = skill(30%) + career(40%) + experience(10%) + behavioral(15%) + edu(5%)
# Then × disqualifier_penalty
WEIGHTS = {
    "skill":       0.30,
    "career":      0.40,
    "experience":  0.10,
    "behavioral":  0.15,
    "education":   0.05,
}

# ── PURE CONSULTING FIRMS (penalized as sole background, any domain) ──────────
CONSULTING_GIANTS = {
    "tcs", "tata consultancy", "infosys", "wipro", "accenture",
    "cognizant", "capgemini", "hcl", "tech mahindra", "mindtree",
    "mphasis", "hexaware", "ltimindtree", "l&t infotech",
    "ibm global services", "deloitte", "kpmg", "ey", "pwc",
    "genpact", "firstsource", "persistent systems", "birlasoft",
}

# ── POSITIVE LOCATION SIGNALS (India-first hiring, adjust as needed) ──────────
PREFERRED_LOCATIONS = {
    "india", "pune", "noida", "hyderabad", "mumbai",
    "delhi", "bangalore", "bengaluru", "ncr", "gurugram", "gurgaon",
}

# ── PROFICIENCY MULTIPLIERS ────────────────────────────────────────────────────
PROFICIENCY_MULT = {
    "beginner":     0.30,
    "intermediate": 0.60,
    "advanced":     0.85,
    "expert":       1.00,
}

# ── EDUCATION TIERS ────────────────────────────────────────────────────────────
TIER_SCORES = {
    "tier_1": 1.00,
    "tier_2": 0.75,
    "tier_3": 0.55,
    "tier_4": 0.40,
    "unknown": 0.45,
}

DEGREE_SCORES = {
    "ph.d": 0.95, "phd": 0.95, "doctorate": 0.95,
    "m.tech": 0.85, "m.e.": 0.85, "m.s.": 0.85, "ms": 0.85,
    "m.sc": 0.80, "mtech": 0.85, "me": 0.85,
    "b.tech": 0.70, "b.e.": 0.70, "be": 0.70, "btech": 0.70,
    "b.sc": 0.65, "b.s.": 0.65, "bsc": 0.65,
    "mba": 0.55,
    "b.com": 0.35, "bba": 0.35,
}

STEM_FIELDS = {
    "computer science", "cs", "artificial intelligence", "machine learning",
    "data science", "mathematics", "statistics", "information technology",
    "software engineering", "electrical engineering", "electronics",
    "computational", "math", "physics",
}
