# AIApplyJobs

An end-to-end AI-powered job application pipeline that automatically discovers, scores, tailors, and applies for jobs on your behalf — using large language models and browser automation.

---

## Overview

AIApplyJobs scrapes thousands of job listings from major job boards, uses AI to score each one against your resume and profile, generates tailored resumes and cover letters, and then autonomously fills out and submits job applications through a real browser — all with minimal human involvement.

---

## Pipeline Stages

The system runs as a sequential pipeline. Each stage feeds into the next:

```
discover → enrich → score → tailor → cover → apply
```

| Stage | Command | What it does |
|-------|---------|--------------|
| **Discover** | `applypilot run discover` | Scrapes job listings from Indeed, LinkedIn, Glassdoor, ZipRecruiter, and Dice |
| **Enrich** | `applypilot run enrich` | Fetches full job descriptions for each listing |
| **Score** | `applypilot run score` | Uses an LLM to score each job 1–10 based on fit with your resume |
| **Tailor** | `applypilot run tailor` | Rewrites your resume for each high-scoring job |
| **Cover** | `applypilot run cover` | Generates a custom cover letter for each job |
| **Apply** | `applypilot apply` | Spawns Claude AI + Playwright to fill and submit the application form |

You can also run tailor and cover together:
```
applypilot run tailor cover
```

---

## Features

- **Multi-board job scraping** — Pulls from Indeed, LinkedIn, Glassdoor, ZipRecruiter, and Dice simultaneously
- **AI fit scoring** — LLM rates each job 1–10 based on your resume, skills, and target role; only jobs scoring 7+ move forward
- **Resume tailoring** — Generates a role-specific resume for each job while preserving real companies, metrics, and facts
- **Cover letter generation** — Writes a personalised cover letter for each job using your profile and the job description
- **Fully autonomous application** — Uses Claude AI + Playwright MCP to control a real Chrome browser and fill in Workday/ATS forms
- **Parallel workers** — Runs multiple apply workers simultaneously with isolated Chrome profiles
- **SQLite pipeline DB** — All state (discovery → applied) tracked in a single local database with WAL mode
- **HTML dashboard** — Visual job browser showing scores, status, links, and salary info (`view_jobs.py`)
- **Configurable searches** — `searches.yaml` controls job queries, locations, boards, and keyword filters
- **LLM-agnostic** — Works with Gemini, Groq, OpenAI, or a local Ollama model
- **CAPTCHA support** — Optional CapSolver integration for CAPTCHA-protected forms

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Job scraping | [JobSpy](https://github.com/Bunsly/JobSpy), custom Dice scraper |
| Database | SQLite (WAL mode) |
| LLM scoring/tailoring | Gemini / Groq (llama-3.1) / OpenAI / Ollama |
| Browser automation | [Claude Code CLI](https://github.com/anthropics/claude-code) + [Playwright MCP](https://github.com/microsoft/playwright-mcp) |
| Browser | Chromium via Chrome DevTools Protocol (CDP) |
| PDF generation | WeasyPrint / ReportLab |
| Language | Python 3.11+ |
| Runner scripts | PowerShell |

---

## Getting Started

### Prerequisites

- Python 3.11+
- [Claude Code CLI](https://github.com/anthropics/claude-code) installed and authenticated (`claude` in PATH)
- An LLM API key (Gemini recommended for free tier speed)
- Chrome or Chromium installed

### Installation

```bash
# Clone the repo
git clone https://github.com/vivekshekharrai-del/AIApplyJobs.git
cd AIApplyJobs

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install applypilot
```

### Configuration

**1. Set up your environment:**
```bash
cp .env.example .env
# Edit .env and add your LLM API key
```

**2. Set up your profile:**
```bash
cp profile.example.json profile.json
# Edit profile.json with your personal details, skills, and salary expectations
```

**3. Set up your resume:**
```
# Add your resume as resume.txt in the project root
```

**4. Configure your job search:**
```bash
# Edit searches.yaml to set your target roles, locations, and job boards
```

### Running the Pipeline

Use the included PowerShell scripts or run commands directly:

```powershell
# Score jobs (runs discover → enrich → score)
.\run_score.ps1

# Tailor resumes + cover letters for scored jobs (dry run — check one job first)
.\run_tailor_cover_test.ps1

# Tailor resumes + cover letters for all high-scoring jobs
.\run_tailor_cover.ps1

# Test apply (1 job, dry run)
.\run_apply_test.ps1

# Apply to up to 4 jobs in parallel
.\run_apply_4.ps1
```

Or run pipeline stages individually:
```bash
applypilot run discover
applypilot run score
applypilot run tailor cover
applypilot apply --limit 4 --min-score 7
```

### View Dashboard

```bash
python view_jobs.py
# Opens jobs_view.html in your browser
```

---

## Project Structure

```
AIApplyJobs/
├── searches.yaml          # Job search queries, locations, boards, filters
├── profile.example.json   # Template for personal profile (copy to profile.json)
├── .env.example           # Template for API keys (copy to .env)
├── view_jobs.py           # Generates HTML job dashboard
├── db_stats.py            # Prints pipeline statistics from the DB
├── rank_jobs.py           # Lists top-scoring jobs
├── check_dice.py          # Checks Dice.com job scraper status
├── run_score.ps1          # PowerShell: run discover → score
├── run_tailor_cover.ps1   # PowerShell: run tailor + cover
├── run_tailor_cover_test.ps1  # PowerShell: test tailor on 1 job
├── run_apply_4.ps1        # PowerShell: apply to up to 4 jobs
├── run_apply_test.ps1     # PowerShell: dry-run apply on 1 job
├── applypilot.ps1         # PowerShell wrapper for applypilot CLI
├── applypilot.bat         # Batch wrapper for applypilot CLI
└── venv/                  # Python virtual environment (not committed)
```

**Runtime-generated (not committed):**
```
applypilot.db       # SQLite database (all pipeline state)
profile.json        # Your personal profile (keep private)
resume.txt          # Your base resume (keep private)
resume.pdf          # Generated PDF resume
tailored_resumes/   # Per-job tailored resume PDFs
cover_letters/      # Per-job cover letter PDFs
logs/               # Apply worker logs
chrome-workers/     # Chrome profile data per worker
apply-workers/      # Apply worker state
jobs_view.html      # Generated dashboard
```

---

## Supported Job Boards

- **Indeed**
- **LinkedIn**
- **Glassdoor**
- **ZipRecruiter**
- **Dice** (via dedicated scraper)

---

## LLM Provider Options

Configure in `.env`:

| Provider | Speed | Cost | Notes |
|----------|-------|------|-------|
| Gemini (aistudio.google.com) | Fast | Free tier available | Recommended |
| Groq (console.groq.com) | Medium | Free tier (rate limited) | llama-3.1-8b-instant |
| OpenAI | Fast | Paid | gpt-4o-mini recommended |
| Ollama (local) | Depends on hardware | Free | Full privacy |

---

## Disclaimer

This tool automates job applications. Use responsibly and in accordance with the terms of service of each job board and employer portal. Always review applications before submission when possible.

---

## License

MIT
