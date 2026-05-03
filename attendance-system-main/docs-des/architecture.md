# System Architecture Document
## E-Attendance System

## Overview
The E-Attendance System is a web-based application that uses face recognition
to automatically mark attendance for both students and employees.

## Architecture Type
Client-Server Architecture with REST API

## Components

### 1. React Frontend (Client)
- Runs in the browser
- Communicates with Django via REST API
- Pages: Login, Dashboard, Attendance View, Reports
- Handles JWT token for authentication
- Real-time feedback for face detection

### 2. Django Backend (Server)
- Core business logic
- REST API via Django REST Framework
- JWT based authentication
- Handles all database operations via ORM
- Connects ML module output to database

### 3. PostgreSQL Database
- Stores all persistent data
- Tables: USER, SUBJECT, ENROLLMENT, ATTENDANCE, FACE_LOG
- Connected to Django via django.db settings
- Handles relational data with foreign keys

### 4. ML Face Recognition Module
- Built in Python using OpenCV
- Captures webcam frames
- Detects and matches student faces
- Sends matched user_id to Django API
- Logs every detection in FACE_LOG table

### 5. GitHub Repository
- All team members use feature branches
- Pull requests for merging code
- Branch strategy: main, backend, FRONTEND, feature/ml, navneetabss-new-1

## How Components Connect
1. Student opens browser - React Frontend loads
2. Student logs in - React calls POST /api/auth/login/
3. Django checks credentials in PostgreSQL
4. Django returns JWT token to React
5. Webcam activates - ML module starts
6. ML detects face - calls POST /api/attendance/face-mark/
7. Django saves record in ATTENDANCE table
8. React fetches updated attendance via GET /api/attendance/
9. Teacher views report via GET /api/reports/export
cat > docs-des/architecture.md << 'EOF'
# System Architecture Document
## E-Attendance System

## Overview
The E-Attendance System is a web-based application that uses face recognition
to automatically mark attendance for both students and employees.
## Security
- JWT tokens expire after 24 hours
- Passwords stored as hashed values
- Role based access control
- Admin, Teacher, Student have different permissions

## Deployment Plan
- Backend: Django on local server or cloud
- Frontend: React build served via nginx
- Database: PostgreSQL on same or separate server
- ML Module: Runs locally on device with webcam
