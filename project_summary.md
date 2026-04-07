# Project Summary
## E-Attendance System

## Project Goal
Build a web-based attendance system that uses
face recognition to automatically mark attendance
for students and employees.

## Problem Being Solved
Manual attendance is slow and error prone.
Students can proxy for each other.
Paper records get lost or damaged.
No real time reporting available.

## Our Solution
Automated face recognition marks attendance.
All data stored securely in PostgreSQL.
Teachers get instant reports anytime.
Admin manages everything from one panel.

## Team Responsibilities
- Govind Singh: Backend Django API
- Navneet Kumar: System Design and Architecture
- ML Teammate: Face Recognition Python Module
- Frontend Teammate: React UI Development
- Database Teammate: PostgreSQL Setup

## System Design Decisions Made
1. Chose PostgreSQL over SQLite for multi user support
2. Chose React over plain HTML for dynamic UI
3. Used JWT over sessions for stateless auth
4. Single USER table with role field for all user types
5. Separate FACE_LOG table for ML audit trail
6. REST API design for loose coupling between modules

## Key Design Principles Followed
- Separation of concerns
- Single responsibility per module
- Loose coupling between components
- Role based access control
- Audit trail for all face detections

## Expected Outcomes
- 90 percent reduction in attendance time
- Zero proxy attendance possible
- Real time reports for teachers
- Secure and scalable system
- Easy to maintain and extend
