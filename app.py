from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB = BASE / 'campus.db'
app = Flask(__name__)
app.secret_key = 'change-this-secret-key'

def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with connect() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY AUTOINCREMENT, regno TEXT UNIQUE NOT NULL, name TEXT NOT NULL, department TEXT NOT NULL, year TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS attendance(id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER NOT NULL, day TEXT NOT NULL, status TEXT NOT NULL, UNIQUE(student_id,day), FOREIGN KEY(student_id) REFERENCES students(id));
        CREATE TABLE IF NOT EXISTS rooms(id INTEGER PRIMARY KEY AUTOINCREMENT, room_no TEXT UNIQUE NOT NULL, room_type TEXT NOT NULL, capacity INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'Available');
        CREATE TABLE IF NOT EXISTS notices(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, body TEXT NOT NULL, posted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        ''')
        if db.execute('SELECT COUNT(*) FROM students').fetchone()[0] == 0:
            db.executemany('INSERT INTO students(regno,name,department,year) VALUES(?,?,?,?)', [
                ('IT24001','Ananya R','Information Technology','II'),('IT24002','Kavin S','Information Technology','II'),('IT24003','Meera P','Information Technology','II')])
        if db.execute('SELECT COUNT(*) FROM rooms').fetchone()[0] == 0:
            db.executemany('INSERT INTO rooms(room_no,room_type,capacity,status) VALUES(?,?,?,?)', [
                ('A-101','Classroom',60,'Available'),('A-202','Computer Lab',40,'Occupied'),('B-105','Seminar Hall',100,'Available')])

@app.route('/')
def dashboard():
    with connect() as db:
        students = db.execute('SELECT COUNT(*) FROM students').fetchone()[0]
        rooms = db.execute('SELECT COUNT(*) FROM rooms').fetchone()[0]
        notices = db.execute('SELECT COUNT(*) FROM notices').fetchone()[0]
        today = db.execute("SELECT COUNT(*) FROM attendance WHERE day=date('now','localtime') AND status='Present'").fetchone()[0]
        latest = db.execute('SELECT * FROM notices ORDER BY id DESC LIMIT 3').fetchall()
    return render_template('dashboard.html', students=students, rooms=rooms, notices=notices, present=today, latest=latest)

@app.route('/students', methods=['GET','POST'])
def students_page():
    with connect() as db:
        if request.method == 'POST':
            regno, name, department, year = (request.form.get(k,'').strip() for k in ('regno','name','department','year'))
            if not all((regno,name,department,year)):
                flash('Fill in every student field.', 'error')
            else:
                try:
                    db.execute('INSERT INTO students(regno,name,department,year) VALUES(?,?,?,?)',(regno,name,department,year))
                    db.commit(); flash('Student added.', 'success')
                except sqlite3.IntegrityError:
                    flash('That register number already exists.', 'error')
            return redirect(url_for('students_page'))
        rows = db.execute('SELECT * FROM students ORDER BY name').fetchall()
    return render_template('students.html', students=rows)

@app.route('/students/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    with connect() as db:
        db.execute('DELETE FROM attendance WHERE student_id=?',(student_id,))
        db.execute('DELETE FROM students WHERE id=?',(student_id,)); db.commit()
    flash('Student removed.', 'success'); return redirect(url_for('students_page'))

@app.route('/attendance', methods=['GET','POST'])
def attendance_page():
    with connect() as db:
        if request.method == 'POST':
            day = request.form.get('day','').strip()
            for sid in request.form.getlist('student_id'):
                status = request.form.get(f'status_{sid}','Absent')
                db.execute('INSERT INTO attendance(student_id,day,status) VALUES(?,?,?) ON CONFLICT(student_id,day) DO UPDATE SET status=excluded.status',(sid,day,status))
            db.commit(); flash('Attendance saved.', 'success'); return redirect(url_for('attendance_page', day=day))
        day = request.args.get('day') or __import__('datetime').date.today().isoformat()
        rows = db.execute('SELECT s.*, a.status FROM students s LEFT JOIN attendance a ON a.student_id=s.id AND a.day=? ORDER BY s.name',(day,)).fetchall()
    return render_template('attendance.html', students=rows, day=day)

@app.route('/rooms')
def rooms_page():
    with connect() as db: rows = db.execute('SELECT * FROM rooms ORDER BY room_no').fetchall()
    return render_template('rooms.html', rooms=rows)

@app.route('/rooms/status/<int:room_id>', methods=['POST'])
def room_status(room_id):
    with connect() as db:
        current = db.execute('SELECT status FROM rooms WHERE id=?',(room_id,)).fetchone()
        if current:
            db.execute('UPDATE rooms SET status=? WHERE id=?',('Occupied' if current['status']=='Available' else 'Available',room_id)); db.commit()
    return redirect(url_for('rooms_page'))

@app.route('/notices', methods=['GET','POST'])
def notices_page():
    with connect() as db:
        if request.method == 'POST':
            title, body = request.form.get('title','').strip(), request.form.get('body','').strip()
            if title and body:
                db.execute('INSERT INTO notices(title,body) VALUES(?,?)',(title,body)); db.commit(); flash('Notice posted.', 'success')
            else: flash('Enter both a title and notice text.', 'error')
            return redirect(url_for('notices_page'))
        rows = db.execute('SELECT * FROM notices ORDER BY id DESC').fetchall()
    return render_template('notices.html', notices=rows)

@app.route('/notices/delete/<int:notice_id>', methods=['POST'])
def delete_notice(notice_id):
    with connect() as db: db.execute('DELETE FROM notices WHERE id=?',(notice_id,)); db.commit()
    flash('Notice deleted.', 'success'); return redirect(url_for('notices_page'))

init_db()
if __name__ == '__main__':
    app.run(debug=True)
#hello python