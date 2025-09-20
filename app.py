import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
# Change this secret key in a real application
app.secret_key = 'your_very_secret_key'

# --- Database Configuration ---
# IMPORTANT: Update these details with your MySQL server information
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'), # Default to localhost for local testing
    'user': os.environ.get('DB_USER', 'your_local_dev_user'),
    'password': os.environ.get('DB_PASSWORD', 'your_local_dev_password'),
    'database': os.environ.get('DB_NAME', 'quiz_system'),
}

app.secret_key = os.environ.get('SECRET_KEY', 'default_dev_secret_key') # Also use an env var for secret key

def get_db_connection():
    """Establishes a connection to the database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

# --- Helper Functions ---
def is_logged_in():
    """Check if a user is logged into the session."""
    return 'user_id' in session

def is_admin():
    """Check if the logged-in user is an admin."""
    return is_logged_in() and session.get('role') == 'admin'

def is_student():
    """Check if the logged-in user is a student."""
    return is_logged_in() and session.get('role') == 'student'


# --- Authentication Routes ---
@app.route('/')
def home():
    """Homepage redirects to login or appropriate dashboard."""
    if is_admin():
        return redirect(url_for('admin_dashboard'))
    if is_student():
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed.', 'danger')
            return render_template('login.html')

        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            # Set up session variables
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('You are now logged in', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid login credentials.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles student registration."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed.', 'danger')
            return render_template('register.html')
        
        cursor = conn.cursor()
        # Check if username already exists
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        if cursor.fetchone():
            flash('Username already exists. Please choose another.', 'warning')
            return render_template('register.html')

        # Insert new student user
        cursor.execute('INSERT INTO users (username, password, role) VALUES (%s, %s, %s)', (username, password, 'student'))
        conn.commit()
        cursor.close()
        conn.close()

        flash('You have successfully registered! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logs the user out by clearing the session."""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# --- Administrator Routes ---
@app.route('/admin_dashboard')
def admin_dashboard():
    """Displays the admin dashboard with subjects and questions."""
    if not is_admin():
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        return render_template('admin_dashboard.html', subjects=[], questions=[])

    cursor = conn.cursor(dictionary=True)
    
    # Fetch all subjects
    cursor.execute('SELECT * FROM subjects ORDER BY name')
    subjects = cursor.fetchall()
    
    # Fetch all questions with their subject name
    cursor.execute('''
        SELECT q.id, q.question_text, s.name AS subject_name
        FROM questions q
        JOIN subjects s ON q.subject_id = s.id
        ORDER BY s.name, q.id
    ''')
    questions = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin_dashboard.html', subjects=subjects, questions=questions)

@app.route('/add_subject', methods=['POST'])
def add_subject():
    """Handles adding a new quiz subject."""
    if not is_admin():
        return redirect(url_for('login'))
        
    subject_name = request.form['subject_name']
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO subjects (name) VALUES (%s)', (subject_name,))
        conn.commit()
        flash('Subject added successfully!', 'success')
    except mysql.connector.IntegrityError:
        flash('This subject already exists.', 'warning')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_dashboard'))


@app.route('/add_question', methods=['POST'])
def add_question():
    """Handles adding a new question."""
    if not is_admin():
        return redirect(url_for('login'))
        
    subject_id = request.form['subject_id']
    question_text = request.form['question_text']
    option1 = request.form['option1']
    option2 = request.form['option2']
    option3 = request.form['option3']
    option4 = request.form['option4']
    correct_answer = request.form['correct_answer']

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        return redirect(url_for('admin_dashboard'))

    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO questions (subject_id, question_text, option1, option2, option3, option4, correct_answer) VALUES (%s, %s, %s, %s, %s, %s, %s)',
        (subject_id, question_text, option1, option2, option3, option4, correct_answer)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash('Question added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# --- Student Routes ---
@app.route('/student_dashboard')
def student_dashboard():
    """Displays the student dashboard with available quizzes."""
    if not is_student():
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        return render_template('student_dashboard.html', subjects=[])

    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM subjects ORDER BY name')
    subjects = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('student_dashboard.html', subjects=subjects)

@app.route('/take_quiz/<int:subject_id>')
def take_quiz(subject_id):
    """Displays the quiz questions for a selected subject."""
    if not is_student():
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        return redirect(url_for('student_dashboard'))
    
    cursor = conn.cursor(dictionary=True)
    
    # Get subject name
    cursor.execute('SELECT name FROM subjects WHERE id = %s', (subject_id,))
    subject = cursor.fetchone()
    if not subject:
        flash('Quiz subject not found.', 'danger')
        return redirect(url_for('student_dashboard'))
    
    # Get questions for the subject
    cursor.execute('SELECT * FROM questions WHERE subject_id = %s', (subject_id,))
    questions = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    if not questions:
        flash('No questions available for this subject yet.', 'warning')
        return redirect(url_for('student_dashboard'))

    return render_template('quiz.html', subject=subject, questions=questions, subject_id=subject_id)


@app.route('/submit_quiz/<int:subject_id>', methods=['POST'])
def submit_quiz(subject_id):
    """Grades the submitted quiz and stores the result."""
    if not is_student():
        return redirect(url_for('login'))
        
    user_answers = request.form
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        return redirect(url_for('student_dashboard'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, correct_answer FROM questions WHERE subject_id = %s', (subject_id,))
    correct_answers = {str(q['id']): str(q['correct_answer']) for q in cursor.fetchall()}
    
    score = 0
    total_questions = len(correct_answers)
    
    for question_id, correct_option in correct_answers.items():
        user_option = user_answers.get(f'question_{question_id}')
        if user_option == correct_option:
            score += 1
            
    # Save the attempt to the database
    user_id = session['user_id']
    cursor.execute(
        'INSERT INTO quiz_attempts (user_id, subject_id, score, total_questions) VALUES (%s, %s, %s, %s)',
        (user_id, subject_id, score, total_questions)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    flash(f'Quiz Submitted! Your score is {score}/{total_questions}.', 'info')
    return redirect(url_for('my_results'))

@app.route('/my_results')
def my_results():
    """Displays the history of quiz attempts for the logged-in student."""
    if not is_student():
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        return render_template('my_results.html', attempts=[])

    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT s.name as subject_name, qa.score, qa.total_questions, qa.attempt_date
        FROM quiz_attempts qa
        JOIN subjects s ON qa.subject_id = s.id
        WHERE qa.user_id = %s
        ORDER BY qa.attempt_date DESC
    ''', (user_id,))
    attempts = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('my_results.html', attempts=attempts)

if __name__ == '__main__':
    app.run(debug=True)
