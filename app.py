import streamlit as st
import json
from datetime import date, timedelta, datetime
import os
import math
import calendar
import dateparser
from groq import Groq
from dotenv import load_dotenv
import streamlit.components.v1 as components

# ------------------ CONFIG ------------------
load_dotenv()
DATA_FILE = "data/user_memory.json"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ------------------ DATA HELPERS ------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "events": [],
            "user_behavior": {
                "tasks_completed": 0,
                "tasks_missed": 0
            },
            "activity_log": []
        }
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ------------------ BEHAVIOR ANALYSIS ------------------

def analyze_behavior(data):
    c = data["user_behavior"]["tasks_completed"]
    m = data["user_behavior"]["tasks_missed"]

    if m > c:
        return "⚠️ You often miss deadlines. Let’s plan smaller steps.", "firm but supportive"
    if c > 0:
        return "🎉 You’re consistent. Keep going!", "positive"
    return "📌 Let’s build consistency together.", "neutral"

# ------------------ AI HELPER ------------------

def generate_ai_text(task, tone):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful planning assistant."},
            {"role": "user", "content": f"Rewrite this task in a {tone} tone:\n{task}\nFormat:\nTitle:\nDescription:"}
        ],
        temperature=0.3,
        max_tokens=200
    )

    content = response.choices[0].message.content
    title = "Untitled Task"
    desc = content

    if "Title:" in content:
        title = content.split("Title:")[1].split("Description:")[0].strip()
        desc = content.split("Description:")[1].strip()

    return title, desc

# ------------------ DATE EXTRACTION ------------------

def ai_extract_date(text):
    """
    Use Groq AI to extract a date from text in YYYY-MM-DD format.
    Returns a date object or None if extraction fails.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a smart assistant that extracts dates from text."},
                {"role": "user", "content": f"Extract the date from this text in YYYY-MM-DD format: '{text}'. If no date is mentioned, reply 'None'."}
            ],
            temperature=0
        )
        date_str = response.choices[0].message.content.strip()

        if date_str.lower() == "none":
            return None
        
        # Convert AI string to date object
        from datetime import datetime
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        return parsed_date
    except Exception as e:
        print("AI date extraction error:", e)
        return None


# ------------------ STREAMLIT UI ------------------

st.set_page_config(page_title="Memory-Aware Calendar AI", layout="centered")
st.title("📅 Memory-Aware Calendar AI")

data = load_data()

# ------------------ BEHAVIOR BUTTON ------------------

if "show_behavior" not in st.session_state:
    st.session_state.show_behavior = False

if st.button("🔮 Predict my behaviour"):
    st.session_state.show_behavior = not st.session_state.show_behavior

if st.session_state.show_behavior:
    msg, tone = analyze_behavior(data)
    st.info(msg)
    st.success(f"🤖 AI tone: **{tone}**")

# ------------------ TRACK SELECTED DATE ------------------
import streamlit.components.v1 as components

# ------------------ CIRCULAR CALENDAR (STATIC & REACTIVE) ------------------

# Ensure session_state keys exist
if "selected_date" not in st.session_state:
    st.session_state.selected_date = None
# ------------------ Month Navigation (MUST BE FIRST) ------------------
if "current_month" not in st.session_state:
    today = date.today()
    st.session_state.current_month = today.month
    st.session_state.current_year = today.year

left, center, right = st.columns([1, 2, 1])

with left:
    if st.button("⬅", key="prev_month"):
        if st.session_state.current_month == 1:
            st.session_state.current_month = 12
            st.session_state.current_year -= 1
        else:
            st.session_state.current_month -= 1

with right:
    if st.button("➡", key="next_month"):
        if st.session_state.current_month == 12:
            st.session_state.current_month = 1
            st.session_state.current_year += 1
        else:
            st.session_state.current_month += 1
year = st.session_state.current_year
month = st.session_state.current_month
days_in_month = calendar.monthrange(year, month)[1]

st.subheader(f"{calendar.month_name[month]} {year}")

cols = st.columns(7)
for day in range(1, days_in_month + 1):
    col = cols[(day - 1) % 7]
    date_str = f"{year}-{month:02d}-{day:02d}"

    has_event = any(e["deadline"] == date_str for e in data["events"])

    label = f"🟢 {day}" if has_event else str(day)

    if col.button(label, key=f"day_btn_{date_str}"):
        st.session_state.selected_date = date_str



# ------------------ Generate SVG for circular calendar ------------------
date_marks = ""
for i in range(1, days_in_month + 1):
    angle = (i / days_in_month) * 2 * math.pi - math.pi / 2
    x = 150 + 110 * math.cos(angle)
    y = 150 + 110 * math.sin(angle)

    date_str = f"{year}-{month:02d}-{i:02d}"
    has_event = any(e["deadline"] == date_str for e in data["events"])

    if st.session_state.selected_date == date_str:
        color = "#ff9800"  # selected date
    elif has_event:
        color = "#4caf50"  # date has event
    else:
        color = "#555"      # normal date

    # Each circle will send the date back to Streamlit via component value
    date_marks += f"""
<g style="cursor:pointer"
   onclick="
     const inputs = window.parent.document.querySelectorAll('input');
     const target = Array.from(inputs).find(i => i.id.includes('calendar_click_input'));
     if (target) {{
       target.value = '{date_str}';
       target.dispatchEvent(new Event('input', {{ bubbles: true }}));
       target.dispatchEvent(new Event('change', {{ bubbles: true }}));
     }}
   ">
  <circle cx="{x}" cy="{y}" r="14" fill="{color}" />
  <text x="{x}" y="{y+5}" text-anchor="middle"
        font-size="12" fill="white" pointer-events="none">
        {i}
  </text>
</g>
"""



# Render SVG
components.html(f"""
    <svg width="300" height="300" viewBox="0 0 300 300">
        <circle cx="150" cy="150" r="130" stroke="#ddd" stroke-width="4" fill="none"/>
        {date_marks}
        <text x="150" y="145" text-anchor="middle" font-size="18" font-weight="bold">{calendar.month_name[month]}</text>
        <text x="150" y="170" text-anchor="middle" font-size="14" fill="#666">{year}</text>
    </svg>

""", height=320, scrolling=False)

    

# ------------------ AUDIO TRANSCRIPTION HELPER ------------------
def transcribe_audio_groq(audio_file):
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_file.getbuffer())
    transcription = client.audio.transcriptions.create(
        file=open("temp_audio.wav", "rb"),
        model="whisper-large-v3"
    )
    return transcription.text

# ------------------ PLAN INPUT (Using st.form) ------------------
st.subheader("✍️ Plan something")

if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""

with st.form("plan_form", clear_on_submit=True):
    plan_text = st.text_area(
        "Type your plan",
        placeholder="Finish AI report by Jan 31..."
    )
    audio_file = st.audio_input("🎙️ Or record your plan")
    submit = st.form_submit_button("💾 Save Plan")

    if submit:
        final_text = ""
        if audio_file is not None:
            with st.spinner("🧠 Transcribing audio..."):
                st.session_state.transcribed_text = transcribe_audio_groq(audio_file).strip()
            final_text = st.session_state.transcribed_text
        elif plan_text.strip():
            final_text = plan_text.strip()

        # Inside st.form submit logic
        if not final_text:
            st.warning("Please write or speak something.")
        else:
            msg, tone = analyze_behavior(data)
            title, desc = generate_ai_text(final_text, tone)

            # Use AI to extract date first
            parsed_date = ai_extract_date(final_text)

            if parsed_date is None:
                st.warning("⚠️ Could not detect a valid date from your input. Please include a proper date like 'Jan 31' or 'February 5'.")
            else:
                data["events"].append({
                    "title": title,
                    "description": desc,
                    "deadline": parsed_date.isoformat(),
                    "status": "pending"
                })
                save_data(data)
                st.success(f"🗓️ Saved for {parsed_date}")
                st.info(desc)
                st.session_state.transcribed_text = ""




# ------------------ DISPLAY EVENTS ------------------

st.divider()
st.subheader("📌 Events for Selected Date")

if st.session_state.selected_date:
    date_events = [
        e for e in data["events"]
        if e["deadline"] == st.session_state.selected_date
    ]
    if not date_events:
        st.info(f"No events on {st.session_state.selected_date}.")
    else:
        for idx, event in enumerate(date_events):
            with st.container():
                st.markdown(f"### {event['title']}")
                st.write(event["description"])
                st.caption(f"📅 Deadline: {event['deadline']}")

                status_icon = (
                    "🟢" if event["status"] == "completed"
                    else "🔴" if event["status"] == "missed"
                    else "⚪"
                )
                st.write(f"Status: {status_icon} {event['status'].capitalize()}")

                col1, col2, col3 = st.columns(3)

                if col1.button("✅ Done", key=f"done_{idx}_{event['deadline']}"):
                    event["status"] = "completed"
                    data["user_behavior"]["tasks_completed"] += 1
                    data["activity_log"].append({
                        "action": "task_completed",
                        "date": str(date.today())
                    })
                    save_data(data)
                   

                if col2.button("❌ Missed", key=f"missed_{idx}_{event['deadline']}"):
                    event["status"] = "missed"
                    data["user_behavior"]["tasks_missed"] += 1
                    data["activity_log"].append({
                        "action": "task_missed",
                        "date": str(date.today())
                    })
                    save_data(data)
                   

                if col3.button("🗑️ Delete", key=f"delete_{idx}_{event['deadline']}"):
                    data["activity_log"].append({
                        "action": "event_deleted",
                        "date": str(date.today())
                    })
                    data["events"].remove(event)
                    save_data(data)
                   
                st.markdown("---")
else:
    st.info("Select a date on the calendar to see its events.")
