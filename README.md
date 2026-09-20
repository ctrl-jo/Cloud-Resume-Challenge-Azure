# ☁️ Azure Cloud Resume Challenge

A full-stack cloud resume built on Microsoft Azure, inspired by [The Cloud Resume Challenge](https://cloudresumechallenge.dev/docs/the-challenge/azure/) by Forrest Brazeal.

This project demonstrates hands-on cloud skills by deploying a personal resume as a static website with a serverless visitor counter — all hosted, secured, and automated on Azure.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GitHub Actions (CI/CD)                       │
│              Automates frontend deployment & backend tests          │
└──────────────┬──────────────────────────────────┬───────────────────┘
               │                                  │
               ▼                                  ▼
┌──────────────────────────┐       ┌────────────────────────────────┐
│       Frontend           │       │          Backend               │
│                          │       │                                │
│  HTML / CSS / JavaScript │       │  Azure Functions (Python)      │
│         ▼                │       │         ▼                      │
│  Azure Blob Storage      │       │  Azure CosmosDB                │
│  (Static Website)        │       │  (Visitor Counter - Table API) │
│         ▼                │       │                                │
│  Cloudflare CDN          │       └────────────────────────────────┘
│  (HTTPS + Custom Domain) │
└──────────────────────────┘
```

### Technology Stack

| Layer         | Technology                        | Purpose                                      |
|---------------|-----------------------------------|----------------------------------------------|
| **Frontend**  | HTML / CSS / JavaScript           | Resume layout, styling, and visitor counter display |
| **Hosting**   | Azure Blob Storage (Static Site)  | Serves the static website files              |
| **CDN / DNS** | Cloudflare (Edge Proxy + DNS)     | Global Anycast CDN, TLS 1.2+ HTTPS, and custom domain routing |
| **API**       | Azure Functions (Python)          | Serverless HTTP-triggered API for the visitor counter |
| **Database**  | Azure CosmosDB (Table API)        | Stores and retrieves the visitor count        |
| **CI/CD**     | GitHub Actions                    | Automated testing, build, and deployment pipelines |
| **IaC**       | ARM Templates / Bicep *(optional)*| Infrastructure as Code for Azure resources   |

---

## Project Structure

```
azure-cloud-resume/
├── frontend/          # HTML, CSS, JS for the resume website
├── backend/           # Azure Functions (Python) for the visitor counter API
├── infra/             # Infrastructure as Code (Bicep) for Azure resources
├── reference/         # Architecture diagrams, notes, and reference material
├── resume/            # Source resume file (PDF) used for website content
├── LICENSE            # MIT License
└── README.md          # Project documentation (you are here)
```

---

## Challenge Progress Checklist

Track progress across all 16 steps of the Cloud Resume Challenge:

### Certification
- [x] **2026-09-01** | **1. Certification** — Earn the AZ-900: Microsoft Azure Fundamentals certification.

### Frontend
- [x] **2026-09-11** | **2. HTML** — Build the resume using HTML.
- [x] **2026-09-11** | **3. CSS** — Style the resume with CSS.
- [x] **2026-09-13** | **4. Static Website** — Deploy the resume as an Azure Storage static website.
- [x] **2026-09-15** | **5. HTTPS** — Enable HTTPS via Cloudflare edge SSL/TLS.
- [x] **2026-09-15** | **6. DNS** — Configure custom domain (jdmercado.site) pointing to the site.

### Backend
- [x] **2026-09-16** | **7. JavaScript** — Add a visitor counter to the site using JavaScript.
- [x] **2026-09-17** | **8. Database** — Create an Azure CosmosDB table to store the visitor count.
- [x] **2026-09-18** | **9. API** — Build an Azure Function (HTTP-triggered, Python) to interact with CosmosDB.
- [x] **2026-09-18** | **10. Python** — Write the Azure Function logic in Python.

### Testing
- [x] **2026-09-19** | **11. Tests** — Write tests for the Python Azure Function code.

### Infrastructure as Code
- [x] **2026-09-19** | **12. Infrastructure as Code** — Define Azure resources using ARM/Bicep templates.

### CI/CD (Backend)
- [x] **2026-09-19** | **13. Source Control** — Store backend code in a GitHub repository.
- [ ] **14. CI/CD (Backend)** — Set up GitHub Actions to test and deploy the backend automatically.

### CI/CD (Frontend)
- [ ] **15. CI/CD (Frontend)** — Set up GitHub Actions to deploy frontend changes to Azure Storage automatically.

### Documentation
- [ ] **16. Blog Post** — Write a blog post documenting the journey and lessons learned.

---

## Certification

✅ **AZ-900: Microsoft Azure Fundamentals** — Achieved

[![AZ-900 Credential](https://img.shields.io/badge/AZ--900-Certified-0078D4?style=for-the-badge&logo=microsoft-azure&logoColor=white)](https://learn.microsoft.com/api/credentials/share/en-us/JD-0113/AA263BB10BC58AD6?sharingId=7F180DC54DF78889)

> [View Credential](https://learn.microsoft.com/api/credentials/share/en-us/JD-0113/AA263BB10BC58AD6?sharingId=7F180DC54DF78889)

---

## Live Site

| Resource            | URL |
|---------------------|-----|
| **Live Resume**     | [https://jdmercado.site](https://jdmercado.site) (or [https://www.jdmercado.site](https://www.jdmercado.site)) |
| **Azure Origin**    | https://jdmcloudresumest.z7.web.core.windows.net/ |
| **API Endpoint**    | _Coming soon_ |

---

## Getting Started

### Prerequisites

- [Azure Account](https://azure.microsoft.com/en-us/free/) (Free tier available)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
- [Python 3.9+](https://www.python.org/downloads/)
- [Node.js](https://nodejs.org/) (for Azure Functions tooling)
- [Git](https://git-scm.com/)
- [Visual Studio Code](https://code.visualstudio.com/) (recommended)

### Local Development

```bash
# Clone the repository
git clone https://github.com/ctrl-jo/Cloud-Resume-Challenge-Azure.git
cd azure-cloud-resume

# Backend — Install Python dependencies
cd backend
pip install -r requirements.txt

# Frontend — Open index.html in your browser
cd ../frontend
# Open index.html directly or use a local server
```

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

## Acknowledgments

- [Forrest Brazeal](https://forrestbrazeal.com/) — Creator of the Cloud Resume Challenge
- [The Cloud Resume Challenge](https://cloudresumechallenge.dev/) — The original challenge that inspired this project
- [Microsoft Azure Documentation](https://learn.microsoft.com/en-us/azure/) — Official Azure docs