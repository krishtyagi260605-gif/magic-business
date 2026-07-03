# Deployment & Hosting Guide: Render + Uptime Robot

This guide provides step-by-step instructions for deploying the **Magic Business Platform** on [Render](https://render.com) using **GitHub** and keeping it active using **Uptime Robot**.

---

## Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Step 1: Set Up GitHub Repository](#step-1-set-up-github-repository)
3. [Step 2: Deploy to Render](#step-2-deploy-to-render)
   - [Option A: Deploy via Blueprint (Recommended)](#option-a-deploy-via-blueprint-recommended)
   - [Option B: Manual Web Service Deployment](#option-b-manual-web-service-deployment)
4. [Step 3: Keep Service Awake with Uptime Robot](#step-3-keep-service-awake-with-uptime-robot)
5. [Important Free-Tier Limitations (Ephemeral Storage)](#important-free-tier-limitations-ephemeral-storage)

---

## 1. Prerequisites
- A GitHub account.
- A Render account (free tier works perfectly).
- An Uptime Robot account (free tier works perfectly).
- API Keys for Google Gemini and/or Groq.

---

## 2. Step 1: Set Up GitHub Repository
Render deploys code directly from GitHub. You need to push your local code to a GitHub repository first:

1. **Initialize a Git repository** in your project folder (if not already done):
   ```bash
   git init
   ```
2. **Add a `.gitignore`** to avoid committing sensitive files:
   Create a `.gitignore` file and add the following lines:
   ```text
   .env
   __pycache__/
   output/
   *.zip
   .DS_Store
   ```
3. **Commit your files**:
   ```bash
   git add .
   git commit -m "Initial commit for Render deployment"
   ```
4. **Create a new repository** on GitHub (keep it Private if you want to keep your code private).
5. **Link and push** to your GitHub repository:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

---

## 3. Step 2: Deploy to Render

### Option A: Deploy via Blueprint (Recommended & Easiest)
We have included a `render.yaml` Blueprint file in the repository. This file pre-configures the build command, start command, and environment variables automatically.

1. Go to your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** in the top right and select **Blueprint**.
3. Connect your GitHub repository.
4. Render will parse the `render.yaml` file. Review the service name and environment variables.
5. Provide your API keys under the variable fields:
   - `GEMINI_API_KEY`: Your Google Gemini API Key.
   - `GROQ_API_KEY`: Your Groq API Key (if using Groq).
6. Click **Apply**. Render will automatically build and deploy your application.

---

### Option B: Manual Web Service Deployment
If you prefer to configure the service manually through the Render UI:

1. Go to the [Render Dashboard](https://dashboard.render.com).
2. Click **New +** and select **Web Service**.
3. Select **Build and deploy from a Git repository**, connect your repository, and click **Next**.
4. Configure the following fields:
   - **Name**: `magic-business-platform`
   - **Region**: Select the region closest to you.
   - **Branch**: `main`
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Scroll down to **Environment Variables** and click **Add Environment Variable**:
   - `GEMINI_API_KEY` = `your_gemini_key_here`
   - `GROQ_API_KEY` = `your_groq_key_here`
   - `HOST` = `0.0.0.0`
6. Choose the **Free** instance type.
7. Click **Create Web Service**.

---

## 4. Step 3: Keep Service Awake with Uptime Robot
Render’s Free Tier automatically spins down (goes to sleep) your application after **15 minutes of inactivity**. The next request can take 50 seconds or longer to respond while it wakes up.

To prevent this sleep cycle, use **Uptime Robot** to ping the application's health check endpoint every 5-10 minutes.

1. Once the deployment on Render is successful, copy your web service URL (e.g., `https://magic-business-platform.onrender.com`).
2. Log in to your [Uptime Robot Dashboard](https://uptimerobot.com).
3. Click **Add New Monitor**.
4. Configure the monitor details:
   - **Monitor Type**: `HTTP(s)`
   - **Friendly Name**: `Magic Business Health`
   - **URL (or IP)**: Paste your Render URL with the health endpoint:
     `https://YOUR_SERVICE_NAME.onrender.com/api/health`
   - **Monitoring Interval**: Every `5 minutes` (or `10 minutes`).
5. Click **Create Monitor**.
6. Uptime Robot will now send a ping to `/api/health` regularly, keeping the Render instance continuously active.

---

## 5. Important Free-Tier Limitations (Ephemeral Storage)
> [!WARNING]
> **Ephemeral Filesystem Alert**
> Render’s free tier uses an **ephemeral disk**. 
> - Any files generated and saved locally (under the `output/` session folders, like logos, letterheads, and PDFs) will be **deleted** whenever the service restarts, spins down, or redeploys.
> - This is perfectly fine for downloading assets immediately after generation, but those assets will not remain hosted on the server forever.
> - **Recommendation**: If you need permanent file storage or want users to access their past generation packages days later, we recommend modifying the file saving utility to upload files directly to cloud storage (e.g., Supabase Storage, AWS S3, or Cloudinary).
