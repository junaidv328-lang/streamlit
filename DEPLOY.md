# ScalpEdge — Deployment Guide

Step-by-step instructions for deploying to Streamlit Community Cloud.

---

## Pre-flight checklist

You should have these files in your project folder:

```
scalpedge/
├── app.py                     ← main Streamlit app
├── requirements.txt           ← Python dependencies
├── runtime.txt                ← Python version pin
├── .gitignore                 ← prevents credential leaks
├── secrets.toml.template      ← reference, do NOT fill in & commit
└── README.md                  ← (this file, optional)
```

The actual `secrets.toml` lives ONLY in two places:
1. Locally at `.streamlit/secrets.toml` (gitignored) — for local dev
2. Pasted into Streamlit Cloud's Secrets manager — for production

---

## Step 1 — Test locally first

Before pushing to cloud, confirm the app runs locally with the same Python version Streamlit Cloud uses (3.12).

```cmd
py install 3.12
py -3.12 -m pip install -r requirements.txt
py -3.12 -m streamlit run app.py
```

You should see the password gate. Since no `secrets.toml` exists yet, the gate is bypassed automatically — go through Tab 1, log in manually with your SmartAPI creds, confirm everything works.

---

## Step 2 — Set up local secrets (optional but recommended)

Test the secrets flow locally before deploying:

```cmd
mkdir .streamlit
copy secrets.toml.template .streamlit\secrets.toml
notepad .streamlit\secrets.toml
```

Fill in real values, save, then restart the app:
```cmd
py -3.12 -m streamlit run app.py
```

You should now see:
- A password prompt (uses `app_password` from secrets)
- After unlocking, Tab 1 shows "✓ CREDENTIALS LOADED FROM SECRETS" and fields are read-only

---

## Step 3 — Set up Git

If you don't have Git installed, get it from https://git-scm.com/download/win.

```cmd
cd path\to\scalpedge
git init
git add .
git status
```

**CRITICAL — before committing, confirm `git status` does NOT list:**
- `.streamlit/secrets.toml`
- `.scalp_creds.json`

If either shows up, your `.gitignore` isn't working. Stop and fix it.

```cmd
git commit -m "Initial commit: ScalpEdge Brooks live"
```

---

## Step 4 — Push to GitHub

1. Create a new **PRIVATE** repo at https://github.com/new (do NOT make it public).
2. Copy the commands GitHub shows you. They'll look like:

```cmd
git remote add origin https://github.com/YOUR_USERNAME/scalpedge.git
git branch -M main
git push -u origin main
```

3. Refresh the GitHub repo page and verify the file list — **make sure no secrets file is visible.**

---

## Step 5 — Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click **New app**.
3. Fill in:
   - **Repository:** `YOUR_USERNAME/scalpedge`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **Advanced settings** → **Secrets**.
5. Open your local `.streamlit/secrets.toml`, copy ALL contents, paste into the Secrets field.
6. Click **Save**, then **Deploy!**

First deploy takes 3–5 minutes (installing scipy, smartapi-python, etc).

---

## Step 6 — Lock down access

Your app URL will be `https://scalpedge-<random>.streamlit.app`. By default this is publicly reachable — but the password gate from Step 2 blocks anyone without the passphrase.

For extra hardening:

1. **Go to your app's Settings → Sharing.**
2. Set **Viewer access** to **"Only specific people"** and add your own GitHub email.
3. Anyone else hitting the URL will see a Streamlit-level access denied page before they even reach the password gate.

This gives you **two layers**:
- Streamlit-level: GitHub email whitelist
- App-level: password gate from `app_password` secret

---

## Step 7 — Updating the app

Any future changes:

```cmd
git add app.py
git commit -m "describe what changed"
git push
```

Streamlit Cloud auto-redeploys within ~30 seconds of detecting the push.

To update secrets without a code change:
- Streamlit Cloud → your app → ⚙ Settings → Secrets → edit → Save
- App reboots automatically.

---

## Common issues

**"ModuleNotFoundError: smartapi-python"**
→ `requirements.txt` has a typo. Confirm spelling, push fix.

**"Read timed out" on Brooks Live tab**
→ Angel One API is sluggish outside market hours. Use 1-day lookback during off-hours, full lookback during 9:15–15:30 IST.

**"FileNotFoundError: .streamlit/secrets.toml" locally**
→ Either create the file from the template, or just run without it — the app gracefully falls back to manual credential entry when no secrets are present.

**"st.secrets has no attribute 'app_password'"**
→ Your secrets.toml is missing the top-level `app_password` line. Add it above the `[angel_one]` section.

**Login works locally but fails on cloud with "Login error"**
→ Angel One sometimes blocks logins from new IPs. Log in once manually from the cloud's IP range (you'll see a notification on your registered email/phone) before relying on automated TOTP login.

---

## Security checklist before going live

- [ ] `.gitignore` blocks `.streamlit/secrets.toml`
- [ ] `git status` shows no credential files before any commit
- [ ] GitHub repo is set to **Private**
- [ ] `app_password` is strong (16+ characters, mixed)
- [ ] Streamlit Cloud sharing is set to "Only specific people" (yourself)
- [ ] No real credentials are anywhere in `app.py` itself
- [ ] You've revoked any SmartAPI keys that may have leaked previously
