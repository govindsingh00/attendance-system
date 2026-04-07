# Data Flow Diagram
## E-Attendance System

## Level 0 - Overview
Student/Staff → System → Attendance Record → Report

## Level 1 - Detailed Flow

### Flow 1: User Login
1. User opens browser
2. React frontend shows login page
3. User enters username and password
4. React sends POST to /api/auth/login/
5. Django checks credentials in USER table
6. Django returns JWT token
7. React stores token for future requests

### Flow 2: Face Recognition Attendance
1. ML module activates webcam
2. Webcam captures student face frame
3. ML model matches face to student in database
4. ML gets confidence score for match
5. ML sends POST to /api/attendance/face-mark/
6. Django receives user_id and subject_id
7. Django creates ATTENDANCE record as present
8. Django creates FACE_LOG entry with score
9. React shows attendance marked confirmation

### Flow 3: Manual Attendance
1. Teacher logs in via React frontend
2. Teacher selects subject and date
3. Teacher marks each student present or absent
4. React sends POST to /api/attendance/mark/
5. Django saves record in ATTENDANCE table
6. Django returns success response
7. React updates attendance list display

### Flow 4: Report Generation
1. Teacher or Admin opens report page
2. Selects student or subject filter
3. React sends GET to /api/reports/export/
4. Django queries ATTENDANCE table
5. Django calculates percentage and stats
6. Django returns data as JSON
7. React displays report or exports CSV
