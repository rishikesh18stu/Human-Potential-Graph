# 🚀 HUMAN-POTENTIAL-GRAPH — Setup & Run Guide

Complete step-by-step instructions for running the ranker locally, in Docker, or on HuggingFace Spaces.

---

## Table of Contents

1. [Quick Start (5 minutes)](#quick-start--5-minutes)
2. [Full Setup (10 minutes)](#full-setup--10-minutes)
3. [Running the Web App](#running-the-web-app)
4. [Running the CLI](#running-the-cli)
5. [Docker Deployment](#docker-deployment)
6. [HuggingFace Spaces](#huggingface-spaces)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start (5 minutes)

### 1. Clone the Repository

```bash
git clone https://github.com/rishikesh18stu/human-potential-graph
cd human-potential-graph
```

### 2. Install Dependencies (Python 3.9+)

```bash
pip install flask
# or: pip install -r requirements.txt
```

### 3. Run the Web App

```bash
python app.py
```

You'll see:
```
[HPG] Starting server on http://0.0.0.0:5000
 * Running on http://127.0.0.1:5000
```

Open **http://localhost:5000** in your browser. ✅ Done!

### 4. Upload & Rank

- **Tab 1 (Upload & Rank):** Drag-drop your `candidates.jsonl` file
- Watch progress bar in real time
- **Tab 2 (Results):** Automatically shows top-100 ranked candidates
- Download `submission.csv`

---

## Full Setup (10 minutes)

### On macOS / Linux

```bash
# Clone
git clone https://github.com/rishikesh18stu/human-potential-graph
cd human-potential-graph

# Create Python virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install flask

# Run the web app
python app.py
```

### On Windows (PowerShell)

```powershell
# Clone
git clone https://github.com/rishikesh18stu/human-potential-graph
cd human-potential-graph

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install flask

# Run
python app.py
```

---

## Running the Web App

### Start the Server

```bash
python app.py
```

Expected output:
```
[HPG] Starting server on http://0.0.0.0:5000
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
```

### Access the UI

Open **http://localhost:5000** in your browser (Chrome/Firefox/Safari).

### What You'll See

**Tab 1 — Upload & Rank:**
- Large drag-drop zone for `candidates.jsonl`
- "🔬 Try Sample" button (loads 50-candidate demo, no upload needed)
- Real-time progress bar while ranking

**Tab 2 — Results:**
- Filterable table of top-100 candidates
- Rank, candidate ID, score, component scores (mini bars)
- Trap detection badges
- Click any row for full detail panel (score breakdown, reasoning, signals)
- Download button for `submission.csv`

**Tab 3 — Architecture:**
- Full NEXUS 6-layer pipeline diagram
- Comparisons vs keyword matching, title matching, etc.

---

## Running the CLI

### Headless Ranking (No Web UI)

Perfect for server environments or batch processing.

```bash
python app.py rank <input_jsonl> <output_csv>
```

**Example:**

```bash
# Rank your full candidate pool
python app.py rank candidates.jsonl submission.csv

# Output:
# [HPG] Reading candidates.jsonl ...
# [HPG] 100000 candidates found. Scoring ...
# [HPG] Done. Top-100 written to submission.csv
#
# Top 10:
#   1. CAND_0018499  0.9724  Senior ML Engineer
#   2. CAND_0002025  0.9723  Senior AI Engineer
#   3. CAND_0046064  0.9697  Senior NLP Engineer
#   ...
```

### Validate the Output

```bash
python validate_submission.py submission.csv

# Output: Submission is valid. ✓
```

### Performance

- **100 candidates:** ~3 seconds
- **1,000 candidates:** ~30 seconds  
- **10,000 candidates:** ~4 minutes
- **100,000 candidates:** ~3-4 minutes (CPU)

**No GPU or network required.**

---

## Docker Deployment

### Build the Image

```bash
docker build -t hpg-ranker:latest .
```

### Run Locally

```bash
docker run -p 5000:5000 hpg-ranker:latest
```

Then access **http://localhost:5000**

### Run with Volume Mount (for candidates.jsonl)

```bash
docker run -p 5000:5000 \
  -v /path/to/your/data:/app/data \
  hpg-ranker:latest
```

Access upload UI or run CLI inside container:
```bash
docker run -v /path/to/candidates.jsonl:/app/input.jsonl \
           -v /path/to/output:/app/output \
           hpg-ranker:latest \
           python app.py rank /app/input.jsonl /app/output/submission.csv
```

### Docker Compose (optional)

```yaml
version: '3.8'
services:
  hpg:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    environment:
      - PORT=5000
```

```bash
docker-compose up --build
```

---

## HuggingFace Spaces

The `Dockerfile` makes deployment to HuggingFace Spaces trivial for the submission requirement.

### 1. Create a Space

- Go to **https://huggingface.co/spaces**
- Click **Create new Space**
- Choose **Docker** as the Space SDK
- Select any name (e.g., `human-potential-graph`)

### 2. Upload Files

Via git or web interface:
```
├── Dockerfile
├── app.py
├── ranker/
│   ├── __init__.py
│   ├── scorer.py
│   └── signals.py
├── templates/
│   └── index.html
├── requirements.txt
├── sample_candidates.json
└── README.md
```

### 3. Deploy

HuggingFace automatically builds and deploys when you push. Once live:
- **Sandbox link:** https://huggingface.co/spaces/YOUR_USERNAME/human-potential-graph
- Add this to your `submission_metadata.yaml`

### Health Check

HuggingFace will request `/api/health` periodically to ensure the space is running.

---

## Project Layout Explained

```
human-potential-graph/
├── app.py                    ← Entry point (web app or CLI)
│                              • GET  / → serves index.html
│                              • POST /api/rank → accepts upload, ranks
│                              • GET  /api/job/<id> → poll progress
│                              • main: runs Flask server or CLI
│
├── ranker/
│   ├── scorer.py             ← 6-layer NEXUS scoring pipeline
│   │                          • score_candidate(dict) → score (0-1)
│   │                          • All 5 component scorers
│   │                          • Disqualifier detection
│   │
│   └── signals.py            ← JD-derived signal dictionaries
│                              • CORE_REQUIRED (embeddings, vectors, retrieval)
│                              • BONUS_SKILLS (LoRA, QLora, MLOps, etc.)
│                              • CAREER_POSITIVE_PHRASES (25 production-ML terms)
│                              • CONSULTING_GIANTS, WRONG_DOMAIN_SKILLS, etc.
│
├── templates/
│   └── index.html            ← React SPA (no build step needed)
│                              • Tab 1: Upload & Rank
│                              • Tab 2: Results table + detail panel
│                              • Tab 3: Architecture diagram
│
├── requirements.txt          ← Just Flask (Flask only!)
├── Dockerfile                ← For HuggingFace Spaces / any container
└── README.md                 ← High-level overview
```

---

## File Format: candidates.jsonl

Each line must be a valid JSON object with this structure:

```json
{
  "candidate_id": "CAND_0000001",
  "profile": {
    "current_title": "Senior ML Engineer",
    "current_company": "Zomato",
    "current_industry": "Food Delivery",
    "current_company_size": "10001+",
    "location": "Noida",
    "country": "India",
    "years_of_experience": 7.2,
    "headline": "Building ML systems at scale",
    "summary": "5+ years ranking systems ..."
  },
  "career_history": [
    {
      "title": "Senior ML Engineer",
      "company": "Zomato",
      "industry": "Food Delivery",
      "duration_months": 24,
      "company_size": "10001+",
      "description": "Led retrieval and ranking team. Built FAISS vector index serving 50M queries/day. Implemented hybrid BM25+dense search. Evaluated with NDCG@10. Shipped to 50M+ users."
    }
  ],
  "skills": [
    {
      "name": "Faiss",
      "proficiency": "expert",
      "duration_months": 18,
      "endorsements": 45,
      "verified": true
    }
  ],
  "education": [
    {
      "institution": "IIT Bombay",
      "degree": "B.Tech",
      "field_of_study": "Computer Science",
      "tier": "tier_1"
    }
  ],
  "redrob_signals": {
    "recruiter_response_rate": 0.61,
    "last_active_date": "2026-06-15",
    "github_activity_score": 94,
    "open_to_work_flag": true,
    "notice_period_days": 15,
    "avg_response_time_hours": 3.5,
    "interview_completion_rate": 0.80,
    "profile_completeness_score": 85,
    "willing_to_relocate": true
  }
}
```

Each line = one candidate. No array wrapper.

---

## Output: submission.csv

The ranker produces a CSV with top-100 ranked candidates:

```csv
candidate_id,rank,score,reasoning
CAND_0018499,1,0.9724,"Senior ML Engineer, 7.2yr — strong production AI/ML trajectory; responsive (61%); GitHub score 94. ✓"
CAND_0002025,2,0.9723,"Senior AI Engineer, 5.9yr — 8 core skills matched; strong career evidence; high response rate."
CAND_0046064,3,0.9697,"Senior NLP Engineer, 8.9yr — production retrieval + ranking; evaluation framework; active GitHub."
...
```

The score is always `score (normalized 0.0–1.0)` = (skill×0.30 + career×0.40 + exp×0.10 + behav×0.15 + edu×0.05) × disq_penalty

---

## Common Tasks

### Test on Sample Data (No Upload)

```bash
# Web UI: click "🔬 Try Sample (50 candidates)" button

# CLI:
python -c "
import json, sys
sys.path.insert(0, '.')
from ranker.scorer import score_candidate

with open('sample_candidates.json') as f:
    cands = json.load(f)

results = sorted(
    [score_candidate(c) for c in cands],
    key=lambda x: (-x['score'], x['candidate_id'])
)

for i, r in enumerate(results[:5], 1):
    print(f\"{i}. {r['candidate_id']}  {r['score']:.4f}  {r['profile_summary']['title']}\")
"
```

### Run Tests

```bash
# GitHub Actions CI runs automatically on push
# To run locally:

python -c "
import json, sys
sys.path.insert(0, '.')
from ranker.scorer import score_candidate

# Load sample
with open('sample_candidates.json') as f:
    cands = json.load(f)

# Score all
results = [score_candidate(c) for c in cands]

# Verify
assert len(results) == len(cands), 'Missing scores'
assert all(0 <= r['score'] <= 1 for r in results), 'Scores out of range'
assert all('candidate_id' in r for r in results), 'Missing IDs'

print(f'✓ All {len(results)} candidates scored correctly')
print(f'✓ Score range: [{min(r[\"score\"] for r in results):.4f}, {max(r[\"score\"] for r in results):.4f}]')
"
```

### Monitor Performance

```bash
# Time a full run
time python app.py rank candidates.jsonl /tmp/out.csv

# Expected: ~3–4 minutes for 100K candidates

# Monitor memory
# macOS:
command time -l python app.py rank candidates.jsonl /tmp/out.csv

# Linux:
/usr/bin/time -v python app.py rank candidates.jsonl /tmp/out.csv
```

### Debug a Specific Candidate

```bash
python -c "
import json, sys
sys.path.insert(0, '.')
from ranker.scorer import score_candidate

with open('candidates.jsonl') as f:
    for line in f:
        c = json.loads(line)
        if c['candidate_id'] == 'CAND_0018499':
            result = score_candidate(c)
            print(f\"Score: {result['score']:.4f}\")
            print(f\"Components: {result['components']}\")
            print(f\"Reasoning: {result['reasoning']}\")
            print(f\"Career evidence: {result['career_ev']}\")
            print(f\"Behavioral: {result['behav_ev']}\")
            print(f\"Disqualifier: {result['disq_reason']}\")
            break
"
```

---

## Troubleshooting

### Port Already in Use

```bash
# Change port
PORT=8080 python app.py

# Or kill the process
lsof -ti:5000 | xargs kill -9
```

### Import Errors

```
ModuleNotFoundError: No module named 'flask'
```

Solution:
```bash
pip install flask
# or
pip install -r requirements.txt
```

### File Not Found: candidates.jsonl

```
Error: No file uploaded. POST a JSONL file as 'file'.
```

Solution: Use the web UI, or provide full path:
```bash
python app.py rank /full/path/to/candidates.jsonl output.csv
```

### Validation Errors

```
Submission is invalid: tie-break requires candidate_id ascending
```

Solution: The ranker already handles this. If you manually edited the CSV, re-sort:
```bash
python -c "
import csv
rows = list(csv.DictReader(open('submission.csv')))
rows.sort(key=lambda x: (-float(x['score']), x['candidate_id']))
with open('submission.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['candidate_id','rank','score','reasoning'])
    w.writeheader()
    for i, r in enumerate(rows, 1):
        r['rank'] = i
        w.writerow(r)
"
python validate_submission.py submission.csv
```

### Out of Memory

For 100K+ candidates, you need ~500MB RAM. If you hit OOM:

```bash
# Stream processing (not yet implemented, but can be added):
# Currently the ranker loads all results in memory before sorting
# For very large pools, chunking / external sorting would help

# Workaround: rank in smaller batches
split -l 10000 candidates.jsonl batch_
for f in batch_*; do
  python app.py rank "$f" "out_${f}.csv"
done
# Then manually merge top-100s
```

### Docker Build Fails

```
ERROR: failed to solve with frontend dockerfile.v0
```

Solution:
```bash
# Ensure Docker is running
docker ps

# Rebuild
docker build --no-cache -t hpg-ranker:latest .
```

### HuggingFace Space Won't Start

- Check **Logs** tab in Space settings
- Ensure `requirements.txt` has `flask>=3.0.0`
- Verify `Dockerfile` EXPOSE port matches your app

---

## Getting Help

### Check Logs

**Local:**
```bash
python app.py 2>&1 | tee app.log
```

**Docker:**
```bash
docker logs <container_id>
```

**HuggingFace Spaces:**
- Go to **Logs** in the Space settings

### Debug Mode

```bash
# Enable Flask debug (NOT for production)
FLASK_ENV=development python app.py
```

### Test API Directly

```bash
# Health check
curl http://localhost:5000/api/health

# Rank sample
curl -X POST http://localhost:5000/api/rank-sample \
  | jq .job_id
# → abc12345

# Poll results
curl http://localhost:5000/api/job/abc12345 \
  | jq '.results[0]'

# Download
curl http://localhost:5000/api/download/abc12345 \
  > submission.csv
```

---

## Next Steps

1. ✅ Run locally on your machine
2. 📤 Push to GitHub (`git push`)
3. 🚀 Deploy to HuggingFace Spaces
4. 📊 Add `sandbox_link` to `submission_metadata.yaml`
5. 🎯 Submit to Redrob challenge

---

**Questions?** Check the main [README.md](README.md) for architecture details or open an issue on GitHub.
