import streamlit as st
import json
from datetime import date,timedelta
import os
import dateparser
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
import streamlit.components.v1 as components
import calendar



# ------------------ CONFIG ------------------
DATA_FILE = "data/user_memory.json"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ------------------ AI HELPERS ------------------


def generate_ai_text(event_text, behavior, pattern):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful calendar assistant."},
            {
                "role": "user",
                "content": f"""
User behavior pattern: {pattern['pattern']}
AI instruction: {pattern['instruction']}

Rewrite the following task in a {pattern['tone']} tone.
Make it realistic, motivating, and behavior-aware.


Task:
"{event_text}"

Format:
Title: ...
Description: ...
"""
            }
        ],
        temperature=0.3,
        max_tokens=200
    )
    content = response.choices[0].message.content.strip()
    title = "Untitled Task"
    description = content
    if "Title:" in content and "Description:" in content:
        title = content.split("Title:")[1].split("Description:")[0].strip()
        description = content.split("Description:")[1].strip()
    return title, description

# ------------------ DATA HELPERS ------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "events": [],
            "user_behavior": {
                "tasks_completed": 0,
                "tasks_missed": 0,
                "preferred_input": "text",
                "reminder_style": "normal"
            },
            "activity_log": []
        }
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def analyze_behavior(data):
    completed = data["user_behavior"]["tasks_completed"]
    missed = data["user_behavior"]["tasks_missed"]
    if missed > completed:
        return {
            "tone": "strict",
            "message": "⚠️ You often miss deadlines. Let's start earlier next time.",
            "reminder_shift": "earlier"
        }
    elif completed >= missed and completed > 0:
        return {
            "tone": "positive",
            "message": "🎉 You're doing great! Keep up the momentum.",
            "reminder_shift": "normal"
        }
    else:
        return {
            "tone": "neutral",
            "message": "📌 Let's build consistency together.",
            "reminder_shift": "normal"
        }
def analyze_recent_pattern(data, window=5):
    logs = data.get("activity_log", [])[-window:]

    completed = sum(1 for l in logs if l["action"] == "task_completed")
    missed = sum(1 for l in logs if l["action"] == "task_missed")

    if missed >= 3:
        return {
            "pattern": "frequent_miss",
            "tone": "firm but supportive",
            "instruction": "Reduce pressure, break task into smaller steps."
        }

    if completed == 0 and missed == 0:
        return {
        "pattern": "new_user",
        "tone": "friendly and exploratory",
        "instruction": "Help the user plan gently without assumptions."
    }


    return {
        "pattern": "unstable",
        "tone": "calm and practical",
        "instruction": "Focus on clarity and realistic planning."
    }


# ------------------ STREAMLIT UI ------------------

st.set_page_config(page_title="Memory-Aware Calendar AI", layout="centered")
st.title("📅 Memory-Aware Calendar AI")
st.caption("A behavioral planning companion")

# Load data and analyze behavior
data = load_data()
behavior_feedback = analyze_behavior(data)

pattern_feedback = analyze_recent_pattern(data)

if "show_behavior" not in st.session_state:
    st.session_state.show_behavior = False

if st.button("🔮 Predict my behaviour"):
    st.session_state.show_behavior = not st.session_state.show_behavior

if st.session_state.show_behavior:
    behavior_feedback = analyze_behavior(data)
    pattern_feedback = analyze_recent_pattern(data)

    st.info(f"🧠 Memory Insight: {behavior_feedback['message']}")
    st.success(
        f"🤖 AI will respond in a **{pattern_feedback['tone']}** tone"
    )



# Calendar
selected_date = st.date_input("Choose a date", date.today(), label_visibility="collapsed")
selected_date_str = str(selected_date)
def extract_date(text):
    parsed = dateparser.parse(text, settings={"PREFER_DATES_FROM": "future"})
    if parsed:
        if parsed.year == date.today().year:
            parsed = parsed.replace(year=2026)
        return parsed.date().isoformat()
    return None

today = selected_date
day = today.day
days_in_month = calendar.monthrange(today.year, today.month)[1]

has_event_today = any(
    e["deadline"] == str(today) for e in data["events"]
)


import math
year = selected_date.year
month = selected_date.month
day = selected_date.day
days_in_month = calendar.monthrange(year, month)[1]

date_marks = ""

for i in range(1, days_in_month + 1):
    angle = (i / days_in_month) * 2 * math.pi - math.pi / 2
    x = 150 + 110 * math.cos(angle)
    y = 150 + 110 * math.sin(angle)

    date_str = f"{year}-{month:02d}-{i:02d}"

    has_event = any(e["deadline"] == date_str for e in data["events"])
    is_today = i == day

    color = "#4caf50" if has_event else "#ff5722" if is_today else "#555"

    date_marks += f"""
    <g onclick="selectDate('{date_str}')" style="cursor:pointer">
        <circle cx="{x}" cy="{y}" r="14" fill="{color}" opacity="0.9"/>
        <text x="{x}" y="{y+5}" text-anchor="middle"
              font-size="12" fill="white" font-weight="bold">{i}</text>
    </g>
    """
if "clicked_date" not in st.session_state:
    st.session_state.clicked_date = str(selected_date)

hidden_date = st.text_input(
    "hidden_date",
    value=st.session_state.clicked_date,
    label_visibility="collapsed",
    key="hidden_date_input"
)

if hidden_date:
    selected_date = date.fromisoformat(hidden_date)
    selected_date_str = str(selected_date)
prev_month_date = selected_date.replace(day=1) - timedelta(days=1)
next_month_date = (
    selected_date.replace(day=days_in_month) + timedelta(days=1)
)

components.html(
f"""
<script>
function selectDate(dateStr) {{
    const input = window.parent.document.querySelector(
        'input[data-testid="stTextInput"]'
    );
    input.value = dateStr;
    input.dispatchEvent(new Event("input", {{ bubbles: true }}));
}}
</script>

<svg width="300" height="300" viewBox="0 0 300 300">

    <!-- Outer circle -->
    <circle cx="150" cy="150" r="130"
        stroke="#ddd" stroke-width="4" fill="none"/>

    <!-- Dates -->
    {date_marks}

    <!-- Center Month -->
    <text x="150" y="145" text-anchor="middle"
        font-size="18" font-weight="bold">
        {selected_date.strftime('%B')}
    </text>

    <!-- Center Year -->
    <text x="150" y="170" text-anchor="middle"
        font-size="14" fill="#666">
        {year}
    </text>
    
    <!-- Month Navigation -->
    
<text x="110" y="170" font-size="18" cursor="pointer"
    onclick="selectDate('{prev_month_date.isoformat()}')">
    ⬅
</text>

<text x="190" y="170" font-size="18" cursor="pointer"
    onclick="selectDate('{next_month_date.isoformat()}')">
    ➡
</text>


</svg>
""",
height=320
)

events_today = [e for e in data["events"] if e["deadline"] == selected_date_str]
if events_today:
    st.success(f"📌 {len(events_today)} event(s) on this day")
else:
    st.info("No events scheduled for this day")

# Initialize session state for unified input
if "plan_input" not in st.session_state:
    st.session_state.plan_input = ""

st.subheader("✍️ Plan something")
st.session_state.plan_input = st.text_area(
    label="Plan input",
    value=st.session_state.plan_input,
    height=120,
    placeholder="Finish AI report tomorrow, revise DBMS on Friday...",
    label_visibility="collapsed"
)


# Voice + text input component
components.html("""
<script>
const interval = setInterval(() => {
    const textareas = window.parent.document.querySelectorAll("textarea");
    if (!textareas.length) return;

    const textarea = textareas[textareas.length - 1];
    clearInterval(interval);

    textarea.parentElement.style.position = "relative";

    const micBtn = document.createElement("button");
    micBtn.innerHTML = "🎤";
    micBtn.style.position = "absolute";
    micBtn.style.right = "12px";
    micBtn.style.top = "12px";
    micBtn.style.fontSize = "20px";
    micBtn.style.border = "none";
    micBtn.style.background = "transparent";
    micBtn.style.cursor = "pointer";
    micBtn.title = "Speak";

    textarea.parentElement.appendChild(micBtn);

    let recognition;
    let listening = false;

    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            micBtn.innerHTML = "⏹️";
        };

        recognition.onend = () => {
            micBtn.innerHTML = "🎤";
            listening = false;
            textarea.dispatchEvent(new Event("input", { bubbles: true }));
        };

        let finalTranscript = "";

        recognition.onresult = (event) => {
            let interimTranscript = "";

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;

                if (event.results[i].isFinal) {
                    finalTranscript += transcript + " ";
                } else {
                    interimTranscript += transcript;
                }
            }

            textarea.value = finalTranscript + interimTranscript;

        };


        micBtn.onclick = () => {
            if (!listening) {
                recognition.start();
                listening = true;
            } else {
                recognition.stop();
            }
        };
    } else {
        micBtn.innerHTML = "❌";
        micBtn.title = "Speech not supported";
    }
}, 300);
</script>
""", height=0)



# ------------------ SAVE PLAN ------------------
if st.button("Save Plan"):
    user_input = st.session_state.plan_input.strip()
    
    if not user_input:
        st.warning("Please write something to plan.")
    else:
        with st.spinner("⚡ Planning instantly with AI..."):
            try:
                pattern_feedback = analyze_recent_pattern(data)
                title, description = generate_ai_text(
                    user_input,
                    behavior_feedback,
                    pattern_feedback
                )

            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()

        deadline = extract_date(user_input) or selected_date_str
        new_event = {
            "title": title,
            "description": description,
            "deadline": deadline,
            "status": "pending"
        }
        data["events"].append(new_event)
        data["activity_log"].append({"action": "event_added", "date": str(date.today())})
        save_data(data)

        st.success(f"🗓️ Event scheduled on {deadline}")
        st.info(f"🤖 AI Plan:\n\n{description}")

        # Clear input after save
        st.session_state.plan_input = ""

# ------------------ DISPLAY EVENTS ------------------
st.divider()
st.subheader("📌 Your Events")

filtered_events = [(idx, e) for idx, e in enumerate(data["events"]) if e["deadline"] == selected_date_str]

if filtered_events:
    for idx, event in filtered_events:
        st.markdown(f"### {event['title']}")
        st.write(event["description"])
        st.write(f"📅 Deadline: {event['deadline']}")
        col1, col2, col3 = st.columns(3)
        if col1.button("✅ Done", key=f"done_{idx}"):
            event["status"] = "completed"
            data["user_behavior"]["tasks_completed"] += 1
            data["activity_log"].append({
                "action": "task_completed",
                "date": str(date.today())
            })

            save_data(data)
        if col2.button("❌ Missed", key=f"missed_{idx}"):
            event["status"] = "missed"
            data["user_behavior"]["tasks_missed"] += 1
            data["activity_log"].append({
                "action": "task_missed",
                "date": str(date.today())
            })

            save_data(data)
        if col3.button("🗑️ Delete", key=f"delete_{idx}"):
            del data["events"][idx]
            data["activity_log"].append({"action": "event_deleted", "date": str(date.today())})
            save_data(data)
        status_icon = "🟢" if event["status"] == "completed" else "🔴" if event["status"] == "missed" else "⚪"
        st.write(f"Status: {status_icon} {event['status'].capitalize()}")
        st.markdown("---")
else:
    st.info("No events yet. Add one above.")
