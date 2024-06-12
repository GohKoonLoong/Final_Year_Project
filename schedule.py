import streamlit as st
import pandas as pd
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta
import os

# Constants
CSV_FILE = "storage/schedule.csv"

# Initialize or load schedule dataframe
def load_schedule():
    if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
        df = pd.read_csv(CSV_FILE)
        return df
    else:
        return pd.DataFrame(columns=['Task', 'Date'])

def save_schedule():
    st.session_state['schedule'].to_csv(CSV_FILE, index=False)

if 'schedule' not in st.session_state:
    st.session_state['schedule'] = load_schedule()

def notify_due_tasks():
    today = datetime.date.today()
    upcoming_tasks = st.session_state['schedule'][(st.session_state['schedule']['Date'] <= today + timedelta(days=1))]
    if not upcoming_tasks.empty:
        for index, task in upcoming_tasks.iterrows():
            st.warning(f"Task '{task['Task']}' is due on {task['Date']}")

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.add_job(notify_due_tasks, 'interval', minutes=1)
scheduler.start()

def main():
    st.set_page_config(page_title="Timetable Schedule", page_icon="📆")
    st.header("Timetable Schedule 📆")

    st.header("Add New Task")
    task = st.text_input("Task")
    date = st.date_input("Date", min_value=datetime.date.today())
    submit = st.button("Add Task")
    
    if submit:
        new_task = pd.DataFrame([[task, date]], columns=['Task', 'Date'])
        st.session_state['schedule'] = pd.concat([st.session_state['schedule'], new_task], ignore_index=True)
        save_schedule()
        st.success("Task added!")

    # Display the schedule in a table format with checkboxes
    st.write("## Your Schedule")
    st.markdown("""
        <style>
        .schedule-table {
            font-size: 18px;
            width: 100%;
            border-collapse: collapse;
        }
        .schedule-table th, .schedule-table td {
            padding: 10px;
            text-align: left;
            border: 1px solid #dddddd;
        }
        .schedule-table th {
            background-color: #black;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Ensure dates are in datetime format
    if not st.session_state['schedule'].empty:
        st.session_state['schedule']['Date'] = pd.to_datetime(st.session_state['schedule']['Date']).dt.date
        st.session_state['schedule'] = st.session_state['schedule'].sort_values(by='Date')
        st.write(st.session_state['schedule'].to_html(classes='schedule-table', index=False), unsafe_allow_html=True)

    # Run notification check
    notify_due_tasks()

if __name__ == "__main__":
    main()
