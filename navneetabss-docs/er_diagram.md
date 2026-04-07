# Database ER Diagram

## 5 Tables

### USER
- id, username, email, password_hash
- role: admin / teacher / student
- full_name, date_of_birth, created_at

### SUBJECT
- id, subject_code, subject_name
- department, teacher_id (FK to USER)

### ENROLLMENT
- id, student_id (FK), subject_id (FK)
- enrolled_on (date)

### ATTENDANCE
- id, student_id (FK), subject_id (FK)
- attendance_date, status: present/absent
- marked_by: manual / face_recognition
- marked_at (timestamp)

### FACE_LOG
- id, user_id (FK)
- image_path, confidence_score
- detected_at (timestamp)

## Relationships
- USER enrolls in many SUBJECTS
- SUBJECT has many STUDENTS
- STUDENT has many ATTENDANCE records
- Each face detection creates one FACE_LOG
