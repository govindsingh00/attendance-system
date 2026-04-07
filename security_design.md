# Security Design Document
## E-Attendance System

## Authentication Security
- JWT tokens used for all API requests
- Tokens expire after 24 hours automatically
- Passwords hashed using bcrypt algorithm
- Plain text passwords never stored in database

## Authorization Security
- Role based access control implemented
- Admin can access all routes
- Teacher can only access their own subjects
- Student can only view their own records
- Every API endpoint checks user role

## Face Recognition Security
- Confidence score must be above 80 percent
- Every detection logged in FACE_LOG table
- Audit trail maintained for all detections
- Prevents unauthorized attendance marking

## Database Security
- All queries go through Django ORM
- SQL injection prevented by ORM
- No direct database access from frontend
- Regular database backups recommended
