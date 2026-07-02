"""
HUMAN-POTENTIAL-GRAPH — Flask API Server
========================================
Endpoints:
  GET  /                  → serves the web UI
  GET  /api/health        → health check
  POST /api/rank          → rank uploaded JSONL; streams progress via SSE
  POST /api/rank-sample   → rank sample candidates (demo mode, no upload needed)
  GET  /api/download/<id> → download generated submission CSV
"""

import csv
import io
import json
import os
import time
import uuid
from pathlib import Path

from flask import (
    Flask, Response, jsonify,
    request, send_file, stream_with_context,
)

from ranker.scorer import score_candidate
from ranker.domains import DOMAIN_CHOICES

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 600 * 1024 * 1024   # 600 MB upload limit

# In-memory job store  { job_id: {"status", "results", "csv_path", "total", "done"} }
JOBS: dict[str, dict] = {}

SAMPLE_PATH = Path(__file__).parent / "sample_candidates.json"
OUTPUT_DIR  = Path("/tmp/hpg_outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def _rank_stream(candidates_iter, job_id: str, total_hint: int, domain_id: str | None = None):
    """
    Score all candidates, update JOBS[job_id], write CSV, no return value.

    domain_id:
        None            → auto-detect each candidate's best-fit domain (default,
                           ranks across ALL domains — AI/ML, Backend, Frontend,
                           Data, DevOps, Product, QA, etc.)
        "<domain_key>"  → force every candidate to be scored against ONE domain's
                           rubric (useful when hiring for a specific role only)
    """
    job = JOBS[job_id]
    job["status"] = "running"
    job["total"]  = total_hint
    job["done"]   = 0

    all_results = []
    for cand in candidates_iter:
        try:
            result = score_candidate(cand, domain_id=domain_id)
            all_results.append(result)
        except Exception:
            pass
        job["done"] += 1

    # Sort: score descending, tie-break candidate_id ascending
    all_results.sort(key=lambda x: (-x["score"], x["candidate_id"]))

    top100 = all_results[:100]

    # Write submission CSV
    csv_path = OUTPUT_DIR / f"{job_id}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "domain", "reasoning"])
        for rank, row in enumerate(top100, 1):
            writer.writerow([row["candidate_id"], rank,
                             f"{row['score']:.4f}", row["domain_label"], row["reasoning"]])

    job["status"]   = "done"
    job["csv_path"] = str(csv_path)
    job["domain_counts"] = {}
    for r in all_results:
        job["domain_counts"][r["domain_label"]] = job["domain_counts"].get(r["domain_label"], 0) + 1
    job["results"]  = [
        {
            "rank":        i + 1,
            "candidate_id": r["candidate_id"],
            "score":        r["score"],
            "reasoning":    r["reasoning"],
            "components":   r["components"],
            "career_ev":    r["career_ev"],
            "behav_ev":     r["behav_ev"],
            "disq_reason":  r["disq_reason"],
            "domain":       r["domain"],
            "domain_label": r["domain_label"],
            **r["profile_summary"],
        }
        for i, r in enumerate(top100)
    ]


def _iter_jsonl(file_bytes: bytes):
    """Yield parsed candidate dicts from raw JSONL bytes."""
    for line in file_bytes.decode("utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def _count_lines(file_bytes: bytes) -> int:
    return sum(1 for l in file_bytes.splitlines() if l.strip())


# ──────────────────────────────────────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────────────────────────────────────

TEMPLATE_PATH = Path(__file__).parent / "templates" / "index.html"


@app.route("/")
def index():
    # The page is a self-contained HTML/React (Babel-in-browser) file that uses
    # JSX curly-brace syntax (e.g. `{{ ... }}`), which Jinja2's render_template
    # tries to parse as template expressions and fails on. Serve it as a plain
    # static file instead so Jinja2 never touches it.
    return send_file(TEMPLATE_PATH, mimetype="text/html")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "system": "HUMAN-POTENTIAL-GRAPH"})


@app.route("/api/domains")
def domains():
    """List all available hiring domains (for the UI's domain selector)."""
    return jsonify({"domains": DOMAIN_CHOICES})


@app.route("/api/rank", methods=["POST"])
def rank():
    """
    Accept a JSONL upload, start synchronous ranking (for small files)
    or background ranking, return job_id immediately.

    Optional form field 'domain': one of ranker.domains.DOMAINS keys.
    If omitted, each candidate's domain is auto-detected — the ranker
    scores across ALL domains (AI/ML, Backend, Frontend, Data, DevOps,
    Product, QA...), not just one.

    For hackathon/demo purposes we run synchronously here and stream
    progress via a follow-up SSE endpoint.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded. POST a JSONL file as 'file'."}), 400

    uploaded  = request.files["file"]
    domain_id = request.form.get("domain") or None
    raw       = uploaded.read()
    total     = _count_lines(raw)

    if total == 0:
        return jsonify({"error": "Uploaded file appears to be empty."}), 400

    job_id = str(uuid.uuid4())[:8]
    JOBS[job_id] = {"status": "queued", "total": total, "done": 0, "results": [], "csv_path": None}

    # Run synchronously (for files up to ~100K candidates this finishes in <5 min on CPU)
    _rank_stream(_iter_jsonl(raw), job_id, total, domain_id=domain_id)

    return jsonify({"job_id": job_id, "total": total, "domain": domain_id})


@app.route("/api/rank-sample", methods=["POST"])
def rank_sample():
    """Demo mode: rank the bundled sample_candidates.json without upload."""
    if not SAMPLE_PATH.exists():
        return jsonify({"error": "sample_candidates.json not found."}), 404

    domain_id = (request.form.get("domain") or request.args.get("domain")) or None

    with open(SAMPLE_PATH, encoding="utf-8") as f:
        candidates = json.load(f)

    job_id = str(uuid.uuid4())[:8]
    JOBS[job_id] = {"status": "queued", "total": len(candidates),
                    "done": 0, "results": [], "csv_path": None}

    _rank_stream(iter(candidates), job_id, len(candidates), domain_id=domain_id)

    return jsonify({"job_id": job_id, "total": len(candidates), "domain": domain_id})


@app.route("/api/job/<job_id>")
def job_status(job_id: str):
    """Poll job status and results."""
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Unknown job_id"}), 404

    return jsonify({
        "status":  job["status"],
        "total":   job["total"],
        "done":    job["done"],
        "results": job.get("results", []),
        "domain_counts": job.get("domain_counts", {}),
    })


@app.route("/api/download/<job_id>")
def download(job_id: str):
    """Download the submission CSV for a completed job."""
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Unknown job_id"}), 404
    if job["status"] != "done":
        return jsonify({"error": "Job not complete yet"}), 202
    csv_path = job.get("csv_path")
    if not csv_path or not Path(csv_path).exists():
        return jsonify({"error": "CSV not found"}), 500

    return send_file(
        csv_path,
        mimetype="text/csv",
        as_attachment=True,
        download_name="submission.csv",
    )


# ──────────────────────────────────────────────────────────────────────────────
# CLI ENTRY POINT (for headless ranking: python app.py rank <in> <out>)
# ──────────────────────────────────────────────────────────────────────────────

def cli_rank(input_path: str, output_path: str):
    import sys
    print(f"[HPG] Reading {input_path} ...")
    with open(input_path, "rb") as f:
        raw = f.read()
    total = _count_lines(raw)
    print(f"[HPG] {total:,} candidates found. Scoring ...")

    job_id = "cli"
    JOBS[job_id] = {"status": "queued", "total": total, "done": 0,
                    "results": [], "csv_path": output_path}
    _rank_stream(_iter_jsonl(raw), job_id, total)

    # Override csv_path to user-specified output
    import shutil
    shutil.copy(JOBS[job_id]["csv_path"], output_path)

    print(f"[HPG] Done. Top-100 written to {output_path}")
    print(f"\nTop 10:")
    for r in JOBS[job_id]["results"][:10]:
        print(f"  {r['rank']:>3}. {r['candidate_id']}  {r['score']:.4f}  [{r['domain_label']}]  {r['title']}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2 and sys.argv[1] == "rank":
        in_path  = sys.argv[2] if len(sys.argv) > 2 else "candidates.jsonl"
        out_path = sys.argv[3] if len(sys.argv) > 3 else "submission.csv"
        cli_rank(in_path, out_path)
    else:
        port = int(os.environ.get("PORT", 5000))
        print(f"[HPG] Starting server on http://0.0.0.0:{port}")
        app.run(host="0.0.0.0", port=port, debug=False)
