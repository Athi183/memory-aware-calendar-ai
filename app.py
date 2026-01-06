import streamlit as st
import json
from datetime import date
import os

DATA_FILE = "data/user_memory.json"

# ------------------ Helper functions ------------------

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

# ------------------ App UI ------------------

st.set_page_config(page_title="Memory-Aware Calendar AI", layout="centered")

st.title("📅 Memory-Aware Calendar AI")
st.caption("A behavioral planning companion")

data = load_data()

behavior_feedback = analyze_behavior(data)
st.info(f"🧠 Memory Insight: {behavior_feedback['message']}")

# Date selector
selected_date = st.date_input("Select a date", date.today())

st.divider()

st.subheader("➕ Add Event")

event_title = st.text_input("Event title")
event_description = st.text_area("Describe your task / idea")
event_deadline = st.date_input("Deadline", selected_date)

if st.button("Save Event"):
    new_event = {
        "title": event_title,
        "description": event_description,
        "deadline": str(event_deadline),
        "status": "pending"
    }

    data["events"].append(new_event)
    data["activity_log"].append({
        "action": "event_added",
        "date": str(date.today())
    })

    save_data(data)
    st.success("Event added successfully!")

st.divider()

# ------------------ Events with behavior tracking ------------------

st.subheader("📌 Your Events")

if data["events"]:
    for idx, event in enumerate(data["events"]):
        st.markdown(f"### {event['title']}")
        st.write(event["description"])
        st.write(f"📅 Deadline: {event['deadline']}")

        col1, col2 = st.columns(2)

        if col1.button("✅ Done", key=f"done_{idx}"):
            event["status"] = "completed"
            data["user_behavior"]["tasks_completed"] += 1
            data["activity_log"].append({
                "action": "task_completed",
                "date": str(date.today())
            })
            save_data(data)
            st.experimental_rerun()

        if col2.button("❌ Missed", key=f"missed_{idx}"):
            event["status"] = "missed"
            data["user_behavior"]["tasks_missed"] += 1
            data["activity_log"].append({
                "action": "task_missed",
                "date": str(date.today())
            })
            save_data(data)
            st.experimental_rerun()

        status_color = "🟢" if event["status"] == "completed" else "🔴" if event["status"] == "missed" else "⚪"
        st.write(f"Status: {status_color} {event['status'].capitalize()}")

        st.markdown("---")
else:
    st.info("No events yet. Add one above.")
