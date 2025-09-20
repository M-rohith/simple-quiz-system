1. About the Project
The Simple Online Quiz System is a web-based application designed to facilitate the creation, management, and participation in online quizzes. It offers a straightforward interface for administrators to set up quiz subjects and questions, and for students to take quizzes and review their results. This project serves as a practical demonstration of full-stack web development using Python Flask and MySQL.

2. Features
Administrator Module:
Secure Admin Login: Access to an exclusive administrative dashboard.
Subject Management: Add and view various quiz subjects (e.g., "History", "Mathematics").
Question Management: Add new multiple-choice questions for any existing subject.
Content Overview: View all subjects and questions currently in the system.

Student Module:
User Registration: Create new student accounts.
Student Login: Access a personalized student dashboard.
Quiz Selection: Browse and select from available quiz subjects.
Quiz Attempt: Take quizzes with dynamically loaded questions.
Automated Grading: Receive an immediate score upon quiz submission.
Quiz History: View a personal record of all past quiz attempts and scores.

3. Technical Stack
Backend:
Python 3.x: The core programming language.
Flask: A lightweight and powerful web framework for Python.
Gunicorn: A production-ready WSGI HTTP server (used for deployment).
mysql-connector-python: Python driver to connect to MySQL.
python-dotenv: For managing environment variables (local development).

Database:
MySQL: A robust relational database management system for storing application data.

Frontend:
HTML5: Structure of the web pages.
CSS3 (Tailwind CSS): Styling and responsive design.
JavaScript: For basic client-side interactions (if any were added).

4. Database Schema
The application's data is structured across four main tables in a MySQL database. Below is a simplified schema diagram illustrating the entities and their relationships:
<img width="1024" height="1024" alt="schema" src="https://github.com/user-attachments/assets/02901207-d398-4023-8a27-95c0a5de3ce3" />


Entities:
users: Stores user authentication details and role (admin or student).
subjects: Stores the names of different quiz categories.
questions: Contains the quiz questions, options, and correct answers, linked to a subject.
quiz_attempts: Records each student's quiz attempt, including score and date, linked to a user and subject.

5. Getting Started
Follow these steps to get your local development environment up and running.

Prerequisites
Before you begin, ensure you have the following installed on your system:
Python 3.x: Download Python
pip: Python package installer (usually comes with Python).
MySQL Server: [suspicious link removed] or use a package like XAMPP (includes MySQL).
Git: Download Git

Installation (Local Development)
Clone the Repository:
Bash:
git clone https://github.com/your-username/simple-quiz-system.git
cd simple-quiz-system
(Replace your-username/simple-quiz-system.git with your actual GitHub repository URL)

Create a Python Virtual Environment (Recommended):
Bash :
python -m venv venv
Activate the Virtual Environment:

Windows:
Bash:
.\venv\Scripts\activate

macOS/Linux:
Bash:
source venv/bin/activate

Install Required Python Packages:
Bash:
pip install -r requirements.txt

Set up the MySQL Database:
Ensure your MySQL server is running.
Open a MySQL client (e.g., MySQL Workbench, phpMyAdmin, or the MySQL command-line client).
Execute the SQL script to create the database and tables:

Bash :
mysql -u your_mysql_user -p < database_setup.sql
(Replace your_mysql_user with your MySQL username, e.g., root. You'll be prompted for the password.)

Configure Environment Variables for Local Development:
Create a file named .env in the root of your project directory.
Add your local MySQL credentials and a SECRET_KEY to this file:
DB_HOST=localhost
DB_USER=your_local_mysql_username # e.g., root
DB_PASSWORD=your_local_mysql_password # e.g., (blank if no password)
DB_NAME=quiz_system
SECRET_KEY=a_long_random_string_for_local_dev
Important: Ensure these match your actual local MySQL setup.

Running the Application
Activate your virtual environment (if not already active).
Run the Flask application:
Bash
python app.py
Open your web browser and navigate to: http://127.0.0.1:5000/

6. Usage
Admin User
Login: Use the default admin credentials:
Username: admin
Password: admin123

From the admin dashboard, you can:
Add new subjects (e.g., "Physics", "Chemistry").
Add new questions by selecting a subject and providing question text, four options, and indicating the correct option (1-4).
View all existing subjects and questions.

Student User
Register: If you don't have an account, click "Register here" on the login page to create a new student account.
Login: Use your registered student username and password.

From the student dashboard, you can:
See a list of available quizzes (subjects).
Click "Start Quiz" to begin an assessment.
Select your answers for each question.
Submit the quiz to receive your score instantly.
Navigate to "My Results" to view your historical quiz attempts.

7. Deployment
This project is configured for deployment to cloud platforms like Heroku or Render. Key deployment preparations include:
requirements.txt: Lists all Python dependencies for the server to install.
.env for local / Environment Variables for Production: Sensitive data (DB credentials, SECRET_KEY) are managed via environment variables, ensuring they are not hardcoded.
Procfile: Specifies how the web process should be started in a production environment using gunicorn.
To deploy, you would typically:
Push your code to a GitHub repository.
Choose a hosting provider (e.g., Render, Heroku).
Set up an external MySQL database instance (as free tiers often don't include robust SQL).
Configure environment variables on the hosting platform's dashboard with your production database credentials and a strong, unique SECRET_KEY.
Connect tje hosting platform to your GitHub repository for automated or manual deployments.
Run your database_setup.sql script on the remote production database.
