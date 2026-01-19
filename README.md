# 📅 Memory-Aware Calendar AI

A smart, interactive calendar application built entirely with **Streamlit** and **Groq AI**, designed to help you plan your tasks intelligently, visualize them on a calendar, and get behavior insights.

---

## Features

1. **AI-Powered Date Extraction**

   * Enter your plans via text or voice.
   * The AI extracts the correct date (YYYY-MM-DD) from your input automatically.
   * Ensures your events are accurately mapped regardless of accidental calendar clicks.

2. **Interactive Circular & Grid Calendar**

   * Visual calendar showing all days of the current month.
   * Dates with saved events are highlighted in green.
   * Click on a date to view the events for that day without reloading the page.
   * Current selected date is highlighted in orange.

3. **Plan Input**

   * Add a plan via text or voice input.
   * AI rewrites your plan in a supportive, motivational, or neutral tone.
   * Automatic mapping of plans to dates using AI.

4. **Behavior Analysis**

   * Predict your behavior based on completed vs. missed tasks.
   * Get motivational messages or tips to improve consistency.

5. **Event Management**

   * Mark tasks as **Done** ✅ or **Missed** ❌.
   * Delete tasks 🗑️.
   * Visualize all events for a selected date.

---

## Technologies Used

* **Streamlit** – for the interactive web app UI.
* **Groq AI** – used for:

  * Rewriting tasks in a motivational or supportive tone.
  * Extracting dates from user input (text or voice).
* **Python** – main programming language for logic and AI integration.
* **SVG & HTML** – for circular calendar visualization.

---

## How It Works

1. **Open the app** – The homepage displays the current month with a circular calendar and a list of events for the selected date.
2. **Adding a Plan**

   * Type your plan in the text area or record it using the voice input.
   * The AI automatically extracts the **date** from your input.
   * AI rewrites your task in a friendly or motivational tone.
   * Click **Save Plan** to save it.
3. **Calendar Visualization**

   * Dates with events appear in green.
   * Click on any date to highlight it and view its events.
4. **Behavior Prediction**

   * Click the **Predict my behaviour** button to receive motivational messages and insights.
5. **Managing Events**

   * Use **Done**, **Missed**, or **Delete** buttons to manage your tasks.
   * The behavior log updates automatically based on your interactions.

---

## Usage Notes

* **Date Format:** When specifying an event in text or voice, include the **day, month, and optionally the year** for accurate AI extraction.
* **Voice Input:** Works the same way as typing; the AI extracts the date from your spoken input.
* **Event Visualization:** After adding a plan, you may need to reload the page to see the green indicator on the calendar for the new event.
* **No accidental overrides:** Clicking a calendar date does **not** override the AI-detected date of your plan. The calendar is primarily for viewing and selecting dates for filtering events.

---

## Setup Instructions

1. Clone the repository:

   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file and add your **Groq API Key**:

   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. Run the app:

   ```bash
   streamlit run app.py
   ```

6. Open your browser at https://memory-aware-calendar-ai.streamlit.app/ to access the app.

---

## Screenshots
<img width="1854" height="1721" alt="image" src="https://github.com/user-attachments/assets/3a541fb1-00ab-46dd-8715-c301cb8fa616" />
<img width="1854" height="2349" alt="image" src="https://github.com/user-attachments/assets/0bb45b77-c552-4c80-86ff-873d238b87b6" />

