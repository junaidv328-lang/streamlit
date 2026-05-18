# ScalpEdge — Deployment Guide (with Market Profile tab)

Step-by-step instructions for deploying to Streamlit Community Cloud.

This build adds a **🗂 MARKET PROFILE** tab (TPO profile + day-over-day
value migration). It reuses the candles Tab 1 already fetches — no new
API calls, no new dependencies, no changes to login or Brooks Live.

---

## Pre-flight checklist

Files in your project folder:

```
scalpedge/
├── app.py                     ← main app (Market Profile already integrated)
├── requirements.txt           ← Python dependencies (unchanged)
├── runtime.txt                ← Python version pin (unchanged)
├── .gitignore                 ← prevents credential leaks
├── secrets.toml.template      ← reference, do NOT fill in & commit
└── DEPLOY.md                  ← this file
```

`app.py` is the **fully integrated** version — the Market Profile tab
is already inside it. You do not need to paste anything manually.

The actual `secrets.toml` lives ONLY in two places:
1. Locally at `.streamlit/secrets.toml` (gitignored) — for local dev
2. Pasted into Streamlit Cloud's Secrets manager — for production

---

## Step 1 — Test locally first

```cmd
py install 3.12
py -3.12 -m pip install -r requirements.txt
py -3.12 -m streamlit run app.py
```

You should see the password gate. With no `secrets.toml` yet, the gate
is bypassed — log in manually with your SmartAPI creds in Tab 1,
fetch a multi-day NIFTY range at 1-min, then open the Market Profile
tab and confirm the profile, day regime, and value migration render.

---

## Step 2 — Set up local secrets (optional but recommended)

```cmd
mkdir .streamlit
copy secrets.toml.template .streamlit\secrets.toml
notepad .streamlit\secrets.toml
```

Fill in real values, save, restart:
```cmd
py -3.12 -m streamlit run app.py
```

---

## Step 3 — Set up Git

```cmd
cd path\to\scalpedge
git init
git add .
git status
```

**CRITICAL — confirm `git status` does NOT list:**
- `.streamlit/secrets.toml`
- `.scalp_creds.json`

If either shows up, stop and fix `.gitignore` before committing.

```cmd
git commit -m "ScalpEdge + Market Profile tab"
```

---

## Step 4 — Push to GitHub

1. Create a new **PRIVATE** repo at https://github.com/new
2. Run the commands GitHub shows:

```cmd
git remote add origin https://github.com/YOUR_USERNAME/scalpedge.git
git branch -M main
git push -u origin main
```

3. Verify the GitHub file list — **no secrets file visible.**

---

## Step 5 — Deploy on Streamlit Cloud

1. https://share.streamlit.io → sign in with GitHub
2. **New app**
3. Repository: `YOUR_USERNAME/scalpedge` · Branch: `main` ·
   Main file path: `app.py`
4. **Advanced settings → Secrets**
5. Paste the full contents of your local `.streamlit/secrets.toml`
6. **Save → Deploy!**  (first build 3–5 min)

---

## Step 6 — Lock down access

App URL: `https://scalpedge-<random>.streamlit.app`

For two layers of protection:
1. App **Settings → Sharing** → Viewer access "Only specific people"
   → add your own GitHub email.
2. The `app_password` gate blocks anyone without the passphrase.

---

## Step 7 — Updating

```cmd
git add app.py
git commit -m "describe change"
git push
```

Streamlit Cloud auto-redeploys in ~30 seconds.

---

## Using the Market Profile tab

1. **Tab 1:** fetch a **multi-day** range (the default 7-day works) for
   NIFTY or BANKNIFTY at **1-min or 3-min**. Finer candles = sharper
   TPO rows. Value migration needs ≥ 2 sessions of data.
2. **Market Profile tab:**
   - Pick the session, TPO period (30 = classic), and row size
     (~5 NIFTY, ~10 BANKNIFTY).
   - **Value Migration card** = the day-over-day directional tell
     (overlapping-to-higher = bullish acceptance, etc).
   - **Day Regime card** = is today option-buyable or a theta trap.
   - TPO chart shows POC (blue), value area (light blue), IB lines.

**Decision order:** Value migration → Day regime → Brooks trigger →
Greeks (strike). Each tab does one job.

---

## Common issues

**"Read timed out" on Brooks Live tab**
→ Angel One API is sluggish off-hours. Use 1-day lookback off-hours.

**Market Profile tab says "NO DATA LOADED"**
→ You haven't fetched in Tab 1 yet this session. Fetch first.

**"VALUE MIGRATION — need a prior session"**
→ Single-day fetch. Widen the date range in Tab 1.

**Profile rows look too coarse/fine**
→ Adjust "Row size (pts)". Smaller = more rows, more detail.

**"Login works locally but fails on cloud"**
→ Angel One may block new IPs. Log in once manually from the cloud IP
   range (you'll get an email/SMS) before relying on TOTP.

---

## Security checklist before going live

- [ ] `.gitignore` blocks `.streamlit/secrets.toml`
- [ ] `git status` shows no credential files before any commit
- [ ] GitHub repo is **Private**
- [ ] `app_password` is strong (16+ chars, mixed)
- [ ] Streamlit Cloud sharing = "Only specific people" (yourself)
- [ ] No real credentials anywhere in `app.py`
- [ ] Any previously leaked SmartAPI keys are revoked
