from django.db import models
# Create your models here.

class Admindata(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    email = models.CharField(max_length=100,primary_key=True)
    def __str__(self):
        return self.name

class Coursedata(models.Model):
    cid = models.AutoField(primary_key=True)
    crname = models.CharField(max_length=100)
    fee = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    remark = models.CharField(max_length=100000)
    def __str__(self):
        return "%s %s" % (self.cid,self.crname)
class Teacherdata(models.Model):
    tid = models.AutoField(primary_key=True)
    crid = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=10)
    dob = models.DateField()
    address = models.TextField()

    joining_date = models.DateField(auto_now_add=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return "%s %s" % (self.tid, self.name)

class Studentdata(models.Model):
    stid = models.AutoField(primary_key=True)
    stname = models.CharField(max_length=100)
    fname = models.CharField(max_length=100)
    dob = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    lastquali = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    section = models.CharField(max_length=50, blank=True, default="")
    def __str__(self):
        return self.stname


class TeachingAssignment(models.Model):
    """Which teacher teaches which course/subject for which section and time slot (batch)."""
    aid = models.AutoField(primary_key=True)
    teacher = models.ForeignKey("Teacherdata", on_delete=models.CASCADE, related_name="assignments")
    course = models.ForeignKey("Coursedata", on_delete=models.CASCADE, related_name="teaching_assignments")
    section = models.CharField(max_length=50)
    time_slot = models.CharField(max_length=32, default="9-10")
    subject = models.CharField(max_length=200)

    class Meta:
        unique_together = ("teacher", "course", "section", "time_slot")

    def __str__(self):
        return "%s — %s sec %s @ %s" % (self.course.crname, self.section, self.time_slot, self.teacher.name)


class AttendanceRecord(models.Model):
    arid = models.AutoField(primary_key=True)
    student = models.ForeignKey(Studentdata, on_delete=models.CASCADE, related_name="attendance_records")
    course = models.ForeignKey(Coursedata, on_delete=models.CASCADE, related_name="attendance_records")
    section = models.CharField(max_length=50)
    attendance_date = models.DateField()
    time_slot = models.CharField(max_length=32)
    status = models.CharField(max_length=16)
    teacher = models.ForeignKey("Teacherdata", on_delete=models.CASCADE, related_name="marked_attendance")

    class Meta:
        unique_together = ("student", "course", "attendance_date", "time_slot")

    def __str__(self):
        return "%s %s %s" % (self.student.stname, self.attendance_date, self.status)

class Logindata(models.Model):
    email = models.CharField(max_length=100,primary_key=True)
    password = models.CharField(max_length=100)
    usertype = models.CharField(max_length=100)
    def __str__(self):
        return self.email



class StudentCoursedata(models.Model):
    st_crid = models.AutoField(primary_key=True)
    stid = models.CharField(max_length=100)
    crname = models.CharField(max_length=100)
    fee = models.CharField(max_length=100)
    joining = models.CharField(max_length=100)
    remark = models.CharField(max_length=100)
    def __str__(self):
        return "%s %s" % (self.st_crid,self.crname)

class Installmentdata(models.Model):
    tid = models.AutoField(primary_key=True)
    stid = models.CharField(max_length=100)
    stcrid = models.CharField(max_length=100)
    inst = models.CharField(max_length=100)
    sub_date = models.CharField(max_length=100)
    remark = models.CharField(max_length=100)
    def __str__(self):
        return "%s" % (self.tid)

class Photodata(models.Model):
    photo = models.CharField(max_length=100)
    email = models.CharField(max_length=100,primary_key=True)
    def __str__(self):
        return self.email
