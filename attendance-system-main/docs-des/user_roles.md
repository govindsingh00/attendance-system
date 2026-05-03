# User Roles and Permissions

## 3 User Types

### Admin
- Full system access
- Add or remove users
- Create and delete subjects
- View all reports

### Teacher
- View attendance of their subjects
- Manually mark attendance
- Generate attendance reports
- View student list per subject

### Student
- View own attendance only
- Auto-marked via face recognition
- See attendance percentage
- Cannot modify any records

## Database Storage
All 3 roles stored in one USER table.
Role field values: admin / teacher / student
