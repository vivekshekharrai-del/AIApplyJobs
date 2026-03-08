# AIApplyJobs — Complete Setup Guide

**For non-technical users. Follow every step in order.**

This tool automatically finds jobs online, scores them against your resume, rewrites your resume for each job, and applies to them on your behalf using AI.

---

## What You Will Need

Before you start, make sure you have:

- A Windows computer (Windows 10 or 11)
- A stable internet connection
- Your resume saved as a plain text file (`.txt`)
- An AI API key (free — instructions below)
- About 30–45 minutes for the one-time setup

---

## Part 1 — Install Required Software

You only need to do Part 1 once. Skip any item you already have installed.

---

### Step 1 — Install Python

Python is the programming language this tool runs on.

1. Go to: **https://www.python.org/downloads/**
2. Click the big yellow **"Download Python 3.13"** button
3. Run the installer
4. **IMPORTANT:** On the first screen, tick the box that says **"Add Python to PATH"** before clicking Install
5. Click **Install Now** and wait for it to finish
6. Click **Close**

**To verify it worked:**
- Press `Windows key + R`, type `cmd`, press Enter
- Type `python --version` and press Enter
- You should see something like `Python 3.13.x`

---

### Step 2 — Install Git

Git is used to download the project code.

1. Go to: **https://git-scm.com/download/win**
2. The download should start automatically — run the installer
3. Click **Next** through all the screens (defaults are fine)
4. Click **Install**, then **Finish**

---

### Step 3 — Install Google Chrome

The tool uses Chrome to automatically fill in job applications.

1. Go to: **https://www.google.com/chrome/**
2. Download and install Chrome if you don't already have it

---

### Step 4 — Install Node.js

Node.js is needed for the browser automation component.

1. Go to: **https://nodejs.org/**
2. Click the **"LTS"** download button (the left one)
3. Run the installer and click **Next** through all screens
4. Click **Install**, then **Finish**

---

### Step 5 — Install Claude Code

Claude Code is the AI that fills in application forms.

1. Press `Windows key + R`, type `cmd`, press Enter
2. Copy and paste this command, then press Enter:
   ```
   npm install -g @anthropic-ai/claude-code
   ```
3. Wait for it to finish (may take a minute)
4. Type `claude --version` and press Enter — you should see a version number

---

## Part 2 — Download the Project

---

### Step 6 — Download the Code

1. Decide where you want the project to live. A simple location is your Desktop or a folder like `C:\AIJobs`
2. Press `Windows key + R`, type `cmd`, press Enter
3. Navigate to where you want the folder. For example, to put it on your Desktop:
   ```
   cd %USERPROFILE%\Desktop
   ```
4. Run this command to download the project:
   ```
   git clone https://github.com/vivekshekharrai-del/AIApplyJobs.git
   ```
5. A new folder called **AIApplyJobs** will appear. This is your project folder.
6. Type this to enter the folder:
   ```
   cd AIApplyJobs
   ```

---

### Step 7 — Set Up the Python Environment

This creates a private Python workspace just for this tool.

Still in the Command Prompt window inside your project folder, run these commands **one at a time**:

```
python -m venv venv
```
```
venv\Scripts\pip install applypilot
```
```
venv\Scripts\pip install --no-deps python-jobspy
```
```
venv\Scripts\pip install pydantic tls-client requests markdownify regex
```

Wait for each one to finish before running the next. This may take 2–3 minutes total.

---

## Part 3 — Configure Your Details

---

### Step 8 — Get a Free AI API Key

The tool uses AI to score and tailor your resume. You need a free API key from Google.

1. Go to: **https://aistudio.google.com/apikey**
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key (it starts with `AIza...`)

**Keep this key somewhere safe — you'll need it in the next step.**

---

### Step 9 — Create Your Settings File (.env)

1. Open your project folder in File Explorer (e.g., `C:\Users\YourName\Desktop\AIApplyJobs`)
2. Right-click inside the folder → **New** → **Text Document**
3. Name it exactly: `.env` (including the dot, no `.txt` at the end)
   - Windows may warn you about changing the extension — click **Yes**
4. Right-click `.env` → **Open with** → **Notepad**
5. Paste this into the file, replacing `YOUR_KEY_HERE` with the key you copied:

```
GEMINI_API_KEY=YOUR_KEY_HERE
LLM_MODEL=gemini-2.0-flash
```

6. Save and close Notepad

---

### Step 10 — Create Your Profile

Your profile tells the tool your personal details to fill into application forms.

1. In your project folder, find the file called **`profile.example.json`**
2. Make a copy of it (right-click → Copy, then right-click → Paste)
3. Rename the copy to exactly: **`profile.json`**
4. Right-click `profile.json` → **Open with** → **Notepad**
5. Fill in your real details, replacing the placeholder values:

| Field | What to put |
|-------|-------------|
| `full_name` | Your full legal name |
| `preferred_name` | What you go by (e.g. "John") |
| `email` | Your email address |
| `phone` | Your phone number |
| `address` | Your street address |
| `city` | Your city |
| `province_state` | Your state (e.g. "TX") |
| `linkedin_url` | Your LinkedIn profile URL |
| `salary_expectation` | Your target salary (numbers only, e.g. "120000") |
| `years_of_experience_total` | Total years of work experience |
| `current_job_title` | Your current or most recent job title |
| `target_role` | The type of role you are looking for |
| `programming_languages` | Your main programming languages |
| `preserved_companies` | Your real employers (the AI will never change these) |
| `preserved_school` | Your real university/college name |

6. Save and close Notepad

---

### Step 11 — Add Your Resume

1. Open your resume in Microsoft Word or Google Docs
2. Select all text (`Ctrl+A`) and copy it (`Ctrl+C`)
3. Open Notepad (search for it in the Start menu)
4. Paste your resume (`Ctrl+V`)
5. Save the file as **`resume.txt`** inside your project folder
   - In Notepad: File → Save As → navigate to your project folder → name it `resume.txt` → Save

---

### Step 12 — Customise Your Job Search

1. In your project folder, open **`searches.yaml`** with Notepad
2. Find the `queries:` section — these are the job titles it will search for
3. Edit the list to match your target roles. For example:
   ```
   - query: "Software Engineer"
     tier: 1
   - query: "Full Stack Developer"
     tier: 1
   ```
4. Find the `locations:` section and update your preferred locations
5. Save and close

---

### Step 13 — Verify Your Setup

Open Command Prompt in your project folder and run:

```
venv\Scripts\applypilot doctor
```

You should see green **OK** next to Claude Code CLI, Chrome/Chromium, and Node.js.
Missing items in red need to be resolved before continuing.

---

## Part 4 — Running the Pipeline

The tool works in stages. Run them in this order. You do **not** have to run all stages every day — see the daily usage guide below.

---

### Stage 1 — Discover Jobs

**What it does:** Searches Indeed and LinkedIn for jobs matching your searches. Can find hundreds of jobs in one run.

**How to run:** Double-click **`run_score.ps1`** in your project folder.

> If Windows asks "How do you want to open this file?" — choose **PowerShell**.
> If it says "Windows protected your PC" — click **More info** → **Run anyway**.

This runs two stages back-to-back (discover → score) and may take 10–30 minutes depending on how many jobs it finds.

When it finishes, you'll see a summary of how many jobs were found and scored.

---

### Stage 2 — View the Dashboard

**What it does:** Opens a visual list of all discovered jobs with their AI scores (1–10), salary, company, and links.

**How to run:**

```
venv\Scripts\python view_jobs.py
```

Or double-click and open in your browser if a file called `jobs_view.html` appears in the folder.

**What to do:**
- Jobs with a score of **7 or higher** are good matches
- Click the **star (☆)** next to any job to approve it for tailoring and applying
- Only star jobs you actually want to apply to

---

### Stage 3 — Tailor Resumes + Cover Letters

**What it does:** The AI rewrites your resume specifically for each starred job, and writes a personalised cover letter. This uses your AI API key.

**Run a test first (1 job only):**
Double-click **`run_tailor_cover_test.ps1`**

Check the output — it should create a tailored resume file in the `tailored_resumes` folder.

**Run for all starred jobs:**
Double-click **`run_tailor_cover.ps1`**

This may take several minutes depending on how many jobs you starred.

---

### Stage 4 — Auto-Apply

**What it does:** Opens Chrome and uses AI to automatically fill in and submit job applications. It reads the tailored resume for each job and handles Workday and other ATS forms.

**IMPORTANT — Read before running:**
- Make sure Chrome is closed before running this
- The tool will open Chrome windows automatically — do not click or use them while it's running
- Watch the first few applications to make sure it's filling things in correctly

**Test run first (1 job, does NOT submit):**
Double-click **`run_apply_test.ps1`**

This is a dry run — it will go through the motions but not actually submit. Review what it did.

**Apply for real (up to 4 jobs at once):**
Double-click **`run_apply_4.ps1`**

---

## Part 5 — Daily Usage

Once set up, your typical daily routine is:

| Step | Action | How often |
|------|--------|-----------|
| 1 | Run `run_score.ps1` to find new jobs | Daily or every 2 days |
| 2 | Open `jobs_view.html` and star good jobs | Daily |
| 3 | Run `run_tailor_cover.ps1` to prepare resumes | After starring jobs |
| 4 | Run `run_apply_4.ps1` to submit applications | After tailoring |

---

## Troubleshooting

**"Windows protected your PC" when running .ps1 files:**
Right-click the file → **Properties** → at the bottom tick **"Unblock"** → OK. Then try again.

**The tool can't find jobs / scraping errors:**
Job boards sometimes block scrapers temporarily. Wait an hour and try again.

**"No jobs ready to apply" error:**
You need to star jobs in the dashboard first (Stage 2), then run tailoring (Stage 3) before applying.

**Chrome opens but closes immediately:**
Make sure Chrome is fully closed before running the apply stage. Check Task Manager (`Ctrl+Shift+Esc`) and end any Chrome processes.

**API errors / rate limit errors:**
Your free Gemini API key has usage limits. Wait 1–2 minutes and try again. If it keeps happening, check your key at `https://aistudio.google.com/apikey`.

**Something looks wrong with the application it filled in:**
The tool logs everything in the `logs` folder. Open `logs\apply_run.log` in Notepad to see what happened.

---

## Important Notes

- **Review applications:** Always check what the tool is doing the first few times. The AI is very good but not perfect.
- **Accuracy:** The tool will never invent work experience or change your real employers and school — it only rephrases and reorganises what's already in your resume.
- **Privacy:** Your resume, profile, and API key are stored only on your computer and are never uploaded anywhere except to the AI API for processing.
- **PDT Rule:** If you are day-trading on the side — unrelated, but worth knowing — accounts under $25,000 have limits on same-day trades.

---

## File Reference

| File | What it is |
|------|-----------|
| `.env` | Your API key (keep private) |
| `profile.json` | Your personal details for applications |
| `resume.txt` | Your base resume |
| `searches.yaml` | Job titles and locations to search |
| `applypilot.db` | The database of all jobs found (do not delete) |
| `tailored_resumes/` | Folder of AI-tailored resumes per job |
| `cover_letters/` | Folder of AI cover letters per job |
| `logs/` | Logs of what happened during apply runs |
| `jobs_view.html` | The job dashboard (open in browser) |

---

*Built on [ApplyPilot](https://github.com/Pickle-Pixel/ApplyPilot) — open source job application automation.*
