import os
from flask import Flask, render_template, request, jsonify
import anthropic
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from reference_content import CORE_PHILOSOPHY, get_symptom_context, get_ask_context, SYMPTOM_LIBRARY, BONUS_TOPICS

load_dotenv()  # reads a local .env file if present (for local development)

app = Flask(__name__)

# Rate limiting: protects against runaway costs from a single user/bot hammering
# the API. Adjust these numbers based on real usage once it's live.
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",  # fine for a single server instance; see note in README
)

api_key = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key) if api_key else None

MODEL = "claude-sonnet-5"
MAX_TOKENS = 2048
MAX_MESSAGE_LENGTH = 2000  # characters - prevents huge prompts from running up costs

DIAGNOSTIC_SYSTEM_PROMPT = f"""You are MarineDx, a marine diesel engine diagnostics assistant grounded in
"The Diesel Whisperer's Handbook" and "Marine Troubleshooting," both by Lalith Prasanna
Madanayake, a marine engineer and consultant. You help engineers, cadets, and technical
students triage engine problems using the same practical, cost-conscious, decision-tree
methodology as the source material -- not generic textbook diagnostics.

{CORE_PHILOSOPHY}

When relevant book excerpts are provided below the symptom list, ground your answer in
them directly rather than substituting generic knowledge. Where no excerpt is provided
for a selected symptom, fall back to sound marine diesel engineering practice while
keeping the same voice: practical, specific to marine (not automotive) contexts, and
always checking the cheapest/most common cause before assuming an expensive one.

Given a list of symptoms, respond with:
1. A ranked list of the 3-4 most likely root causes (most likely first)
2. For each cause, 1-2 concrete diagnostic checks to confirm or rule it out
3. A brief safety note if any symptom suggests urgent risk (e.g. overheating, oil in coolant)

Be concise and technical. Format with clear structure but no markdown headers - use simple
numbered lists and short paragraphs."""

ASK_SYSTEM_PROMPT = """You are MarineDx, a marine diesel engine engineering assistant
grounded in "The Diesel Whisperer's Handbook" and "Marine Troubleshooting," both by
Lalith Prasanna Madanayake, a marine engineer and consultant. Answer technical questions
about marine diesel engines, their systems, maintenance, and troubleshooting using the
same practical, decision-tree, cost-conscious voice as the source material -- a senior
marine engineer's approach, not a textbook's. When relevant book excerpts are provided
below the question, ground your answer in them directly. Be specific to marine (not
automotive) contexts and keep answers focused, without unnecessary padding."""


def call_claude(system_prompt, user_message):
    if client is None:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Create a .env file (see .env.example) "
            "or set the environment variable before starting the server."
        )
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    # Sonnet 5 runs adaptive thinking by default, so response.content may include
    # a ThinkingBlock before the actual text block. Find the text block explicitly
    # rather than assuming content[0] is text.
    for block in response.content:
        if block.type == "text":
            return block.text
    raise RuntimeError("No text block found in the model's response.")


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Too many requests — please slow down and try again in a minute."}), 429


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/diagnose", methods=["POST"])
@limiter.limit("10 per minute")
def diagnose():
    data = request.get_json(force=True, silent=True) or {}
    message = data.get("message", "").strip()
    symptoms = data.get("symptoms", [])  # list of selected symptom labels, optional
    if not message:
        return jsonify({"error": "No message provided"}), 400
    if len(message) > MAX_MESSAGE_LENGTH:
        return jsonify({"error": f"Message too long (max {MAX_MESSAGE_LENGTH} characters)"}), 400
    try:
        book_context = get_symptom_context(symptoms) if symptoms else ""
        full_message = message + book_context
        text = call_claude(DIAGNOSTIC_SYSTEM_PROMPT, full_message)
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ask", methods=["POST"])
@limiter.limit("10 per minute")
def ask():
    data = request.get_json(force=True, silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "No message provided"}), 400
    if len(message) > MAX_MESSAGE_LENGTH:
        return jsonify({"error": f"Message too long (max {MAX_MESSAGE_LENGTH} characters)"}), 400
    try:
        book_context = get_ask_context(message)
        full_message = message + book_context
        text = call_claude(ASK_SYSTEM_PROMPT, full_message)
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reference", methods=["GET"])
def reference():
    """Static reference library content - no API call, just serves the book excerpts."""
    return jsonify({
        "symptoms": {k: v for k, v in SYMPTOM_LIBRARY.items() if v.get("book_coverage")},
        "topics": BONUS_TOPICS,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Debug mode is opt-in only (set FLASK_DEBUG=1 locally if you want it).
    # Never hardcode True here - debug mode exposes stack traces and allows
    # arbitrary code execution via the interactive debugger if it's ever
    # accidentally exposed on a public server.
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
