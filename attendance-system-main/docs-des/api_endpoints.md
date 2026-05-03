# API Endpoints

## Authentication
- POST /api/auth/login/ — Login, returns JWT token
- POST /api/auth/logout/ — Logout
- POST /api/auth/register/ — Register new user

## Users
- GET /api/users/ — List all users
- GET /api/users/id/ — Get single user
- PUT /api/users/id/ — Update user
- DELETE /api/users/id/ — Delete user

## Subjects
- GET /api/subjects/ — List all subjects
- POST /api/subjects/ — Create subject
- DELETE /api/subjects/id/ — Delete subject

## Attendance
- GET /api/attendance/ — View records
- POST /api/attendance/mark/ — Mark manually
- POST /api/attendance/face-mark/ — Mark via ML
- GET /api/attendance/report/ — Get report

## Reports
- GET /api/reports/student/id/ — Student report
- GET /api/reports/subject/id/ — Subject report
- GET /api/reports/export/ — Export CSV or PDF
