# F Block Allotment Register — Full-Stack Version

A real, standalone web app version of the register: Flask backend, SQLite
database file, plain HTML/CSS/JS frontend. No Claude account or artifact
needed to use it — runs as an ordinary website.

## What's inside

```
webapp/
├── app.py            Flask backend (2 routes: GET/POST /api/state)
├── requirements.txt  Python dependencies
├── Procfile          Start command for Render/Railway/Heroku-style hosts
├── seed_data.json    Initial data (your current register, used only once
│                      to populate the database the first time it runs)
├── fblock.db          <- created automatically on first run (SQLite database)
└── static/
    └── index.html    The entire frontend (same interface you've been using)
```

## How it works

- All data lives in **one SQLite database file** (`fblock.db`), created
  automatically the first time the server starts.
- The frontend calls two endpoints:
  - `GET /api/state` — loads the full register (flats, rooms, occupants, activity log)
  - `POST /api/state` — saves it back after every allot/unallot/edit
- Whoever is "signed in" (Dr. Ankit / Dr. Utkarsh / Sagar) is remembered
  per-browser using the browser's own storage — each person only has to
  pick their name once on their own computer/phone.
- Everyone who opens the site sees the same live data, since it all comes
  from the one shared database file on the server.

## Run it on your own computer first (5 minutes)

You'll need Python 3 installed.

```bash
cd webapp
pip install -r requirements.txt
python app.py
```

Then open **http://localhost:5000** in your browser. That's the whole app,
running locally — nobody outside your computer can see it yet.

## Put it online so the office can reach it

The easiest free option is **Render** (render.com):

1. Create a free Render account, click **New → Web Service**.
2. Connect it to a GitHub repo containing this `webapp` folder (or use
   Render's "deploy without Git" file upload if you don't want to set up
   GitHub — either works).
3. Settings:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
4. Click deploy. Render gives you a URL like
   `https://f-block-register.onrender.com` — that's your real, public
   web portal. Share that link with your logistics office.

**Railway** (railway.app) works almost identically if you prefer it.

### Important: about the database persisting

Free tiers on most hosts (including Render's free plan) use a filesystem
that gets **wiped on redeploy or after periods of inactivity**. That means
`fblock.db` — and everything your office has entered — could reset back to
`seed_data.json` unexpectedly.

For anything beyond testing, you have two solid options:
1. **Render's paid tier** ($7/mo as of writing) supports a "Persistent Disk"
   — `fblock.db` survives restarts and redeploys.
2. **Switch to a hosted database** — Render and Railway both offer a free
   Postgres add-on. The code change is small (swap the `sqlite3` calls in
   `app.py` for a Postgres connection) — ask me and I'll make that version
   if you'd rather not risk data loss on a free tier.

If GIMS has its own server or IT department, running this on that server
(with a normal disk, not a free ephemeral one) sidesteps this issue
entirely — that's the most reliable option if it's available to you.

## Resetting the data

If you ever want to wipe the live database back to the original register,
send a POST request to `/api/reset` (e.g. from a terminal:
`curl -X POST https://your-url/api/reset`). There's no undo for this one —
it's a hard reset, not the in-app Undo button.

## What's different from the Claude artifact version

- No Claude account needed to use it — it's a normal website.
- Real database file instead of Claude's storage system.
- Same interface, same features (allotment, sharing, activity log, undo,
  gender tags, comments, floor plans, block map) — nothing was removed.
- You now own and control the hosting, so you can add proper logins,
  backups, or anything else later — just ask.
