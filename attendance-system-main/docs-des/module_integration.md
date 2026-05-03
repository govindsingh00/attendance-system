# Module Integration Document
## E-Attendance System

## Team Members and Modules

### Govind Singh - Backend (Django)
- Builds REST API endpoints
- Handles database models
- JWT authentication logic
- Connects all modules together

### Navneet Kumar - System Design
- Architecture diagram
- ER diagram and database schema
- API endpoints specification
- Data flow documentation
- Tech stack justification

### ML Teammate - Face Recognition
- Python OpenCV face detection
- Trains model on student photos
- Sends data to Django API
- Logs detections in FACE_LOG

### Frontend Teammate - React
- Login and dashboard pages
- Attendance view and report pages
- Calls Django REST API
- Shows real-time face detection status

### Database Teammate - PostgreSQL
- Sets up PostgreSQL server
- Runs Django migrations
- Manages database connections
- Handles backup and restore

## Integration Points

### ML Module to Django
- ML calls: POST /api/attendance/face-mark/
- Sends: user_id, subject_id, confidence_score, image_path
- Django saves to ATTENDANCE and FACE_LOG tables
- ML needs: list of enrolled student face data

### React Frontend to Django
- All API calls use JWT token in header
- React calls GET /api/attendance/ to show records
- React calls POST /api/auth/login/ for authentication
- Django returns JSON responses to React

### Django to PostgreSQL
- Django ORM handles all queries
- Models map directly to database tables
- Migrations track schema changes
- No raw SQL needed

## Data Flow Summary
Webcam Input
  → ML Module detects face
  → POST to Django API with user_id
  → Django saves ATTENDANCE record
  → React fetches updated records
  → Teacher views final report

## Dependency Order
1. PostgreSQL must be set up first
2. Django backend second
3. ML module needs Django running
4. React frontend last
5. System design documents guide all above
