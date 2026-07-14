# MarineDx — Marine Engine Diagnostics Assistant

A Flask web app that gives marine engineers, cadets, and technical students an AI-powered
diagnostic assistant for marine diesel engines, plus a report generator for logging
sessions and exporting them for client/logbook records.

## How it's structured

```
marinedx/
├── app.py                  Flask backend — holds the API key, talks to Claude
├── templates/
│   └── index.html          The whole frontend (UI + JS), single file
├── requirements.txt
├── .env.example             Copy to .env and add your real API key
└── README.md
```

The browser never talks to Anthropic directly — it calls your own `/api/diagnose`
and `/api/ask` endpoints, and Flask makes the actual Claude API call server-side.
This keeps your API key private, which is required for any real deployment
(client-side JavaScript can't safely hold a secret key).

## Running it locally

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Get an API key from https://console.anthropic.com/settings/keys

3. Copy `.env.example` to `.env` and paste your key in:
   ```
   cp .env.example .env
   ```
   Then edit `.env` so it has your real key.

4. Run the server:
   ```
   python app.py
   ```

5. Open http://localhost:5000 in your browser.

## Deploying for real (when you're ready)

This is a standard Flask app, so it deploys the same way most small Flask apps do.
A few solid, low-effort options:

**Render.com** (free tier available, simplest for a first deploy)
- Push this folder to a GitHub repo
- Create a new "Web Service" on Render, point it at the repo
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Add `ANTHROPIC_API_KEY` as an environment variable in Render's dashboard (never commit your .env file)

**Railway.app** — very similar flow to Render, also has a free starter tier.

**Fly.io** — a bit more setup (needs a `Dockerfile` or `fly.toml`), but gives you
more control over region/scaling if you outgrow the free tiers later.

**PythonAnywhere** — good if you want something dead simple with no GitHub step,
though the free tier has some restrictions on outbound requests to external APIs
(worth checking against Anthropic's API before relying on it).

Whichever you choose, the only two things that matter:
1. Set `ANTHROPIC_API_KEY` as a real environment variable on the host — never hardcode it in the code or commit it to git.
2. Make sure `.env` is in your `.gitignore` so it never ends up in a public repo.

## Notes on cost

Every diagnosis or question sent through the app is a real API call billed to
your Anthropic account. For a public-facing tool with external users, you'll
want to think about:
- Rate limiting per user/IP (to avoid one person running up a large bill)
- Possibly a lightweight usage cap or login system before opening it up widely

Happy to help build either of those in when you're ready to go live.
