# HUMAN-POTENTIAL-GRAPH — Complete Getting Started Guide

## Prerequisites

- **Python 3.9+** (3.11 recommended)
- **pip** (Python package manager)
- **Git** (optional, for cloning)
- **curl** (optional, for API testing)

---

## Installation & Setup

### Step 1: Get the Code

#### Option A — Download the ZIP (recommended for first time)
```bash
# Download human-potential-graph.zip from the outputs folder
# Extract it:
unzip human-potential-graph.zip
cd human-potential-graph
```

#### Option B — Clone from GitHub (if you've pushed it)
```bash
git clone https://github.com/rishikesh18stu/human-potential-graph.git
cd human-potential-graph
```

### Step 2: Create Virtual Environment (optional but recommended)
```bash
# On macOS / Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
# This only installs Flask (the only external dependency)
```

---

## Run It — Three Options

### Option 1: Web Application (EASIEST — recommended for first test)

```bash
python app.py
```

**Output:**
```
[HPG] Starting server on http://0.0.0.0:5000
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
```

**Then:**
1. Open browser → `http://localhost:5000`
2. Click **"Try Sample (50 candidates)"** (no upload needed)
3. Watch the progress bar
4. Explore the results table → click any candidate to see full score breakdown
5. Download `submission.csv`

**To rank your own data:**
1. Click **"Upload Candidate Pool"**
2. Drag-drop your `candidates.jsonl` file (or click to browse)
3. Click **"Rank Candidates"**
4. Progress bar updates live as candidates are scored
5. Results table appears automatically when done
6. Click **"Download submission.csv"**

---

### Option 2: Command-Line Interface (for batch/automation)

**Rank a full dataset without web UI:**
```bash
python app.py rank candidates.jsonl submission.csv
```

**Output:**
```
[HPG] Reading candidates.jsonl ...
[HPG] 100000 candidates found. Scoring ...
[HPG] Done. Top-100 written to submission.csv

Top 10:
    1. CAND_0018499  0.9724  Senior ML Engineer
    2. CAND_0002025  0.9723  Senior AI Engineer
    3. CAND_0046064  0.9697  Senior NLP Engineer
   ...
```

**Validate the submission format before uploading to the challenge:**
```bash
python validate_submission.py submission.csv
```

**Output:**
```
Submission is valid.
```

---

### Option 3: Docker Container (for reproducible environments / cloud deployment)

**Build the image:**
```bash
docker build -t hpg-ranker .
```

**Run the container:**
```bash
docker run -p 7860:7860 hpg-ranker
```

**Then open:**
```
http://localhost:7860
```

**Or run batch ranking in container:**
```bash
docker run -v /path/to/candidates.jsonl:/data/candidates.jsonl \
           -v /path/to/outputs:/data/outputs \
           hpg-ranker \
           python app.py rank /data/candidates.jsonl /data/outputs/submission.csv
```

---

## Directory Structure & Key Files

```
human-potential-graph/
│
├── app.py                          ← Main entry point (Flask server OR CLI)
├── requirements.txt                ← Dependencies (just Flask)
├── README.md                       ← Full project documentation
├── Dockerfile                      ← Container setup
│
├── ranker/                         ← Core ranking engine
│   ├── __init__.py
│   ├── scorer.py                  ← 6-layer NEXUS scoring pipeline (1100 lines)
│   │   ├── score_skills()         → L1: Skill matching (30% weight)
│   │   ├── score_career()         → L2: Career trajectory (40% weight)
│   │   ├── score_experience()     → L3: Experience fit (10% weight)
│   │   ├── score_behavioral()     → L4: Availability signals (15% weight)
│   │   ├── score_education()      → L5: Education signal (5% weight)
│   │   ├── compute_disqualifier() → Trap detection (×penalty)
│   │   └── score_candidate()      → Full pipeline orchestration
│   │
│   └── signals.py                 ← Signal dictionaries (400 lines)
│       ├── CORE_REQUIRED          → 40+ embeddings/vector DB/retrieval skills
│       ├── BONUS_SKILLS           → 30+ MLOps/eval/LLM skills
│       ├── CAREER_POSITIVE_PHRASES→ 25 production-ML signal phrases
│       ├── CONSULTING_GIANTS      → 15 consulting firm names (disqualifier)
│       ├── WRONG_DOMAIN_SKILLS    → CV/Speech/Robotics (disqualifier)
│       ├── DISQUALIFIED_TITLES    → Non-fit role titles
│       ├── PREFERRED_LOCATIONS    → India + key cities
│       └── Score multipliers      → Proficiency, tier, degree

├── templates/
│   └── index.html                 ← React single-page app
│       ├── Tab 1: Upload & Rank   → Drag-drop JSONL, progress bar
│       ├── Tab 2: Results         → Table + score breakdown
│       └── Tab 3: Architecture    → NEXUS pipeline diagram

├── sample_candidates.json         ← 50-candidate demo (for "Try Sample")
├── sample_submission.csv          ← Example top-100 output
│
└── .github/workflows/ci.yml       ← GitHub Actions (auto-test on push)
```

---

## Typical Workflow

### Workflow A: Test with Sample Data (5 minutes)
```bash
# 1. No setup needed — just run:
python app.py

# 2. Browser: http://localhost:5000
#    Click: "Try Sample (50 candidates)"
#    Wait: ~5 seconds
#    Done: Top-50 ranked, download CSV

# 3. Exit: Ctrl+C in terminal
```

### Workflow B: Rank Your Own Dataset (10-300 minutes depending on file size)
```bash
# 1. Start server:
python app.py

# 2. Browser: http://localhost:5000
#    Drag-drop: your candidates.jsonl
#    Click: "Rank Candidates"
#    Watch: Live progress bar (e.g., "12,543 / 100,000 — 12.5%")
#    When done: Results table auto-appears

# 3. Explore results:
#    - Scroll table, sort by score
#    - Click row to expand score breakdown
#    - Red 🚫 badge = trap detected (see reason)
#    - Green ✓ badge = OK

# 4. Download:
#    Click: "Download submission.csv"
#    File: submission.csv arrives with top-100 ranked

# 5. Validate (before submitting to challenge):
python validate_submission.py submission.csv
# Output: "Submission is valid."
```

### Workflow C: Headless CLI (for automation / scripts)
```bash
# 1. Rank in background (no browser):
python app.py rank candidates.jsonl submission.csv

# 2. Validate:
python validate_submission.py submission.csv

# 3. Parse results programmatically:
python -c "
import csv
with open('submission.csv') as f:
    for row in csv.DictReader(f):
        print(f\"{row['rank']:3d} | {row['candidate_id']} | {row['score']}\")
"
```

### Workflow D: Deploy to HuggingFace Spaces
```bash
# 1. Create new Space on huggingface.co (HuggingFace account required)
#    Owner: your-username
#    Space name: human-potential-graph
#    License: OpenRAIL
#    Space SDK: Docker

# 2. Push code:
git init
git add .
git commit -m "Initial commit"
git remote add space https://huggingface.co/spaces/your-username/human-potential-graph
git push -u space main

# 3. HuggingFace auto-deploys from Dockerfile
#    → Space URL: https://huggingface.co/spaces/your-username/human-potential-graph
#    → Public, no credits required (300 seconds timeout OK for demo)
```

---

## API Testing (Advanced)

### Test the Upload Endpoint
```bash
# Rank a file via API:
curl -X POST http://localhost:5000/api/rank \
  -F "file=@candidates.jsonl"

# Response:
# {"job_id": "abc12345", "total": 100000}

# Poll the job:
curl http://localhost:5000/api/job/abc12345 | jq '.status'
# "running" → wait → "done"

# Download results:
curl http://localhost:5000/api/download/abc12345 > submission.csv
```

### Test the Demo Endpoint
```bash
# Rank sample (no file upload):
curl -X POST http://localhost:5000/api/rank-sample

# Response:
# {"job_id": "xyz78901", "total": 50}

curl http://localhost:5000/api/job/xyz78901 | jq '.results[0]'
# Returns first candidate's full score breakdown
```

### Health Check
```bash
curl http://localhost:5000/api/health
# {"status": "ok", "system": "HUMAN-POTENTIAL-GRAPH"}
```

---

## Troubleshooting

### Issue: "No module named 'flask'"
```bash
pip install flask
# OR if using virtual env, make sure it's activated:
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Issue: "Port 5000 already in use"
```bash
# Use a different port:
python app.py --port 8000
# Browser: http://localhost:8000

# OR kill the process on 5000:
lsof -ti:5000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :5000   # Windows (then taskkill /PID xxx)
```

### Issue: "candidates.jsonl: No such file"
```bash
# Make sure file is in the right directory:
ls candidates.jsonl

# OR specify full path:
python app.py rank /path/to/candidates.jsonl /path/to/submission.csv
```

### Issue: "submission.csv is invalid"
```bash
# Check format:
python validate_submission.py submission.csv

# Expected output:
# Submission is valid.

# If error, file may be corrupted — re-run ranking:
python app.py rank candidates.jsonl submission.csv
```

### Issue: "Web UI loads but upload doesn't work"
```bash
# Check browser console (F12) for errors
# If 413 error: file too large (600MB limit)
# If 500 error: check terminal output

# Try sample first (no file):
# Browser → "Try Sample (50 candidates)"
```

### Issue: Slow ranking on large files
```bash
# Expected times on CPU (single-core Python):
# - 1K candidates: ~6 seconds
# - 10K candidates: ~60 seconds
# - 100K candidates: ~4-6 minutes

# To speed up: use PyPy or Cython (out of scope for this project)
# Project is designed for CPU-only, no GPU needed
```

---

## Input File Format

**File name:** `candidates.jsonl` or `candidates.json`

**Format:** One JSON object per line (JSONL), each candidate with this structure:

```json
{
  "candidate_id": "CAND_0000001",
  "profile": {
    "current_title": "Senior ML Engineer",
    "current_company": "Zomato",
    "current_industry": "Food Delivery",
    "current_company_size": "10001+",
    "headline": "Building ranking systems @ scale",
    "summary": "...",
    "years_of_experience": 7.2,
    "location": "Noida",
    "country": "India"
  },
  "career_history": [
    {
      "company": "Zomato",
      "title": "Senior ML Engineer",
      "industry": "Food Delivery",
      "duration_months": 24,
      "company_size": "10001+",
      "description": "Built NDCG-optimized ranking pipeline serving 50M+ daily searches using BGE embeddings + FAISS index + BM25 hybrid retrieval + LLM reranker..."
    }
  ],
  "skills": [
    {
      "name": "Weaviate",
      "proficiency": "expert",
      "duration_months": 24,
      "endorsements": 12
    }
  ],
  "education": [
    {
      "degree": "B.Tech",
      "field_of_study": "Computer Science",
      "tier": "tier_1"
    }
  ],
  "certifications": [...],
  "languages": [...],
  "redrob_signals": {
    "recruiter_response_rate": 0.61,
    "last_active_date": "2026-06-15",
    "github_activity_score": 94,
    "open_to_work_flag": true,
    "notice_period_days": 15,
    "avg_response_time_hours": 2.5,
    "interview_completion_rate": 0.75,
    "willing_to_relocate": false,
    "profile_completeness_score": 92,
    ...
  }
}
```

---

## Output Format

**File:** `submission.csv`

```csv
candidate_id,rank,score,reasoning
CAND_0018499,1,0.9724,Senior ML Engineer, 7.2yr — strong production AI/ML trajectory; 6 core AI skills verified; responsive (61%); active GitHub (94/100); short notice period (15d).
CAND_0002025,2,0.9723,Senior AI Engineer, 5.9yr — 100% product-AI career trajectory; 8 core skills verified; response rate 68%.
CAND_0046064,3,0.9697,Senior NLP Engineer, 8.9yr — 9 production ML signals in descriptions; strong behavioral availability. Note: Current role not explicitly AI-focused; recommend brief screen call.
...
```

**Columns:**
- `candidate_id` — unique candidate identifier
- `rank` — 1–100 (top-100 only)
- `score` — 0.0–1.0 (4 decimal places)
- `reasoning` — 1–2 sentence summary of why ranked at this position + any trap flags

---

## Success Criteria

✅ **Successfully run if:**
1. No errors in terminal
2. Web UI loads (or CSV generated)
3. Candidates ranked with scores between 0.0 and 1.0
4. Top-ranked candidates have high scores AND plausible career descriptions
5. submission.csv passes validation: `python validate_submission.py submission.csv`

✅ **High-quality ranking if:**
1. Top-10 candidates have >0.85 scores
2. Candidates with production-ML career descriptions rank in top-50
3. Pure consulting careers get low scores (<0.5)
4. Keyword stuffers (non-technical titles + AI skills) get flagged/down-weighted
5. Inactive candidates (>6 months) don't appear in top-100

---

## Next Steps

1. **Explore the code:**
   - `ranker/signals.py` — all the JD-derived knowledge (skills, phrases, disqualifiers)
   - `ranker/scorer.py` — the 6-layer pipeline logic
   - `templates/index.html` — React UI source

2. **Customize scoring:**
   - Edit weights in `signals.py` → `WEIGHTS = {...}`
   - Add/remove skill terms in `CORE_REQUIRED`, `BONUS_SKILLS`
   - Adjust disqualifier penalties in `scorer.py` → `compute_disqualifier()`

3. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial HUMAN-POTENTIAL-GRAPH commit"
   git remote add origin https://github.com/rishikesh18stu/human-potential-graph
   git push -u origin main
   ```

4. **Deploy to HuggingFace Spaces:**
   - Create space at huggingface.co
   - Choose Docker SDK
   - Push repo
   - Share link in submission_metadata.yaml

---

## Questions?

- **API issues?** Check `/api/health` endpoint
- **Ranking slow?** Check system resources, expected times in Troubleshooting above
- **Results look wrong?** Run on sample data first (`Try Sample` button)
- **Need modifications?** Edit `signals.py` (knowledge) or `scorer.py` (logic)

Good luck! 🚀
