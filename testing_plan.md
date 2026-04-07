# Testing Plan
## E-Attendance System

## Unit Testing

### Backend Tests
- Test login API with correct credentials
- Test login API with wrong credentials
- Test attendance marking with valid user
- Test attendance marking with invalid user
- Test report generation for student
- Test report generation for subject
- Test JWT token expiry handling
- Test role based access for admin routes
- Test role based access for teacher routes
- Test role based access for student routes

### ML Module Tests
- Test face detection with clear image
- Test face detection with blurry image
- Test confidence score calculation
- Test with unknown face not in database
- Test with multiple faces in one frame
- Test webcam connection and disconnection

### Database Tests
- Test USER table insert and retrieve
- Test SUBJECT table foreign key constraint
- Test ENROLLMENT table unique constraint
- Test ATTENDANCE table date filtering
- Test FACE_LOG table confidence score storage

## Integration Testing
- Test React login calling Django API
- Test ML module calling attendance API
- Test Django saving to PostgreSQL
- Test report export from database to CSV
- Test complete attendance flow end to end

## User Acceptance Testing

### Admin Testing
- Admin can create new user accounts
- Admin can create new subjects
- Admin can view all attendance reports
- Admin can delete users and subjects

### Teacher Testing
- Teacher can view their subject attendance
- Teacher can manually mark attendance
- Teacher can export attendance as CSV
- Teacher cannot access other subjects

### Student Testing
- Student can view own attendance
- Student cannot modify attendance
- Student can see attendance percentage
- Student cannot view other students data

## Performance Testing
- System handles 100 concurrent users
- Attendance marking under 2 seconds
- Report generation under 5 seconds
- Face recognition under 1 second per frame[200~frame
EOF~

s
s
## Performance Testing
- System handles 100 concurrent users
- Attendance marking under 2 seconds
- Report generation under 5 seconds
- Face recognition under 1 second per frame
