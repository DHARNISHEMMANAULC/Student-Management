STUDENT MANAGEMENT SYSTEM - FLASK + SQLITE

1. Open this folder in VS Code.
2. Open the VS Code terminal.
3. Create and activate a virtual environment (optional but recommended):

   Windows:
   py -m venv venv
   venv\Scripts\activate

   macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate

4. Install dependencies:

   pip install -r requirements.txt

5. Run the application:

   python app.py

6. Open this address in your browser:

   http://127.0.0.1:5000

DATABASE
- SQLite database is created automatically at instance/management.db.
- Do not create the database manually.
- Student records remain saved after the Flask server stops.

FEATURES
- Add student
- View student records
- Search by name, email or phone
- Filter by course
- Edit student
- Delete student
- Course analytics
- JSON endpoint: http://127.0.0.1:5000/api/students

DOCKER
Build:
   docker build -t student-management .

Run:
   docker run -d --name student-management -p 5000:5000 -v student_data:/app/instance student-management

Open:
   http://localhost:5000

SECURITY NOTE
Change SECRET_KEY to a long random secret before deploying publicly.
This workshop project is a starting point; add authentication and production
server configuration before exposing real student information online.
