# Database ER Diagram
## E-Attendance System

## 5 Main Tables

### 1. USER Table
- id (Primary Key, auto increment)
- username (unique)
- email (unique)
- password_hash
- role (admin / teacher / student)
- full_name
- date_of_birth
- created_at (timestamp)

### 2. SUBJECT Table
- id (Primary Key)
- subject_code (unique)
- subject_name
- department
- teacher_id (Foreign Key to USER)
- created_at

### 3. ENROLLMENT Table
- id (Primary Key)
- student_id (Foreign Key to USER)
- subject_id (Foreign Key to SUBJECT)
- enrolled_on (date)

### 4. ATTENDANCE Table
- id (Primary Key)
- student_id (Foreign Key to USER)
- subject_id (Foreign Key to SUBJECT)
- attendance_date (date)
- status (present / absent)
- marked_by (manual / face_recognition)
- marked_at (timestamp)

### 5. FACE_LOG Table
- id (Primary Key)
- user_id (Foreign Key to USER)
- image_path (string)
- confidence_score (float)
- detected_at (timestamp)

## Relationships
- One USER can enroll in many SUBJECTS
- One SUBJECT can have many STUDENTS
- One STUDENT has many ATTENDANCE records
- Each face detection creates one FACE_LOG entry
- One TEACHER can teach many SUBJECTS
