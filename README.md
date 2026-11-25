# Smart Campus Management System

A small Flask + SQLite web application for managing student records, daily attendance, room availability, and campus notices.

## Features
- Dashboard with student, room, notice, and today's attendance counts
- Add/list/remove students (register number must be unique)
- Mark attendance by date and update saved attendance
- View rooms and toggle availability
- Post and delete notices
- SQLite database is initialized automatically with sample students and rooms

## Requirements
- Python 3.10+

## Run on Windows
1. Extract this ZIP.
2. Open a terminal in the extracted `smart_campus_app` folder.
3. Run `python -m pip install -r requirements.txt`
4. Run `python app.py`
5. Open `http://127.0.0.1:5000` in a browser.

The app creates `campus.db` automatically in the project folder. Delete that file to reset the database and sample data.
