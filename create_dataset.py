"""
Generates 30+ diverse resumes and 5 job descriptions for RAG profile matching.
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
RESUMES_DIR = BASE_DIR / "data" / "resumes"
JDS_DIR = BASE_DIR / "data" / "job_descriptions"

RESUMES_DIR.mkdir(parents=True, exist_ok=True)
JDS_DIR.mkdir(parents=True, exist_ok=True)

CANDIDATES = [
    # ML & AI
    ("John Doe", "Senior ML Engineer", 6, ["Python", "Machine Learning", "PyTorch", "TensorFlow", "FastAPI", "Docker", "AWS"], "M.Tech CSE, IIT Bombay", "ML Specialist building deep learning recommendation engines serving 50M requests daily."),
    ("Sara Connor", "NLP & LLM Engineer", 5, ["Python", "NLP", "Transformers", "LangChain", "Vector Databases", "ChromaDB", "PyTorch"], "M.S. Data Science, UW", "RAG expert fine-tuning BERT and building dense vector search pipelines for legal contracts."),
    ("Vikram Malhotra", "Computer Vision Specialist", 4, ["Python", "OpenCV", "PyTorch", "TensorRT", "C++", "Docker"], "B.Tech ECE, NIT Trichy", "Deployed real-time edge detection and OCR inference systems for autonomous inspection."),
    ("Aarav Mehta", "MLOps Engineer", 5, ["Python", "Kubeflow", "MLflow", "Docker", "Kubernetes", "AWS SageMaker"], "B.E. CSE, BITS Pilani", "Automated model retraining pipelines and feature store architectures on Kubernetes."),
    ("Elena Rostova", "Data Scientist", 4, ["Python", "R", "Scikit-Learn", "Pandas", "SQL", "Tableau"], "M.S. Statistics, NYU", "Statistical modeling, customer churn forecasting, and predictive marketing algorithms."),

    # Backend Python & Go
    ("Alex Chen", "Backend Systems Architect", 8, ["Python", "Go", "Distributed Systems", "PostgreSQL", "Kafka", "Kubernetes", "gRPC"], "M.S. CS, Stanford", "Event-driven distributed architectures processing 250k events/sec using Go, Python, and Kafka."),
    ("Emily Watson", "Senior Python & FastAPI Engineer", 5, ["Python", "FastAPI", "SQLAlchemy", "Redis", "Celery", "PostgreSQL", "Pytest"], "B.S. CS, UIUC", "High-throughput async APIs, distributed task workers with Celery/Redis, and database tuning."),
    ("Rajesh Iyer", "Python Django Developer", 4, ["Python", "Django", "PostgreSQL", "Celery", "Docker", "AWS"], "B.Tech IT, Anna University", "Scalable multi-tenant SaaS backends with Django REST Framework and PostgreSQL partitioning."),
    ("Marcus Vance", "Go Microservices Developer", 5, ["Go", "Docker", "Kubernetes", "gRPC", "PostgreSQL", "Redis"], "B.S. Software Eng, Purdue", "High-performance microservices in Golang with protobuf/gRPC and sub-10ms P99 latencies."),
    ("Neha Kulkarni", "API Integration Engineer", 3, ["Python", "FastAPI", "REST APIs", "PostgreSQL", "Docker"], "B.Tech CSE, Pune University", "RESTful web services, external webhook processors, and OpenAPI documentation."),

    # Backend Java
    ("Michael Brown", "Java Spring Boot Engineer", 6, ["Java", "Spring Boot", "Microservices", "Hibernate", "MySQL", "Docker", "RabbitMQ"], "B.S. CS, UT Austin", "Resilient enterprise banking systems with Java 17, Spring Boot, and RabbitMQ message queues."),
    ("Aditya Roy", "Senior Java Cloud Architect", 9, ["Java", "Spring Cloud", "Kafka", "PostgreSQL", "Kubernetes", "AWS"], "M.Tech CS, IIT Delhi", "Cloud-native banking microservices architecture supporting 10,000 transactions per second."),
    ("Kavita Nair", "Java Full Stack Developer", 4, ["Java", "Spring Boot", "Angular", "TypeScript", "MySQL"], "B.E. CSE, Kerala University", "Full-stack enterprise applications with Spring Boot REST backends and Angular frontends."),
    ("David Miller", "Java Backend Developer", 3, ["Java", "Spring Boot", "JPA", "PostgreSQL", "Maven"], "B.S. CS, Ohio State", "CRUD services, database migrations with Flyway, and JUnit integration testing."),
    ("Sneha Patil", "Enterprise Java Engineer", 5, ["Java", "Spring Boot", "Redis", "Oracle", "Docker"], "B.E. IT, Mumbai University", "Payment processing gateways, database connection pooling, and multi-threaded processing."),

    # DevOps & Cloud Platform
    ("Priya Sharma", "Lead DevOps & Cloud Engineer", 7, ["Kubernetes", "Docker", "Terraform", "AWS", "CI/CD", "Prometheus", "Python", "Linux"], "B.E. IT, BITS Pilani", "Enterprise multi-account AWS architectures on EKS with Terraform and automated GitHub Actions."),
    ("Carlos Rodriguez", "Site Reliability Engineer (SRE)", 6, ["Python", "Bash", "Linux", "Kubernetes", "Ansible", "Datadog", "Terraform"], "B.S. Systems, FSU", "99.99% service availability, automated incident response runbooks, and chaos engineering."),
    ("Tanya Sen", "Cloud Security Engineer", 5, ["AWS", "Terraform", "Docker", "Kubernetes", "Vault", "IAM", "Python"], "B.Tech CS, Jadavpur Univ", "DevSecOps pipelines, automated IAM least-privilege audits, and HashiCorp Vault secrets management."),
    ("Kevin Zhang", "Infrastructure Automation Engineer", 4, ["Terraform", "Ansible", "AWS", "Linux", "Python", "Docker"], "B.S. CS, UC San Diego", "Infrastructure as Code for automated blue-green deployments across multi-region VPCs."),
    ("Deepak Verma", "Kubernetes Platform Engineer", 5, ["Kubernetes", "Helm", "Istio", "Docker", "Prometheus", "Golang"], "B.Tech CSE, DTU", "Service mesh architecture with Istio and automated cluster scaling on Google Kubernetes Engine."),

    # Full Stack & Frontend
    ("Jane Smith", "Full Stack Software Engineer", 4, ["React", "TypeScript", "Node.js", "Express", "PostgreSQL", "TailwindCSS"], "B.S. Soft Eng, UC Berkeley", "Interactive single-page apps and high-performance Node.js/Express APIs with PostgreSQL."),
    ("Ananya Verma", "Frontend React & UI Engineer", 3, ["React", "JavaScript", "HTML5", "CSS3", "Next.js", "Redux", "Figma"], "B.Tech CE, Delhi University", "Next.js web portals with 98+ Lighthouse scores and pixel-perfect design systems."),
    ("Lucas Silva", "Full Stack MERN Developer", 5, ["MongoDB", "Express", "React", "Node.js", "TypeScript", "Docker"], "B.S. CS, Univ of Sao Paulo", "Full-stack SaaS platforms with real-time WebSocket dashboards and responsive UI components."),
    ("Rohit Joshi", "Senior Frontend Architect", 7, ["React", "TypeScript", "Next.js", "GraphQL", "Webpack", "TailwindCSS"], "B.Tech CSE, VIT Vellore", "Micro-frontend architectures, performance profiling, and SSR optimization for e-commerce."),
    ("Sophie Martin", "Frontend Vue.js Developer", 4, ["Vue.js", "Nuxt.js", "JavaScript", "TailwindCSS", "REST APIs"], "B.S. Web Dev, McGill", "State management with Pinia, responsive mobile-first layouts, and accessible component trees."),

    # Data Engineering
    ("Amit Patel", "Senior Data Engineer", 6, ["Python", "Apache Spark", "Kafka", "SQL", "Snowflake", "Airflow", "AWS"], "M.S. Data Eng, ASU", "Petabyte-scale ETL pipelines, streaming analytics with Kafka/Spark, and Snowflake data warehouses."),
    ("Chloe Bennett", "Big Data Platform Engineer", 5, ["Python", "Hadoop", "Spark", "SQL", "PostgreSQL", "Airflow"], "B.S. CS, Georgia Tech", "Automated batch processing DAGs in Apache Airflow and relational dimensional modeling."),
    ("Ravi Shankar", "Analytics Engineer", 4, ["SQL", "dbt", "Snowflake", "Python", "Looker", "PostgreSQL"], "B.Tech IT, SRM University", "Modern data stack transformations using dbt, automated data quality tests, and LookML modeling."),
    ("Megan Foster", "Streaming Pipeline Engineer", 5, ["Kafka", "Flink", "Python", "Java", "Docker", "Kubernetes"], "B.S. CS, Michigan", "Sub-second streaming analytics with Apache Flink and Kafka event hub architectures."),
    ("Siddharth Rao", "Database Administrator & Data Ops", 6, ["PostgreSQL", "MySQL", "Python", "Linux", "Docker", "Performance Tuning"], "B.E. CS, Bangalore Univ", "High-availability database clustering, index optimization, query tuning, and replication.")
]

JOB_DESCRIPTIONS = [
    {
        "id": "jd-1",
        "title": "Senior Machine Learning Engineer",
        "must_have_skills": ["Python", "Machine Learning", "PyTorch", "Docker"],
        "min_experience_years": 5,
        "description": "We are seeking a Senior ML Engineer with 5+ years of experience in Python, PyTorch, and Docker. The ideal candidate will design, build, and deploy production machine learning models and recommendation engines on cloud platforms."
    },
    {
        "id": "jd-2",
        "title": "Lead DevOps & Cloud Engineer",
        "must_have_skills": ["Kubernetes", "Docker", "Terraform", "AWS"],
        "min_experience_years": 5,
        "description": "Looking for a Lead DevOps Engineer with 5+ years of expertise in Kubernetes, Docker, Terraform, and AWS. Responsible for cloud infrastructure automation, CI/CD pipeline modernization, and zero-downtime microservice orchestration."
    },
    {
        "id": "jd-3",
        "title": "Full Stack React & Node.js Developer",
        "must_have_skills": ["React", "Node.js", "TypeScript", "PostgreSQL"],
        "min_experience_years": 3,
        "description": "Hiring a Full Stack Developer with 3+ years experience building web applications with React, TypeScript, and Node.js. Must possess strong relational database skills with PostgreSQL and modern REST API design."
    },
    {
        "id": "jd-4",
        "title": "Backend Distributed Systems Engineer",
        "must_have_skills": ["Python", "Kafka", "Distributed Systems", "PostgreSQL"],
        "min_experience_years": 5,
        "description": "Seeking a Backend Distributed Systems Engineer with 5+ years of experience in Python, Kafka, and PostgreSQL. Must have hands-on experience building low-latency, event-driven distributed microservices."
    },
    {
        "id": "jd-5",
        "title": "Java Spring Boot Cloud Developer",
        "must_have_skills": ["Java", "Spring Boot", "Microservices", "Docker"],
        "min_experience_years": 4,
        "description": "Exciting role for a Java Backend Engineer with 4+ years experience in Java and Spring Boot. You will build and scale enterprise microservices, integrate message brokers, and deploy containerized services with Docker."
    }
]

def generate():
    for name, title, exp, skills, edu, summary in CANDIDATES:
        slug = name.lower().replace(" ", "_")
        filename = f"resume_{slug}.txt"
        filepath = RESUMES_DIR / filename
        content = (
            f"NAME: {name}\n"
            f"TITLE: {title}\n"
            f"EXPERIENCE: {exp} years\n"
            f"EDUCATION: {edu}\n"
            f"SKILLS: {', '.join(skills)}\n\n"
            f"PROFESSIONAL SUMMARY:\n{summary}\n\n"
            f"WORK EXPERIENCE:\n"
            f"Senior Role (2021 - Present):\n- Core contributions and architectural execution across {', '.join(skills[:3])}.\n"
            f"Previous Role (2018 - 2021):\n- Built high-performance software modules and collaborated in Agile squads.\n\n"
            f"CERTIFICATIONS & AWARDS:\n- Certified Solutions Professional\n"
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"Generated {len(CANDIDATES)} diverse resumes in {RESUMES_DIR}")

    for jd in JOB_DESCRIPTIONS:
        filepath = JDS_DIR / f"{jd['id']}_{jd['title'].lower().replace(' ', '_').replace('&', 'and')}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(jd, f, indent=2)

    print(f"Generated {len(JOB_DESCRIPTIONS)} job descriptions in {JDS_DIR}")

if __name__ == "__main__":
    generate()
