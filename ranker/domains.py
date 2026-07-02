"""
HUMAN-POTENTIAL-GRAPH — Domain Registry
========================================
The original ranker only understood one job profile: Senior AI Engineer
(embeddings, vector DBs, retrieval/ranking). This registry generalizes the
scoring engine to multiple hiring domains, each with its own:

  - core_skills          → MUST-HAVE skills for that role (2.5× weight)
  - bonus_skills         → NICE-TO-HAVE skills (1× weight)
  - career_phrases       → production-evidence phrases mined from role descriptions
  - title_keywords       → terms that mark a title as belonging to this domain
  - wrong_domain_skills  → skills that signal a DIFFERENT primary domain
  - disqualified_titles  → titles that are clear non-fits for this domain

Add a new domain by adding a new entry to DOMAINS — the scorer and UI
pick it up automatically (dropdown + auto-detect both read this dict).
"""

# ── DOMAIN REGISTRY ─────────────────────────────────────────────────────────

DOMAINS = {

    # ────────────────────────────────────────────────────────────────────
    "ai_ml_engineer": {
        "label": "AI / ML Engineer",
        "core_skills": {
            "embedding", "embeddings", "sentence-transformers", "sentence transformers",
            "openai embeddings", "bge", "e5", "ada", "text-embedding", "dense retrieval",
            "bi-encoder", "cross-encoder", "semantic search", "neural search",
            "pinecone", "weaviate", "qdrant", "milvus", "faiss", "opensearch",
            "elasticsearch", "chroma", "chromadb", "pgvector", "redis vector",
            "vector database", "vector db", "vector store", "hnsw",
            "retrieval", "ranking", "reranking", "re-ranking", "bm25", "hybrid search",
            "vector search", "information retrieval", "ndcg", "mrr", "map@k",
            "mean average precision", "evaluation framework", "recall@", "a/b test",
            "pytorch", "tensorflow", "hugging face", "transformers", "fine-tuning",
            "fine tuning", "finetuning", "nlp", "language model", "llm", "bert",
            "sentence bert", "rag", "retrieval augmented generation", "python",
        },
        "bonus_skills": {
            "lora", "qlora", "peft", "learning to rank", "lambdamart",
            "xgboost", "lightgbm", "collaborative filtering", "recommendation",
            "recommender", "online evaluation", "offline evaluation", "a/b testing",
            "langchain", "llamaindex", "distributed systems", "kafka", "spark",
            "mlops", "mlflow", "kubeflow", "bentoml", "triton", "onnx", "tensorrt",
            "openai", "anthropic", "cohere", "gemini", "fastapi", "flask",
            "redis", "postgres", "postgresql", "ray", "celery", "airflow",
            "docker", "kubernetes", "aws sagemaker", "gcp vertex", "azure ml",
        },
        "career_phrases": [
            "ranking system", "retrieval system", "search system", "recommendation system",
            "recommender system", "ranking model", "search engine", "ranking pipeline",
            "retrieval pipeline", "ranking infrastructure", "search infrastructure",
            "embedding pipeline", "vector index", "embedding model", "semantic similarity",
            "dense retrieval", "neural retrieval", "bi-encoder", "cross-encoder",
            "embedding space", "vector store", "faiss index",
            "production deployment", "deployed to production", "shipped",
            "production ml", "ml in production", "at scale", "online serving",
            "real users", "production system", "production traffic", "serving",
            "a/b test", "ndcg", "mrr", "recall@", "precision@", "offline eval",
            "evaluation pipeline", "evaluation framework", "ranking metric",
            "online experiment", "shadow deployment",
            "candidate ranking", "job matching", "talent", "search relevance",
            "information retrieval", "ir system", "relevance model",
            "hybrid retrieval", "bm25", "rag", "llm-based",
            "ml engineer", "ai engineer", "machine learning engineer",
            "applied scientist", "research engineer", "staff ml",
        ],
        "title_keywords": [
            "ml", "ai ", "machine learning", "nlp", "applied scientist",
            "research engineer", "ai engineer", "data scientist",
        ],
        "wrong_domain_skills": {
            "computer vision", "speech recognition", "speech synthesis",
            "tts", "asr", "robotics", "autonomous driving", "object detection",
            "image classification", "image segmentation", "yolo", "ocr",
            "lidar", "slam", "pose estimation",
        },
        "disqualified_titles": {
            "accountant", "hr manager", "marketing manager", "content writer",
            "graphic designer", "civil engineer", "mechanical engineer",
            "operations manager", "sales executive", "customer support",
            "business analyst", "project manager", "product manager",
            "financial analyst", "supply chain", "procurement",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    "software_engineer": {
        "label": "Software Engineer (Backend / Full-Stack)",
        "core_skills": {
            "java", "python", "go", "golang", "c++", "c#", ".net", "node.js", "nodejs",
            "rest api", "restful", "graphql", "grpc", "microservices", "system design",
            "postgres", "postgresql", "mysql", "mongodb", "redis", "sql",
            "spring boot", "spring", "django", "flask", "fastapi", "express",
            "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd", "git",
            "distributed systems", "multithreading", "concurrency", "data structures",
            "algorithms", "object oriented", "oop", "unit testing", "tdd",
        },
        "bonus_skills": {
            "kafka", "rabbitmq", "elasticsearch", "terraform", "jenkins",
            "github actions", "grpc", "protobuf", "bazel", "load balancing",
            "caching", "message queue", "event driven", "domain driven design",
            "clean architecture", "design patterns", "scalability", "high availability",
            "typescript", "react", "vue", "angular", "graphql", "websocket",
        },
        "career_phrases": [
            "scalable backend", "backend system", "distributed system", "microservice architecture",
            "rest api", "api gateway", "system design", "high availability",
            "production system", "production deployment", "deployed to production",
            "scaled to", "handled millions", "reduced latency", "improved throughput",
            "database optimization", "query optimization", "caching layer",
            "ci/cd pipeline", "code review", "technical design doc", "architecture design",
            "load balancer", "horizontal scaling", "fault tolerant", "zero downtime",
            "software engineer", "backend engineer", "full stack engineer",
            "platform engineer", "staff engineer", "principal engineer",
        ],
        "title_keywords": [
            "software engineer", "backend", "full stack", "fullstack", "platform engineer",
            "staff engineer", "principal engineer", "swe", "developer",
        ],
        "wrong_domain_skills": {
            "photoshop", "illustrator", "figma", "sketch", "adobe xd",
            "seo", "content marketing", "email campaign", "social media marketing",
        },
        "disqualified_titles": {
            "accountant", "hr manager", "marketing manager", "content writer",
            "graphic designer", "civil engineer", "mechanical engineer",
            "sales executive", "customer support", "financial analyst",
            "supply chain", "procurement",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    "data_engineer": {
        "label": "Data Engineer",
        "core_skills": {
            "spark", "pyspark", "hadoop", "kafka", "airflow", "dbt", "etl", "elt",
            "data pipeline", "data warehouse", "snowflake", "redshift", "bigquery",
            "sql", "python", "scala", "hive", "presto", "trino", "databricks",
            "data modeling", "star schema", "dimensional modeling", "data lake",
            "delta lake", "parquet", "avro", "batch processing", "stream processing",
            "kinesis", "flink", "orchestration",
        },
        "bonus_skills": {
            "terraform", "docker", "kubernetes", "aws glue", "aws emr",
            "gcp dataflow", "azure data factory", "great expectations",
            "data quality", "data governance", "metadata management",
            "cdc", "change data capture", "kafka connect", "debezium",
            "airbyte", "fivetran", "looker", "tableau", "power bi",
        },
        "career_phrases": [
            "data pipeline", "etl pipeline", "elt pipeline", "data warehouse",
            "built pipeline", "orchestrated workflow", "data lake", "batch processing",
            "stream processing", "real-time pipeline", "data ingestion",
            "data modeling", "schema design", "reduced pipeline latency",
            "processed terabytes", "processed petabytes", "data quality checks",
            "data governance", "scalable data infrastructure", "data platform",
            "data engineer", "analytics engineer", "big data engineer",
        ],
        "title_keywords": [
            "data engineer", "analytics engineer", "big data", "etl developer",
            "data platform",
        ],
        "wrong_domain_skills": {
            "photoshop", "illustrator", "figma", "seo", "content marketing",
        },
        "disqualified_titles": {
            "accountant", "hr manager", "marketing manager", "content writer",
            "graphic designer", "civil engineer", "mechanical engineer",
            "sales executive", "customer support", "financial analyst",
            "supply chain", "procurement",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    "devops_cloud": {
        "label": "DevOps / Cloud / SRE",
        "core_skills": {
            "kubernetes", "docker", "terraform", "ansible", "aws", "gcp", "azure",
            "ci/cd", "jenkins", "github actions", "gitlab ci", "helm", "prometheus",
            "grafana", "cloudformation", "iac", "infrastructure as code",
            "site reliability", "sre", "monitoring", "observability", "logging",
            "linux", "bash", "shell scripting", "networking", "vpc",
            "load balancing", "auto scaling", "incident response", "on-call",
        },
        "bonus_skills": {
            "istio", "service mesh", "argo cd", "argocd", "spinnaker",
            "datadog", "new relic", "elk stack", "splunk", "pagerduty",
            "chaos engineering", "disaster recovery", "cost optimization",
            "security hardening", "compliance", "vault", "secrets management",
        },
        "career_phrases": [
            "reduced downtime", "improved reliability", "incident response",
            "on-call rotation", "infrastructure as code", "automated deployment",
            "ci/cd pipeline", "container orchestration", "kubernetes cluster",
            "cloud migration", "cost reduction", "auto scaling", "high availability",
            "disaster recovery", "sla", "slo", "sli", "uptime", "99.9%", "99.99%",
            "monitoring dashboard", "alerting", "chaos engineering",
            "devops engineer", "sre", "site reliability engineer", "platform engineer",
            "infrastructure engineer", "cloud engineer",
        ],
        "title_keywords": [
            "devops", "sre", "site reliability", "cloud engineer",
            "infrastructure engineer", "platform engineer",
        ],
        "wrong_domain_skills": {
            "photoshop", "illustrator", "figma", "seo", "content marketing",
        },
        "disqualified_titles": {
            "accountant", "hr manager", "marketing manager", "content writer",
            "graphic designer", "civil engineer", "mechanical engineer",
            "sales executive", "customer support", "financial analyst",
            "supply chain", "procurement",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    "frontend_engineer": {
        "label": "Frontend Engineer",
        "core_skills": {
            "javascript", "typescript", "react", "vue", "angular", "html", "css",
            "next.js", "nextjs", "nuxt", "webpack", "vite", "redux", "state management",
            "responsive design", "accessibility", "a11y", "web performance",
            "css3", "html5", "sass", "tailwind", "component library",
            "rest api", "graphql", "jest", "cypress", "testing library",
        },
        "bonus_skills": {
            "storybook", "figma", "design system", "micro frontend",
            "server side rendering", "ssr", "static site generation", "ssg",
            "web vitals", "lighthouse", "pwa", "service worker",
            "webassembly", "three.js", "d3.js", "canvas", "svg animation",
        },
        "career_phrases": [
            "improved page load", "reduced bundle size", "web performance",
            "responsive design", "accessibility improvements", "component library",
            "design system", "pixel perfect", "cross browser", "user interface",
            "user experience", "conversion rate", "a/b tested ui", "frontend architecture",
            "micro frontend", "server side rendering", "static site generation",
            "frontend engineer", "ui engineer", "web developer", "react developer",
        ],
        "title_keywords": [
            "frontend", "front-end", "ui engineer", "web developer", "react developer",
        ],
        "wrong_domain_skills": {
            "kubernetes", "terraform", "ansible", "site reliability",
        },
        "disqualified_titles": {
            "accountant", "hr manager", "civil engineer", "mechanical engineer",
            "sales executive", "customer support", "financial analyst",
            "supply chain", "procurement",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    "data_analyst_bi": {
        "label": "Data Analyst / BI",
        "core_skills": {
            "sql", "excel", "tableau", "power bi", "looker", "data visualization",
            "dashboard", "reporting", "python", "pandas", "statistics",
            "a/b testing", "hypothesis testing", "data cleaning", "etl",
            "business intelligence", "kpi", "metrics", "google analytics",
        },
        "bonus_skills": {
            "r", "google sheets", "dax", "power query", "snowflake",
            "bigquery", "redshift", "regression", "forecasting", "cohort analysis",
            "funnel analysis", "segmentation", "sql server", "postgres",
        },
        "career_phrases": [
            "built dashboard", "data visualization", "business intelligence",
            "kpi tracking", "reporting automation", "data driven decision",
            "stakeholder reporting", "ad hoc analysis", "cohort analysis",
            "funnel analysis", "a/b test analysis", "revenue analysis",
            "reduced reporting time", "self-serve analytics", "data storytelling",
            "data analyst", "business analyst", "bi analyst", "bi developer",
            "reporting analyst", "insights analyst",
        ],
        "title_keywords": [
            "data analyst", "business analyst", "bi analyst", "bi developer",
            "reporting analyst", "insights analyst",
        ],
        "wrong_domain_skills": {
            "kubernetes", "terraform", "react", "photoshop",
        },
        "disqualified_titles": {
            "accountant", "hr manager", "content writer", "graphic designer",
            "civil engineer", "mechanical engineer", "sales executive",
            "customer support", "supply chain", "procurement",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    "product_manager": {
        "label": "Product Manager",
        "core_skills": {
            "product strategy", "roadmap", "product roadmap", "user research",
            "a/b testing", "product analytics", "stakeholder management",
            "prioritization", "agile", "scrum", "jira", "product requirements",
            "prd", "go-to-market", "customer discovery", "wireframing",
        },
        "bonus_skills": {
            "sql", "figma", "mixpanel", "amplitude", "google analytics",
            "okrs", "competitive analysis", "pricing strategy",
            "growth strategy", "user personas", "customer journey mapping",
        },
        "career_phrases": [
            "product roadmap", "launched product", "increased engagement",
            "increased retention", "reduced churn", "grew revenue",
            "led cross-functional", "stakeholder alignment", "user research",
            "customer discovery", "go-to-market strategy", "product-market fit",
            "a/b tested feature", "prioritized backlog", "shipped feature",
            "product manager", "senior product manager", "group product manager",
            "product owner",
        ],
        "title_keywords": [
            "product manager", "product owner", "group product manager",
            "associate product manager", "apm",
        ],
        "wrong_domain_skills": {
            "kubernetes", "terraform", "docker", "photoshop",
        },
        "disqualified_titles": {
            "accountant", "hr manager", "civil engineer", "mechanical engineer",
            "sales executive", "customer support", "supply chain", "procurement",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    "qa_test_engineer": {
        "label": "QA / Test Engineer (SDET)",
        "core_skills": {
            "selenium", "cypress", "playwright", "test automation", "manual testing",
            "test case design", "regression testing", "api testing", "postman",
            "junit", "testng", "pytest", "test plan", "bug tracking", "jira",
            "performance testing", "load testing", "jmeter", "sdet",
        },
        "bonus_skills": {
            "ci/cd", "docker", "appium", "mobile testing", "accessibility testing",
            "security testing", "test data management", "bdd", "cucumber",
            "gherkin", "contract testing", "chaos testing",
        },
        "career_phrases": [
            "test automation framework", "reduced regression time", "test coverage",
            "automated test suite", "ci/cd integration", "bug triage",
            "quality assurance", "test strategy", "performance testing",
            "load testing", "api test automation", "end to end testing",
            "qa engineer", "test engineer", "sdet", "automation engineer",
            "quality engineer",
        ],
        "title_keywords": [
            "qa engineer", "test engineer", "sdet", "automation engineer",
            "quality engineer", "quality assurance",
        ],
        "wrong_domain_skills": {
            "photoshop", "illustrator", "content marketing",
        },
        "disqualified_titles": {
            "accountant", "hr manager", "marketing manager", "content writer",
            "civil engineer", "mechanical engineer", "sales executive",
            "financial analyst", "supply chain", "procurement",
        },
    },
}

DOMAIN_CHOICES = [{"id": k, "label": v["label"]} for k, v in DOMAINS.items()]

# Titles that are non-technical regardless of domain — used as a global sanity
# check alongside each domain's own disqualified_titles.
GLOBAL_NONTECH_TITLES = {
    "accountant", "hr manager", "marketing manager", "content writer",
    "graphic designer", "sales executive", "customer support",
    "financial analyst", "supply chain", "procurement",
}
