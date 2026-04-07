# System Architecture Document
## E-Attendance System

## Overview
Web-based attendance system using face recognition
for students and employees.

## Architecture Pattern
Client-Server with REST API

## Component 1: React Frontend
- Runs in browser
- Login, Dashboard, Attendance, Reports pages
- Sends requests to Django API
- Shows face detection feedback in real time
- JWT token stored in browser for auth

## Component 2: Django Backend
- Handles all business logic
- REST API via Django REST Framework
- JWT authentication for all routes
- Admin panel for management
- Connects ML output to database

## Component 3: PostgreSQL Database
- Stores users, subjects, attendance, face logs
- Django ORM handles all queries
- Foreign keys maintain data integrity
- Supports complex reporting queries

## Component 4: ML Face Recognition






cat > architecture.md << 'EOF'
# System Architecture Document
## E-Attendance System

## Overview
Web-based attendance system using face recognition
for students and employees.

## Architecture Pattern
Client-Server with REST API

## Component 1: React Frontend
- Runs in browser
- Login, Dashboard, Attendance, Reports pages
- Sends requests to Django API
- Shows face detection feedback in real time
- JWT token stored in browser for auth

## Component 2: Django Backend
- Handles all business logic
- REST API via Django REST Framework
- JWT authentication for all routes
- Admin panel for management
- Connects ML output to database

## Component 3: PostgreSQL Database
- Stores users, subjects, attendance, face logs
- Django ORM handles all queries
- Foreign keys maintain data integrity
- Supports complex reporting queries

## Component 4: ML Face Recognition
- Python + OpenCV
- Webcam captures frames
- Matches face to enrolled students
- Posts result to Django API
- Confidence score logged every time

## Component 5: GitHub
- All members use feature branches
- Pull requests for merging
- Code review before merge to main

## Request Flow Example
1. Student opens browser
2. React loads login page
3. Student submits credentials
4. Django verifies in PostgreSQL
5. Django returns JWT token
6. Webcam starts via ML module
7. Face detected and matched
8. Django marks attendance
9. React shows confirmation
10. Teacher exports final report

## Security Design
- Passwords never stored as plain text
- JWT tokens expire after 24 hours
- Every API route checks user role
- Face logs kept for audit trail
- HTTPS for all communications

## Scalability Notes
- PostgreSQL handles thousands of records
- Django can run on multiple servers
- React frontend is stateless
- ML module runs independently
- Each component can scale separately
