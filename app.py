import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

app = Flask(__name__)

# --- Configuration ---
# Use environment variables for sensitive data, with local development defaults
app.secret_key = os.environ.get('SECRET_KEY', 'a_very_insecure_default_for_local_dev_only_change_me') # IMPORTANT: Change this default!

# Database Configuration
DB_CONFIG = {
<<<<<<< HEAD
    'host': os.environ.get('DB_HOST', 'localhost'), # Default to localhost for local testing
    'user': os.environ.get('DB_USER', 'your_local_dev_user'),
    'password': os.environ.get('DB_PASSWORD', 'your_local_dev_password'),
    'database': os.environ.get('DB_NAME', 'quiz_system'),
}

app.secret_key = os.environ.get('SECRET_KEY', 'default_dev_secret_key') # Also use an env var for secret key

=======
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'your_local_mysql_user'), # IMPORTANT: Your local MySQL username (e.g., 'root')
    'password': os.environ.get('DB_PASSWORD', 'your_local_mysql_password'), # IMPORTANT: Your local MySQL password (e.g., '')
    'database': os.environ.get('DB_NAME', 'quiz_system'),
}

# --- Database Connection Helper ---
>>>>>>> 63836e3 (Prepare for deployment: Added .env support, requirements.txt, and Procfile)
def get_db_connection():
    """Establishes a connection to the database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        # In a production environment, you might log this error and raise a more generic one
        flash('Database connection failed. Please try again later.', 'danger')
        return None

# --- Helper Functions (Authentication & Authorization) ---
def is_logged_in():
    """Check if a user is logged into the session."""
    return 'user_id' in session

def is_admin():
    """Check if the logged-in user is an admin."""
    return is_logged_in() and session.get('role') == 'admin'

def is_student():
    """Check if the logged-in user is a student."""
    return is_logged_in() and session.get('role') == 'student'

# --- Routes ---

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
    if is_logged_in(): # Prevent logged-in users from seeing login page
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] # In a real app, hash and verify passwords!

        conn = get_db_connection()
        if not conn:
            # flash message already handled by get_db_connection
            return render_template('login.html')

        cursor = conn.cursor(dictionary=True)
        # For simplicity, password is in plaintext here. Use hashing (e.g., bcrypt) in production!
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            # Set up session variables
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f'Welcome, {user["username"]}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles student registration."""
    if is_logged_in(): # Prevent logged-in users from registering again
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] # In a real app, hash passwords before storing!

        conn = get_db_connection()
        if not conn:
            return render_template('register.html')
        
        cursor = conn.cursor()
        # Check if username already exists
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        if cursor.fetchone():
            flash('Username already exists. Please choose another.', 'warning')
            cursor.close()
            conn.close()
            return render_template('register.html')

        # Insert new student user
        # Passwords should be hashed here in a real application
        cursor.execute('INSERT INTO users (username, password, role) VALUES (%s, %s, %s)', (username, password, 'student'))
        conn.commit() # Save changes to the database
        cursor.close()
        conn.close()

        flash('You have successfully registered! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logs the user out by clearing the session."""
    session.clear() # Clears all session data
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# --- Administrator Routes ---
@app.route('/admin_dashboard')
def admin_dashboard():
    """Displays the admin dashboard with subjects and questions."""
    if not is_admin():
        flash('Admin access required.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        return render_template('admin_dashboard.html', subjects=[], questions=[])

    cursor = conn.cursor(dictionary=True)
    
    # Fetch all subjects
    cursor.execute('SELECT id, name FROM subjects ORDER BY name')
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
        flash('Admin access required.', 'danger')
        return redirect(url_for('login'))
        
    subject_name = request.form['subject_name'].strip() # .strip() to remove leading/trailing whitespace

    if not subject_name:
        flash('Subject name cannot be empty.', 'warning')
        return redirect(url_for('admin_dashboard'))

    conn = get_db_connection()
    if not conn:
        return redirect(url_for('admin_dashboard'))
    
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO subjects (name) VALUES (%s)', (subject_name,))
        conn.commit()
        flash(f'Subject "{subject_name}" added successfully!', 'success')
    except mysql.connector.IntegrityError:
        flash(f'The subject "{subject_name}" already exists.', 'warning')
    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/add_question', methods=['POST'])
def add_question():
    """Handles adding a new question."""
    if not is_admin():
        flash('Admin access required.', 'danger')
        return redirect(url_for('login'))
        
    subject_id = request.form['subject_id']
    question_text = request.form['question_text'].strip()
    option1 = request.form['option1'].strip()
    option2 = request.form['option2'].strip()
    option3 = request.form['option3'].strip()
    option4 = request.form['option4'].strip()
    correct_answer = request.form['correct_answer']

    # Basic validation
    if not all([subject_id, question_text, option1, option2, option3, option4, correct_answer]):
        flash('All question fields are required.', 'warning')
        return redirect(url_for('admin_dashboard'))
    if not (1 <= int(correct_answer) <= 4):
        flash('Correct answer must be between 1 and 4.', 'warning')
        return redirect(url_for('admin_dashboard'))

    conn = get_db_connection()
    if not conn:
        return redirect(url_for('admin_dashboard'))

    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO questions (subject_id, question_text, option1, option2, option3, option4, correct_answer) VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (subject_id, question_text, option1, option2, option3, option4, correct_answer)
        )
        conn.commit()
        flash('Question added successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_dashboard'))

# --- Student Routes ---
@app.route('/student_dashboard')
def student_dashboard():
    """Displays the student dashboard with available quizzes."""
    if not is_student():
        flash('Student access required.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        return render_template('student_dashboard.html', subjects=[])

    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, name FROM subjects ORDER BY name')
    subjects = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('student_dashboard.html', subjects=subjects)

@app.route('/take_quiz/<int:subject_id>')
def take_quiz(subject_id):
    """Displays the quiz questions for a selected subject."""
    if not is_student():
        flash('Student access required.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        return redirect(url_for('student_dashboard'))
    
    cursor = conn.cursor(dictionary=True)
    
    # Get subject name
    cursor.execute('SELECT id, name FROM subjects WHERE id = %s', (subject_id,))
    subject = cursor.fetchone()
    if not subject:
        flash('Quiz subject not found.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('student_dashboard'))
    
    # Get questions for the subject
    cursor.execute('SELECT id, question_text, option1, option2, option3, option4 FROM questions WHERE subject_id = %s', (subject_id,))
    questions = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    if not questions:
        flash(f'No questions available for the "{subject["name"]}" quiz yet.', 'warning')
        return redirect(url_for('student_dashboard'))

    return render_template('quiz.html', subject=subject, questions=questions, subject_id=subject_id)

@app.route('/submit_quiz/<int:subject_id>', methods=['POST'])
def submit_quiz(subject_id):
    """Grades the submitted quiz and stores the result."""
    if not is_student():
        flash('Student access required.', 'danger')
        return redirect(url_for('login'))
        
    user_answers = request.form # Dict-like object of submitted form data
    
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('student_dashboard'))

    cursor = conn.cursor(dictionary=True)
    # Fetch correct answers for all questions in this subject
    cursor.execute('SELECT id, correct_answer FROM questions WHERE subject_id = %s', (subject_id,))
    correct_answers_map = {str(q['id']): str(q['correct_answer']) for q in cursor.fetchall()}
    
    score = 0
    total_questions = len(correct_answers_map)
    
    # Compare user answers with correct answers
    for question_id, correct_option_num in correct_answers_map.items():
        # user_answers.get(f'question_{question_id}') will return the value ('1', '2', '3', or '4')
        # if the radio button was selected, otherwise None.
        user_selected_option = user_answers.get(f'question_{question_id}')
        
        if user_selected_option == correct_option_num:
            score += 1
            
    # Save the attempt to the database
    user_id = session['user_id']
    try:
        cursor.execute(
            'INSERT INTO quiz_attempts (user_id, subject_id, score, total_questions) VALUES (%s, %s, %s, %s)',
            (user_id, subject_id, score, total_questions)
        )
        conn.commit()
        flash(f'Quiz Submitted! Your score is {score}/{total_questions}.', 'info')
    except Exception as e:
        flash(f'An error occurred while saving your results: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('my_results'))

@app.route('/my_results')
def my_results():
    """Displays the history of quiz attempts for the logged-in student."""
    if not is_student():
        flash('Student access required.', 'danger')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    
    conn = get_db_connection()
    if not conn:
        return render_template('my_results.html', attempts=[])

    cursor = conn.cursor(dictionary=True)
    # Join quiz_attempts with subjects to get the subject name for display
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

# --- Main Application Runner ---
if __name__ == '__main__':
    # Use debug=True only for local development.
    # For production, FLASK_ENV should be 'production' and debug=False.
    app.run(debug=True)