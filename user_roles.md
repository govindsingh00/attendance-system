# User Roles and Permissions

## 3 User Types in System

### 1. Admin
- Full access to everything
- Add or remove users
- Create and delete subjects
- View all attendance reports
- Manage entire system settings

### 2. Teacher
- View attendance of their subjects only
- Manually mark attendance if needed
- Generate and export attendance reports
- View student list per subject
- Cannot access other teachers subjects

### 3. Student
- View own attendance records only
- Gets auto marked via face recognition
- See attendance percentage per subject
- Cannot modify any attendance records
- Cannot view other students data

## How Roles Are Stored
- All 3 roles in one USER table
- Role field values: admin / teacher / student
- JWT token carries role information
- Django checks role before every API call
