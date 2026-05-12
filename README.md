# Atmos — AI-Powered Face Recognition Attendance System

![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat-square&logo=python)
![Django](https://img.shields.io/badge/Django-5.1-green?style=flat-square&logo=django)
![ArcFace](https://img.shields.io/badge/ArcFace-DeepFace-orange?style=flat-square)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.33-red?style=flat-square)

> Web-based AI attendance system — no special hardware, runs in any browser.

---

## What is Atmos?

Atmos is a face recognition based attendance system built as an MCA final year project at Lovely Professional University. A teacher starts an attendance session from the browser, students look at the camera, and the system automatically marks them present using ArcFace deep learning model. Blink detection prevents proxy attendance using printed photos.

**Recognition Accuracy:** 70–80%  
**Response Time:** 2–3 seconds per frame  
**Anti-Spoofing:** Blink detection via MediaPipe EAR  

---

## How It Works

```
Teacher clicks "Start Attendance"
        ↓
Browser camera captures frame every 3 seconds
        ↓
Server checks for blink (liveness / anti-spoofing)
        ↓
Haar Cascade detects face region
        ↓
ArcFace generates 512-D embedding vector
        ↓
Cosine similarity vs stored encodings (threshold: 0.4)
        ↓
Match found → AttendanceRecord saved → Name shown in UI
```
---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.1 (Python) |
| Database | SQLite |
| Face Recognition | DeepFace + ArcFace (ResNet-50) |
| Face Detection | OpenCV Haar Cascade |
| Liveness Detection | MediaPipe Face Mesh |
| Training | Kaggle GPU |
| Frontend | HTML5, CSS3, JavaScript |
| Camera | HTML5 getUserMedia API |

---

````markdown
## Project Structure

```
attendance-system/
│
├── ML/
│   ├── datasets/            # Student face images (folder per student ID)
│   ├── models/              # encodings.json (trained embeddings)
│   └── src/
│       ├── recognize.py     # FaceRecognizer — detection + matching
│       ├── liveness.py      # EAR blink detection
│       └── train.py         # Training script (run on Kaggle)
│
├── app2/
│   ├── templates/           # All HTML templates
│   ├── models.py            # Database models
│   └── views.py             # Views + ML inference endpoint
│
├── student/
│   ├── settings.py
│   └── urls.py
│
├── manage.py
├── requirements.txt
└── .gitignore
```
````

---

## Setup & Installation

```bash
# 1. Clone
git clone https://github.com/govindsingh00/attendance-system.git
cd attendance-system

# 2. Virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Migrate
python manage.py migrate

# 5. Run
python manage.py runserver
```

---

## Face Recognition Setup

### Step 1 — Collect images
````markdown
```
ML/datasets/
├── 1/   # 30-40 photos of Student ID 1
├── 2/
├── 3/
└── 4/
```
````

### Step 2 — Train (on Kaggle for GPU)
```bash
python ML/src/train.py
```
Generates `ML/models/encodings.json` — normalized ArcFace embeddings per student.

---

## Anti-Spoofing — How Blink Detection Works

MediaPipe detects 468 facial landmarks. 6 landmarks per eye are used to compute Eye Aspect Ratio (EAR):

    EAR = (||p2-p6|| + ||p3-p5||) / (2 x ||p1-p4||)

| Eye State | EAR Value |
|---|---|
| Open eye | 0.25 – 0.35 |
| Blink | drops below 0.22 |
| Printed photo | constant EAR, never blinks, blocked |

System requires at least 1 confirmed blink before running face recognition.

---

## User Roles

**Admin**
- Register students, teachers, courses
- Assign teachers to sections and time slots

**Teacher**
- View assigned classes
- Start face attendance session
- Download CSV attendance sheet

**Student**
- View own attendance percentage per course

---

## Database Models

| Model | Key Fields |
|---|---|
| Studentdata | stid, stname, email, section |
| Teacherdata | tid, name, email, phone |
| Coursedata | cid, crname, duration |
| TeachingAssignment | teacher, course, section, time_slot |
| AttendanceRecord | student, course, date, time_slot, status |
| Logindata | email, password, usertype |

---

## Known Limitations

- Accuracy drops under poor lighting or off-axis face angles
- CPU inference: 2–3s per frame (GPU would reduce to <500ms)
- Blink detection cannot defend against video replay attacks
- Tested on 4 students only — needs larger scale evaluation
- Single organization deployment only

---

## Future Work

- Video replay attack defense using MiniFASNet or rPPG
- GPU deployment for real-time performance
- Per-subject cosine threshold calibration
- Multi-tenant architecture
- Mobile app
- Incremental enrollment without retraining

---

## Research Paper

Published as IEEE-format conference paper:

> **Atmos: An AI-Powered Face Recognition Attendance System with Anti-Spoofing Using ArcFace and Blink Detection**  
> Sachin Gupta, Govind Singh Tanwar, Kashish Sharma, Komal Kumari, Navneet Kumar  
> Lovely Professional University, Jalandhar, Punjab, India

---

## Team

| Name | Role |
|---|---|
| Sachin Gupta | ML Module (ArcFace, Liveness, Anti-Spoofing, Django API) |
| Govind Singh Tanwar | Backend (Django views, models, DB) |
| Kashish Sharma | Security (Authentication) |
| Komal Kumari | Frontend (Templates, UI) |
| Navneet Kumar | Testing, System Design |

**Lovely Professional University, Jalandhar, Punjab, India**  
**Master of Computer Applications (MCA)**