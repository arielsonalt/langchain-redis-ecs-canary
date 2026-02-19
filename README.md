# LangChain Agent + Redis + ECS Canary 10% (AWS)

Production-ready example of a LangChain Agent with Redis-backed memory, deployed on AWS ECS Fargate using Blue/Green deployments with Canary 10% traffic shifting via CodeDeploy.

---

## 🚀 Architecture Overview

- **FastAPI** REST API
- **LangChain Agent** (tool-calling)
- **Redis (ElastiCache)** for conversation memory
- **Amazon ECS Fargate**
- **Application Load Balancer**
- **AWS CodeDeploy (Blue/Green)**
- **Canary Deployment: 10% for 5 minutes**
- **GitHub Actions CI/CD**
- **Amazon ECR**
- **AWS Secrets Manager**

---

## 🏗 High-Level Flow

1. Developer pushes to `main`
2. GitHub Actions:
   - Builds Docker image
   - Pushes image to ECR
   - Registers new ECS Task Definition
   - Creates CodeDeploy deployment
3. CodeDeploy:
   - Routes 10% traffic to new version (Green)
   - Waits 5 minutes
   - If healthy → shifts 100%
   - If unhealthy → rollback

---

## 📁 Project Structure
langchain-redis-ecs-canary/
│
├── app/
│  ├── main.py
│  └── requirements.txt
│
├── Dockerfile
├── taskdef.json
├── appspec.yaml
│
├── scripts/
│   └── render-taskdef.sh
│
└── .github/workflows/
    └── deploy.yml


