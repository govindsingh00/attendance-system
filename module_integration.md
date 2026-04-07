# Module Integration Document
## E-Attendance System

## Team Members and Their Modules

### Govind Singh - Backend Developer
- Builds all REST API endpoints in Django
- Handles database models and migrations
- JWT authentication implementation
- Connects all modules together via API

### Navneet Kumar - System Designer
- System architecture diagram
- ER diagram and database schema design
- API endpoints specification document
- Data flow diagram
- Tech stack selection and justification
- Module integration planning

### ML Teammate - Face Recognition
- Python OpenCV face detection module
- Trains recognition model on student photos
- Sends matched data to Django API
- Stores detection logs in FACE_LOG table

### Frontend Teammate - React Developer
- Login and registration pages
- Student and teacher dashboard
- Attendance view and marking pages
- Report generation and export UI
- Calls Django REST API for all data

### Database Teammate - PostgreSQL Setup
- Sets up PostgreSQL server
- Runs Django migrations
- Manages database connections
- Handles backup and restore

## How Modules Connect

### ML to Django Connection
- ML sends: POST /api/attendance/face-mark/
- Data sent: user_id, subject_id, confidence_score
- Django saves to ATTENDANCE table
- Django saves to FACE_LOG table

### React to Django Connection
- All requests include JWT token in header
- React calls GET /api/attendance/ for records
- React calls POST /api/auth/login/ for login
- Django always returns JSON response

### Django to PostgreSQL Connection
- Django ORM handles all database queries
- Models in models.py map to database tables
- Migrations track all schema changes

## Module Dependency Order
1. PostgreSQL setup first
2. Django backend second
3. ML module needs Django API running
4. React frontend built last
5. System design guides all above steps
