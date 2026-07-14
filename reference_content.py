"""
Reference content extracted from:
- "The Diesel Whisperer's Handbook" by Lalith Prasanna Madanayake
- "Marine Troubleshooting" by Lalith Prasanna Madanayake

This is used two ways:
1. Injected as grounding context into the Claude system prompt for /api/diagnose
   and /api/ask, so answers reflect the book's actual methodology and voice
   rather than generic AI knowledge.
2. Served directly to the frontend Reference Library tab, so users can browse
   this content without triggering an API call at all.
"""

# Core diagnostic philosophy from the book (Ch. 2) - always included as base
# grounding, regardless of which symptoms are selected. This anchors tone and
# method even for chapters/symptoms without a dedicated entry below.
CORE_PHILOSOPHY = """Core diagnostic philosophy (from Ch. 2, "Your Engine Has Already Told You What's Wrong"):

Modern ECUs follow a "protect the asset first, ask questions later" approach. When a
sensor reading falls outside its expected range, the ECU de-rates power, caps RPM, or
forces a shutdown -- commonly called "limp mode." This is a protective feature, not a
failure: it exists so a cheap sensor fault doesn't turn into a catastrophic mechanical
failure. The right response to a symptom is not panic, but finding out what triggered
the protection.

Diagnostic method: organize each complaint as a decision tree -- a symptom at the top,
a branching series of yes/no checks that narrow the list of likely causes before any
tool is picked up. Always check the cheapest, most common possibility first (a stored
fault code, a loose connector, fouled running gear) before assuming an expensive
mechanical cause. Note whether a fault correlates with RPM, load, temperature, sea
state, or time since last refueling -- correlation is often the fastest route to root
cause on an intermittent fault."""


# Maps the frontend's data-sym symptom labels to book content. Symptoms without a
# dedicated chapter are marked book_coverage=False and rely on the core philosophy
# plus general marine engineering knowledge.
SYMPTOM_LIBRARY = {
    "Black exhaust smoke": {
        "book_coverage": True,
        "chapter": "Ch. 7 — Black Smoke, White Smoke, Blue Smoke",
        "content": """Black smoke that appears specifically under acceleration and clears at
steady RPM usually points to a temporary air/fuel imbalance -- often a boost pressure
sensor under-reporting versus the turbo's real output, or a turbo responding slowly
(spool lag) that has worsened over time. Check for a stored boost/manifold pressure
fault code first. If none, inspect intake and charge-air piping for cracks or loose
clamps, which can cause a real boost drop invisible to a sensor mounted upstream of
the leak.""",
    },
    "Blue exhaust smoke": {
        "book_coverage": True,
        "chapter": "Ch. 7 — Black Smoke, White Smoke, Blue Smoke",
        "content": """Blue smoke, especially on deceleration or right after idle, generally
points toward oil being drawn into the combustion process -- valve seals or piston
rings on older engines, though on newer common-rail engines it can occasionally be
linked to a turbocharger seal issue rather than internal engine wear. Cross-check
against Ch. 12: a rising-pitch whine under acceleration alongside blue smoke points
more strongly toward a turbo shaft seal than internal wear.""",
    },
    "White exhaust smoke": {
        "book_coverage": True,
        "chapter": "Ch. 7 — Black Smoke, White Smoke, Blue Smoke",
        "content": """White smoke at startup that clears within a minute or two is usually
simple: unburned fuel vapor before the engine reaches operating temperature. White
smoke that persists, especially with a sweet smell, deserves an immediate coolant
check -- this combination can indicate coolant entering the combustion chamber, a
significantly more serious concern that should stop further running until inspected.""",
    },
    "Excessive vibration": {
        "book_coverage": True,
        "chapter": "Ch. 16 — Vibration, Alignment & Mounting-Related Faults",
        "content": """Excess vibration -- from worn engine mounts, a misaligned shaft, or an
out-of-balance propeller -- doesn't just feel unpleasant. It physically stresses
wiring harnesses and connector pins at a frequency that can intermittently interrupt
sensor signals, producing hard-to-reproduce electronic faults. Check: does the symptom
correlate with a specific, narrow RPM band (points to resonance/prop balance/shaft
alignment)? Have mounts been inspected recently? Was there a recent grounding or hard
impact that could have shifted alignment without visible damage? Field check: at idle
in neutral, a visibly excessive shake at the mounts (more than a light, even hum)
warrants inspection before it starts generating harness-related electronic faults
elsewhere.""",
    },
    "Knocking noise": {
        "book_coverage": True,
        "chapter": "Ch. 18 — Unusual Noises: Knocking, Whining & Rattling Decoded",
        "content": """A rhythmic knock that scales in frequency with RPM, most noticeable at
idle and lessening under load, often points toward injector timing or a specific
cylinder's combustion event rather than a bottom-end mechanical issue -- a stored
fault code will often confirm which cylinder. A rattle appearing only in the first few
seconds after cold start and disappearing once oil pressure builds is common and
usually benign, but worth flagging to a technician if it starts lingering longer than
it used to.""",
    },
    "Whining noise": {
        "book_coverage": True,
        "chapter": "Ch. 18 — Unusual Noises / Ch. 12 — Turbocharger Faults",
        "content": """A rising-pitch whine under acceleration is the classic early turbo
bearing wear signature (Ch. 12) -- often present well before any fault code appears.
A steady, high-pitched whine present at all RPMs, including idle, more often points to
a power steering, hydraulic, or accessory drive component than the engine itself.
Mechanical turbo check: with the engine off, gently rock the compressor wheel by hand
-- play in the shaft is a late-stage sign that should not be ignored.""",
    },
    "Loss of power": {
        "book_coverage": True,
        "chapter": "Ch. 8 — The Power Loss That Comes and Goes",
        "content": """An intermittent power loss is harder to diagnose than a constant one
precisely because it vanishes right when you want to catch it in the act -- a
connector corroded just enough to fail only under vibration, heat, or a specific RPM
range will often test fine at the dock. Correlate against: sea state/vibration (points
to connector/harness fault), fuel level (points to fuel pickup or partially clogged
filter, especially below a quarter tank), engine temperature (points to a
heat-sensitive sensor or wiring fault that opens once components expand), or a fixed
RPM every time (points to resonance-related connector issue or a genuine, consistently
flagged mechanical limit). A written log with exact conditions at the time of failure
is the single most powerful tool against this category of fault.""",
    },
    "Hard starting": {
        "book_coverage": True,
        "chapter": "Ch. 6 — Won't Start When Warm: The Diesel's Cruelest Trick",
        "content": """On electronically controlled diesels, warm starting can be harder than
cold starting -- warm fuel is thinner, more prone to vapor formation, and less
forgiving of small air leaks on the suction side. Decision tree: Does the engine crank
at full speed but fail to catch? (If cranking is sluggish, suspect battery/electrical
first, not fuel/ECU.) If cranking is normal, is there a stored or active fault code?
Retrieve it before anything else. If no code: check for air introduction into the fuel
system (a loose primer bulb fitting or a filter housing o-ring that seals cold but
weeps slightly once fuel expands with heat is a very common cause). Also check whether
glow plug cycling is intentionally skipped above a coolant temperature threshold on
your engine, or whether a fuel temperature sensor is giving an implausible reading and
causing the ECU to miscalculate start injection timing.""",
    },
    "Hunting / surging RPM": {
        "book_coverage": True,
        "chapter": "Ch. 9 — The RPM Ceiling",
        "content": """Before touching any sensor, rule out mechanical drag: a fouled
propeller, a partially closed seacock restricting raw water flow (can trigger a
temperature-based de-rate), or marine growth on running gear -- especially on a vessel
that hasn't moved in weeks. Decision tree: Has the boat been sitting for an extended
period? Check running gear and hull first. Is there a boost pressure fault code? A
turbo under-producing boost causes the ECU to proactively limit fuel to avoid excess
exhaust gas temperature -- this shows as a hard ceiling, not a gradual loss. Is there
elevated exhaust back-pressure? A partially blocked exhaust elbow/riser (common with
delayed impeller service) causes a protective de-rate. Is fuel rail pressure below
spec under load? On common-rail systems this triggers a deliberate, safe RPM cap
rather than allowing uneven injection.""",
    },
    "Overheating": {
        "book_coverage": True,
        "chapter": "Ch. 11 — Overheating and the Cooling System's Hidden Language",
        "content": """Read the pattern, not just the number. Overheating only at high RPM/load
points to raw-water flow restriction (blocked strainer, failing impeller, scale in the
heat exchanger). Overheating at idle that resolves under load often points to a
thermostat stuck partially closed or a recirculation issue. A slow drift across a
season is the classic signature of heat exchanger fouling from mineral/salt buildup.
Sudden, sharp overheating with a coolant level drop is a genuine emergency (burst
hose, failed gasket, water pump seal) -- not a sensor issue. Always confirm raw water
discharge at the exhaust first; a weak or absent stream points at the intake side
(strainer, seacock, impeller) before assuming a costlier closed-loop fault. SAFETY:
per Ch. 10's core protocol, oil pressure alarms are immediate shutdown situations
without exception; coolant temperature alarms allow a brief window to reduce RPM and
assess before a full shutdown decision.""",
    },
}


# Additional book content not tied to a specific symptom chip in the current UI,
# but valuable for the open-ended "Ask" tab and the Reference Library.
BONUS_TOPICS = {
    "Fault codes & limp mode": {
        "chapter": "Ch. 2 — Your Engine Has Already Told You What's Wrong",
        "content": CORE_PHILOSOPHY,
    },
    "Turbocharger & boost faults": {
        "chapter": "Ch. 12 — Turbocharger and Boost Pressure Faults",
        "content": """A turbo is one of the few still-primarily-mechanical components on a
modern marine diesel -- a shaft spinning at extraordinary speed on a thin oil film --
even as everything around it has gone electronic. Mechanical failure signature: a
whining/rising-pitch whistle under acceleration that wasn't there before (early
bearing wear, often before any code appears); visible oil in intake piping or
excessive blue-tinted smoke under boost (failing shaft seal); felt play in the shaft
with the engine off (late-stage, should not be ignored). Sensor-driven signature: a
boost pressure sensor reading persistently low/erratic causes proactive under-fueling
-- sluggish acceleration and a hard RPM ceiling even with a healthy turbo; a
wastegate/VGT actuator fault can cause boost to overshoot or undershoot.""",
    },
    "Fuel contamination & filtration": {
        "chapter": "Ch. 13 — Fuel Contamination, Water-in-Fuel & Filtration Faults",
        "content": """Common-rail injectors operate with micron-level clearances and rely on
fuel itself for lubrication -- water, microbial growth ("diesel bug"), or fine
particulate that an older mechanical pump would tolerate can cause rapid injector wear
or immediate misfire codes on an electronic system. Decision tree: Is there a
water-in-fuel sensor alarm? Act immediately -- drain the water separator bowl. Does
the fault correlate with rough weather or a recent refueling? Both agitate tank
sediment. Is there a filter restriction code without a water alarm? Suspect microbial
growth/particulate -- inspect the element for black, sludgy residue. Does performance
degrade gradually over hours then partially recover after shutdown? Points to fuel
starvation from a clogging filter. Prevention: biocide treatment at each fill in humid
climates, keep tanks full during layup, replace filters on schedule without
exception.""",
    },
    "Alarms: false positive vs. real danger": {
        "chapter": "Ch. 10 — When the Alarm Won't Shut Up",
        "content": """Core safety protocol: identify which system triggered the alarm before
doing anything else -- oil pressure, coolant temperature, and exhaust gas temperature
alarms carry very different urgency than a generic fault indicator. Oil pressure
alarms = immediate shutdown, without exception. Coolant temperature alarms allow a
brief window to reduce RPM and assess (raw water flow, steam, smell) before a full
shutdown decision. Generic ECU fault alarms without an accompanying temperature or
pressure warning frequently allow continued, reduced-power operation back to a safe
harbor -- this is what limp mode is designed for. Cross-check: does the alarm
correlate with an independently verifiable physical symptom (steam, smell, sound
change, reduced raw water discharge)? A sensor-only fault with no corroborating
physical sign is more likely a false positive worth nursing home carefully; a fault
WITH a real physical symptom should always be treated as genuine.""",
    },
    "Transmission, shaft & pod faults": {
        "chapter": "Ch. 17 — Transmission, Shaft & Pod Interface Faults",
        "content": """On integrated pod drives, steering, trim, and propulsion share a single
electronic backbone, so a transmission-side fault can appear on the same display,
using similar code formatting, as an engine fault. Check: does the fault code's
manufacturer prefix/numbering fall inside or outside the engine's known code range?
Does the symptom appear only during shifting/docking rather than steady cruising RPM?
Is there a new delay or clunk shifting from neutral into gear? A useful habit: note
whether the symptom persists with the transmission in neutral at the same RPM -- if
so, the engine is the more likely source; if it only appears in gear or under load,
look at the transmission/shaft/pod interface first.""",
    },
}


def get_symptom_context(selected_symptoms):
    """Given a list of symptom strings (matching frontend data-sym values),
    return concatenated book excerpts for any that have dedicated coverage,
    plus a note about any that don't."""
    covered = []
    uncovered = []
    for sym in selected_symptoms:
        entry = SYMPTOM_LIBRARY.get(sym)
        if entry and entry.get("book_coverage"):
            covered.append(f"[{entry['chapter']}]\n{entry['content']}")
        else:
            uncovered.append(sym)

    context = ""
    if covered:
        context += "\n\n---\nRelevant excerpts from the reference handbook:\n\n" + "\n\n".join(covered)
    if uncovered:
        context += (
            f"\n\n(Note: {', '.join(uncovered)} do not have a dedicated chapter in the "
            "source material -- use general marine diesel engineering knowledge for these, "
            "but keep the same practical, cost-conscious, decision-tree voice.)"
        )
    return context


def get_ask_context(user_message):
    """Simple keyword match against symptom and bonus topic titles/chapters to
    find relevant book context for an open-ended question."""
    message_lower = user_message.lower()
    matches = []

    all_topics = {**SYMPTOM_LIBRARY, **BONUS_TOPICS}
    for key, entry in all_topics.items():
        if not entry.get("book_coverage", True):
            continue
        keywords = key.lower().split() + entry["chapter"].lower().split()
        if any(kw in message_lower for kw in keywords if len(kw) > 3):
            matches.append(f"[{entry['chapter']}]\n{entry['content']}")

    if matches:
        return "\n\n---\nRelevant excerpts from the reference handbook:\n\n" + "\n\n".join(matches[:2])
    return ""
