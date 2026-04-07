# API Endpoints List
## E-Attendance System

## Authentication APIs
- POST /api/auth/login/ — User login returns JWT token
- POST /api/auth/logout/ — User logout clears token
- POST /api/auth/register/ — Register new user account
- POST /api/auth/refresh/ — Refresh expired JWT token

## User Management APIs
- GET /api/users/ — List all users (Admin only)
- GET /api/users/id/ — Get single user details
- PUT /api/users/id/ — Update user information
- DELETE /api/users/id/ — Delete user (Admin only)
- GET /api/users/me/ — Get current logged in user

## Subject APIs
- GET /api/subjects/ — List all subjects
- POST /api/subjects/ — Create new subject (Teacher or Admin)
- GET /api/subjects/id/ — Get subject details
- PUT /api/subjects/id/ — Update subject info
- DELETE /api/subjects/id/ — Delete subject (Admin only)

## Enrollment APIs
- GET /api/enrollments/ — List all enrollments
- POST /api/enrollments/ — Enroll student in subject
- DELETE /api/enrollments/id/ — Remove enrollment

## Attendance APIs
- GET /api/attendance/ — View all attendance records
- POST /api/attendance/mark/ — Mark attendance manually
- POST /api/attendance/face-mark/ — Mark via ML face recognition
- GET /api/attendance/report/ — Get attendance report
- GET /api/attendance/student/id/ — Get student attendance

## Report APIs
- GET /api/reports/student/id/ — Full student report
- GET /api/reports/subject/id/ — Subject wise report
- GET /api/reports/export/ — Export as CSV or PDF
- GET /api/reports/summary/ — Dashboard summary stats
