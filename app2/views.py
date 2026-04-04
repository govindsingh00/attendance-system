from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .location_data import location_context
from .models import *
from django.core.files.storage import FileSystemStorage
import os
import time

TIME_SLOTS = (
    ("9-10", "9:00 – 10:00"),
    ("10-11", "10:00 – 11:00"),
    ("11-12", "11:00 – 12:00"),
    ("12-1", "12:00 – 1:00"),
    ("2-3", "2:00 – 3:00"),
    ("3-4", "3:00 – 4:00"),
    ("4-5", "4:00 – 5:00"),
)

TIME_SLOT_CODES = [x[0] for x in TIME_SLOTS]


def _norm_section_key(s):
    return (s or "").strip().lower()


def _courses_for_teacher_assignments(assignments_list, canonical_section):
    """Courses for a section using normalized section text (avoids DB whitespace mismatches)."""
    if not canonical_section:
        return []
    key = _norm_section_key(canonical_section)
    seen = set()
    courses = []
    for a in assignments_list:
        if _norm_section_key(a.section) != key:
            continue
        if a.course_id not in seen:
            seen.add(a.course_id)
            courses.append(a.course)
    return courses


def _slot_choices_for_teacher_assignments(assignments_list, canonical_section, course):
    """Only time slots that exist on a teaching assignment for this section + course."""
    if not canonical_section or not course:
        return []
    labels = dict(TIME_SLOTS)
    key = _norm_section_key(canonical_section)
    allowed = set()
    for a in assignments_list:
        if _norm_section_key(a.section) != key or a.course_id != course.cid:
            continue
        if a.time_slot in labels:
            allowed.add(a.time_slot)
    return [(code, labels[code]) for code, _ in TIME_SLOTS if code in allowed]


def _teacher_assigned_to_slot(assignments_list, canonical_section, course, time_slot):
    key = _norm_section_key(canonical_section)
    for a in assignments_list:
        if (
            _norm_section_key(a.section) == key
            and a.course_id == course.cid
            and a.time_slot == time_slot
        ):
            return True
    return False


def _students_for_section_course(section, course):
    enrolled = StudentCoursedata.objects.filter(crname__iexact=course.crname.strip()).values_list("stid", flat=True)
    enrolled_ids = set()
    for x in enrolled:
        try:
            enrolled_ids.add(int(str(x).strip()))
        except ValueError:
            continue
    if not enrolled_ids:
        return []
    sec_key = _norm_section_key(section)
    matched = []
    for st in Studentdata.objects.filter(stid__in=enrolled_ids).order_by("stname"):
        if _norm_section_key(st.section) == sec_key:
            matched.append(st)
    return matched


def _match_section(allowed_sections, section):
    sec = (section or "").strip()
    for s in allowed_sections:
        if s.lower() == sec.lower():
            return s
    return None

# Create your views here.
def login(request):
    if request.method == "POST":
        em=request.POST["T1"]
        paswrd=request.POST["T2"]
        obj = Logindata.objects.get(email=em,password=paswrd)
        ut=obj.usertype
        request.session["ut"]=ut
        request.session["email"]=em
        if ut=="admin":
            return HttpResponseRedirect("/admin_home/")
        elif ut=="student":
            return HttpResponseRedirect("/student_home/")
        elif ut=="teacher":
            return HttpResponseRedirect("/teacher_home/")
        else:
            return render(request, "Login.html",{"msg":"Either Email or Password is Incorrect"})
    else:
        return render(request,"Login.html")

def logout(request):
    try:
        del request.session["email"]
        del request.session["ut"]
    except:
        pass
    return HttpResponseRedirect("/")

def autherror(request):
    return render(request,"AuthError.html")

def admin_reg(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "admin":
            if request.method=="POST":
                adm = Admindata()
                lgn = Logindata()

                nm=request.POST["t1"]
                a=request.POST["t2"]
                b=request.POST["t3"]
                c=request.POST["t4"]
                d=request.POST["t5"]
                e=request.POST["t6"]
                add=a+" "+b+" "+c+" "+d+" "+e
                mob=request.POST["t7"]
                em=request.POST["t8"]
                paswrd=request.POST["t9"]

                adm.name = nm
                adm.email = em
                adm.contact = mob
                adm.address = add

                lgn.email = em
                lgn.password = paswrd
                lgn.usertype = "admin"

                adm.save()
                lgn.save()
                ctx = location_context()
                ctx["msg"] = "Data Saved"
                return render(request, "AdminReg.html", ctx)
            else:
                return render(request, "AdminReg.html", location_context())
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")


def student_reg(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut != "student":
            if request.method=="POST":
                st = Studentdata()
                lgn = Logindata()

                a=request.POST["t1"]
                b=request.POST["t2"]
                nm=a+" "+b
                fnm=request.POST["t111"]
                dob=request.POST["t3"]
                gender=request.POST["R1"]
                c=request.POST["t4"]
                d=request.POST["t5"]
                e=request.POST["t6"]
                f=request.POST["t7"]
                g=request.POST["t8"]
                add = c +" "+ d +" "+ e+" "+f+" "+g
                lq=request.POST["t9"]
                mob=request.POST["t222"]
                em=request.POST["t11"]
                pswrd=request.POST["t12"]

                st.stname= nm
                st.fname= fnm
                st.dob = dob
                st.gender = gender
                st.address = add
                st.lastquali = lq
                st.contact = mob
                st.email = em
                st.section = request.POST.get("t14", "").strip()

                lgn.email = em
                lgn.password = pswrd
                lgn.usertype = "student"

                st.save()
                lgn.save()

                ctx = location_context()
                ctx["msg"] = "Data Saved"
                return render(request, "StudentReg.html", ctx)
            else:
                return render(request, "StudentReg.html", location_context())
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def teacher_reg(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]

        if ut == "admin":
            courses = Coursedata.objects.all()

            if request.method == "POST":
                try:
                    t = Teacherdata()
                    lgn = Logindata()

                    nm = request.POST["t1"] + " " + request.POST["t2"]
                    add = request.POST["t5"] + " " + request.POST["t6"] + " " + request.POST["t7"] + " " + request.POST["t8"] + " " + request.POST["t9"]

                    em = request.POST["t11"]

                    t.name = nm
                    t.crid = request.POST["t3"]
                    t.email = em
                    t.phone = request.POST["t10"]
                    t.gender = request.POST["R1"]
                    t.dob = request.POST["t4"]
                    t.address = add

                    lgn.email = em
                    lgn.password = request.POST["t12"]
                    lgn.usertype = "teacher"

                    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
                    t.save()
                    lgn.save()

                    if request.FILES.get("photo"):
                        file = request.FILES["photo"]
                        safe_name = os.path.basename(file.name)
                        name, ext = os.path.splitext(safe_name)
                        filename = "%s_%s%s" % (int(time.time()), name[:40] or "photo", ext or ".jpg")
                        filepath = os.path.join(settings.MEDIA_ROOT, filename)
                        with open(filepath, "wb+") as destination:
                            for chunk in file.chunks():
                                destination.write(chunk)
                        ph = Photodata()
                        ph.email = em
                        ph.photo = filename
                        ph.save()

                    ctx = location_context()
                    ctx["msg"] = "Teacher Registered Successfully"
                    ctx["courses"] = courses
                    return render(request, "TeacherReg.html", ctx)
                except IntegrityError:
                    ctx = location_context()
                    ctx["msg"] = "That email is already registered."
                    ctx["courses"] = courses
                    return render(request, "TeacherReg.html", ctx)
            else:
                ctx = location_context()
                ctx["courses"] = courses
                return render(request, "TeacherReg.html", ctx)
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def admin_home(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        em = request.session["email"]
        if ut == "admin":
            adm = Admindata.objects.filter(email=em)
            pic = Photodata.objects.filter(email=em)
            return render(request,"AdminHome.html",{"data":adm,"data1":pic})
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def teacher_home(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        em = request.session["email"]

        if ut == "teacher":
            tchr = Teacherdata.objects.filter(email=em)
            pic = Photodata.objects.filter(email=em)

            return render(request, "TeacherHome.html", {"data": tchr, "data1": pic})
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def editadminprofile(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        em = request.session["email"]
        if ut == "admin":
            admin = Admindata.objects.filter(email=em)
            return render(request, "EditAdmin.html", {"data": admin})
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def editadminprofile1(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "admin":
            if request.method == "POST":
                nm = request.POST["t1"]
                ad = request.POST["t2"]
                mob = request.POST["t3"]
                em = request.POST["t4"]

                data = Admindata.objects.get(email=em)

                data.name = nm
                data.address = ad
                data.contact = mob

                data.save()
                return render(request, "EditAdmin.html", {"msg": "Profile Updated Successfully"})
            else:
                return HttpResponseRedirect("/admin_home/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def admin_pass_change(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        em = request.session["email"]
        if ut == "admin":
            data = Logindata.objects.filter(email=em)
            return render(request, "AdminPassChange.html", {"data":data})
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def admin_pass_change1(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        em = request.session["email"]
        if ut == "admin":
            if request.method == "POST":
                old = request.POST["t1"]
                new = request.POST["t2"]
                ACC = Logindata.objects.get(email=em,password=old)
                ACC.password = new
                ACC.save()
                return render(request, "AdminPassChange.html", {"msg":"PASSWORD CHANGED"})
            else:
                return HttpResponseRedirect("/admin_home/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def student_home(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        em = request.session["email"]
        if ut == "student":
            std = Studentdata.objects.filter(email=em)
            pic = Photodata.objects.filter(email=em)
            return render(request,"StudentHome.html",{"data":std,"data1":pic})
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def editstprofile(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "student":
            if request.method == "POST":
                sid = request.POST["S1"]
                std = Studentdata.objects.filter(stid=sid)
                if ut == "admin":
                    return render(request,"EditStudentad.html",{"data":std})

                elif ut == "student":
                    return render(request, "EditStudent.html", {"data": std})
            else:
                return HttpResponseRedirect("/student_home/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def editstprofile1(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "student":
            if request.method == "POST":
                sid = request.POST["t1"]
                add = request.POST["t6"]
                cont = request.POST["t8"]

                std = Studentdata.objects.get(stid=sid)

                std.address = add
                std.contact = cont

                std.save()
                if ut == "admin":
                    return render(request, "EditStudentad.html", {"msg": "details edited Successfully"})

                elif ut == "student":
                    return render(request, "EditStudent.html", {"msg": "details edited Successfully"})
            else:
                return HttpResponseRedirect("/student_home/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def student_pass_change(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "student":
            if request.method=="POST":
                sid = request.POST["S1"]
                stdata = Studentdata.objects.filter(stid=sid)
                return render(request,"StudentPassChange.html",{"data":stdata})
            else:
                return HttpResponseRedirect("/student_home/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def student_pass_change1(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "student":
            if request.method=="POST":
                em = request.POST["E1"]
                old = request.POST["t1"]
                new = request.POST["t2"]
                stdata = Logindata.objects.get(email=em,password=old)
                stdata.password = new
                stdata.save()
                return render(request,"StudentPassChange.html",{"msg":"Password Changed Successfully"})
            else:
                return HttpResponseRedirect("/student_home/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def course_reg(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "admin":
            if request.method == "POST":
                crse = Coursedata()
                cr = request.POST["t1"]
                dr = request.POST["t2"]
                rmk = request.POST["t3"]

                crse.crname = cr.upper()
                crse.fee = ""
                crse.duration = dr
                crse.remark = rmk

                crse.save()
                return render(request, "CourseReg.html",{"msg":"Course Registered Succesfully"})
            else:
                return render(request, "CourseReg.html")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def allcourses(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut=="admin":
            crdt = Coursedata.objects.all()
            return render(request,"AllCourses.html",{"data":crdt})
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def edit_course(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "admin":
            if request.method == "POST":
                crseid=request.POST["C1"]
                crdata = Coursedata.objects.filter(cid=crseid)
                return render(request,"EditCourse.html",{"data":crdata})
            else:
                return HttpResponseRedirect("/allcourses/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def edit_course1(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "admin":
            if request.method == "POST":
                crseid=request.POST["C1"]
                nm = request.POST["t1"]
                dr = request.POST["t2"]
                rm = request.POST["t3"]

                crdata = Coursedata.objects.get(cid=crseid)

                crdata.crname = nm
                crdata.fee = ""
                crdata.duration = dr
                crdata.remark = rm

                crdata.save()

                return render(request,"EditCourse.html",{"mssg":"Course Updated Successfully"})
            else:
                return HttpResponseRedirect("/allcourses/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def delete_course(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "admin":
            if request.method == "POST":
                crseid=request.POST["C1"]
                crdata = Coursedata.objects.filter(cid=crseid)
                return render(request,"DeleteCourse.html",{"data":crdata})
            else:
                return HttpResponseRedirect("/allcourses/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def delete_course1(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "admin":
            if request.method == "POST":
                crseid=request.POST["C1"]

                crdata = Coursedata.objects.get(cid=crseid)

                crdata.delete()

                return render(request,"DeleteCourse.html",{"mssg":"Course Deleted Successfully"})
            else:
                return HttpResponseRedirect("/allcourses/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def alladmins(request):
    records = Admindata.objects.all()
    photo = Photodata.objects.all()
    return render(request,'AllAdmins.html',{"data":records,"photo":photo})

def allteachers(request):
    records = Teacherdata.objects.all()
    data = []

    for t in records:
        try:
            p = Photodata.objects.get(email=t.email)
            photo = p.photo
        except:
            photo = None

        data.append({
            "teacher": t,
            "photo": photo
        })

    return render(request, 'AllTeachers.html', {"data": data})

# for photo
def uploadphoto(request):
    if request.session.has_key("email"):
        em = request.session["email"]
        ut = request.session["ut"]
        if request.method == "POST":
            file=request.FILES["F1"]
            path = os.path.basename(file.name)
            file_ext = os.path.splitext(path)[1][1:]
            filename = str(int(time.time()))+'.'+file_ext

            fs = FileSystemStorage()

            fs.save(filename, file)

            obj = Photodata()

            obj.email = em
            obj.photo = filename
            obj.save()

            if(ut=="admin"):
                return HttpResponseRedirect("/admin_home/")
            elif(ut=="teacher"):
                return HttpResponseRedirect("/teacher_home/")

        else:

            return render(request,"UploadPhoto.html")

    else:
        return HttpResponseRedirect("/autherror/")

def chngephoto(request):
    if request.session.has_key("email"):
        em = request.session["email"]
        ut = request.session["ut"]
        if request.method == "POST":
            pic = request.POST["C1"]
            dlt = Photodata.objects.filter(photo=pic,email=em)
            return render(request, "ChangePhoto.html",{"data":dlt})
        else:
            if ut == "teacher":
                return HttpResponseRedirect("/teacher_home/")
            return HttpResponseRedirect("/admin_home/")
    else:
        return HttpResponseRedirect("/autherror/")

def chngephoto1(request):
    if request.session.has_key("email"):
        em = request.session["email"]
        ut = request.session["ut"]
        if request.method == "POST":
            fs1 = FileSystemStorage()
            old = request.POST["IMG1"]
            pic = Photodata.objects.get(photo=old,email=em)
            picname = pic.photo
            fs1.delete(picname)

            file=request.FILES["F1"]
            path = os.path.basename(file.name)
            file_ext = os.path.splitext(path)[1][1:]
            filename = str(int(time.time()))+'.'+file_ext
            fs = FileSystemStorage()
            fs.save(filename, file)

            pic.photo = filename
            pic.save()
            if ut=="admin":
                return HttpResponseRedirect("/admin_home/")

            elif ut=="student":
                return HttpResponseRedirect("/student_home/")
            elif ut=="teacher":
                return HttpResponseRedirect("/teacher_home/")
        else:
            if ut=="admin":
                return render(request,"ChangePhoto.html")

    else:
        return HttpResponseRedirect("/autherror/")

def deletephoto(request):
    if request.session.has_key("email"):
        em = request.session["email"]
        ut = request.session["ut"]
        if request.method == "POST":
            pic = request.POST["C1"]
            dlt = Photodata.objects.filter(photo=pic,email=em)
            if ut=="admin":
                return render(request, "DeletePhoto.html",{"data":dlt})

        else:
            return HttpResponseRedirect("/admin_home/")
    else:
        return HttpResponseRedirect("/autherror/")

def deletephoto1(request):
    if request.session.has_key("email"):
        em = request.session["email"]
        ut = request.session["ut"]
        if request.method == "POST":
            fs1 = FileSystemStorage()
            old = request.POST["IMG1"]
            pic = Photodata.objects.get(photo=old,email=em)
            picname = pic.photo
            fs1.delete(picname)
            pic.delete()
            if ut=="admin":
                return HttpResponseRedirect("/admin_home/")

            elif ut=="student":
                return HttpResponseRedirect("/student_home/")
            elif ut=="teacher":
                return HttpResponseRedirect("/teacher_home/")
        else:
            if ut=="admin":
                return render(request,"ChangePhoto.html")

    else:
        return HttpResponseRedirect("/autherror/")

# for student
def student_course_info(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "student":
            if request.method=="POST":
                sid = request.POST["S1"]
                stcrse = StudentCoursedata.objects.filter(stid=sid)
                return render(request,"StudentCourseInfo.html",{"data1":stcrse})
            else:
                return HttpResponseRedirect("/student_home/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

# for student by admin
def studentuploadphoto(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut != "student":
            if request.method == "POST":
                file = request.FILES["F1"]
                em = request.POST["E1"]

                path = os.path.basename(file.name)
                file_ext = os.path.splitext(path)[1][1:]
                filename = str(int(time.time())) + '.' + file_ext
                fs = FileSystemStorage()
                fs.save(filename, file)
                obj = Photodata()
                obj.email = em
                obj.photo = filename
                obj.save()
                if ut == "admin":
                    return HttpResponseRedirect("/allstudentsAD/")
                else:
                    return HttpResponseRedirect("/allstudentsACC/")
            else:
                return HttpResponseRedirect("/allstudentsAD/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def studentchngephoto(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut != "student":
            if request.method == "POST":
                pic = request.POST["C1"]
                em = request.POST["C2"]
                dlt = Photodata.objects.filter(photo=pic, email=em)

                if ut == "admin":
                    return render(request, "ChangePhotoStudent1.html", {"data": dlt})
            else:
                if ut == "admin":
                    return HttpResponseRedirect("/allstudentsAD/")

        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def studentchngephoto1(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut != "student":
            if request.method == "POST":
                fs1 = FileSystemStorage()
                old = request.POST["IMG1"]
                em = request.POST["E1"]
                pic = Photodata.objects.get(photo=old, email=em)
                picname = pic.photo
                fs1.delete(picname)

                file = request.FILES["F1"]
                path = os.path.basename(file.name)
                file_ext = os.path.splitext(path)[1][1:]
                filename = str(int(time.time())) + '.' + file_ext
                fs = FileSystemStorage()
                fs.save(filename, file)
                pic.photo = filename
                pic.save()
                if ut == "admin":
                    return HttpResponseRedirect("/allstudentsAD/")

            else:
                if ut=="admin":
                    return HttpResponseRedirect("/allstudentsAD/")

        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def studentdeletephoto(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut !="student":
            if request.method == "POST":
                pic = request.POST["C1"]
                em = request.POST["C2"]
                dlt = Photodata.objects.filter(photo=pic,email=em)
                return render(request, "DeletePhotoStudent.html",{"data":dlt})
            else:
                if ut=="admin":
                    return HttpResponseRedirect("/allstudentsAD/")

        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def studentdeletephoto1(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut != "student":
            if request.method == "POST":
                fs1 = FileSystemStorage()
                old = request.POST["IMG1"]
                em = request.POST["E1"]
                pic = Photodata.objects.get(photo=old,email=em)
                picname = pic.photo
                fs1.delete(picname)
                pic.delete()
                if ut=="admin":
                    return HttpResponseRedirect("/allstudentsAD/")
                else:
                    return HttpResponseRedirect("/allstudentsACC/")
            else:
                return render(request,"ChangePhoto.html")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def ADviewstudent(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut=="admin":
            if request.method == "POST":
                sid = request.POST["S1"]
                em = request.POST["S2"]

                pic = Photodata.objects.filter(email=em)
                stprofile = Studentdata.objects.filter(stid=sid)
                stcrse = StudentCoursedata.objects.filter(stid=sid)
                return render(request,"ADviewstudent.html",{"data1":stprofile,"data2":stcrse,"data4":pic})
            else:
                return HttpResponseRedirect("/admin_home/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def deletestudentprofile(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut=="admin":
            if request.method == "POST":
                sid = request.POST["S1"]
                em = request.POST["S2"]
                try:
                    data1 = Studentdata.objects.filter(stid=sid, email=em)
                    data2 = StudentCoursedata.objects.filter(stid=sid)
                    data3 = Installmentdata.objects.filter(stid=sid)
                    data4 = Photodata.objects.filter(email=em)
                    return render(request,"DeleteStudentProfile.html",{"data1":data1,"data2":data2,"data3":data3,"data4":data4,})
                except:
                    return render(request, "DeleteStudentProfile.html",
                                  {"msg":"No Data FOUND"})
            else:
                return HttpResponseRedirect("/allstudentsAD/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def deletestudentprofile1(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut=="admin":
            if request.method == "POST":
                sid = request.POST["S1"]
                em = request.POST["S2"]
                data1 = Studentdata.objects.get(stid=sid,email=em)
                data2 = Logindata.objects.get(email=em)
                data3 = StudentCoursedata.objects.filter(stid=sid)
                data4 = Installmentdata.objects.filter(stid=sid)

                data1.delete()
                data2.delete()
                if data3:
                    data3.delete()
                if data4:
                    data4.delete()

                old = request.POST["IMG1"]
                if old:
                    fs1 = FileSystemStorage()
                    pic = Photodata.objects.get(photo=old, email=em)
                    picname = pic.photo
                    fs1.delete(picname)
                    pic.delete()
                return render(request,"DeleteStudentProfile.html",{"msg":"Student All Data Deleted Succeffully"})
            else:
                return HttpResponseRedirect("/allstudentsAD/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def allstudentsAD(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut=="admin":
            stdata = Studentdata.objects.all()
            return render(request,"AllStudentsAD.html",{"data":stdata})
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def studentcourseadd(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "admin":
            if request.method=="POST":
                obj = Coursedata.objects.all()
                list=[]
                sid = request.POST["A1"]
                list.append(sid)
                return render(request,"StudentCourseregADMIN.html",{"data":obj,"data1":list})
            else:
                return HttpResponseRedirect("/ADviewstudent/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def studentcourseadd1(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "admin":
            if request.method=="POST":
                sid = request.POST["A1"]
                crnm = request.POST["t1"]
                joind = request.POST["t3"]
                rmk = request.POST["t4"]

                obj = StudentCoursedata()
                obj.crname = crnm
                obj.fee = ""
                obj.joining = joind
                obj.remark = rmk
                obj.stid = sid

                obj.save()

                return render(request,"StudentCourseregADMIN.html",{"msg":"Course Added in Student Profile"})
            else:
                return HttpResponseRedirect("/ADviewstudent/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def editstudentcoursedata(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "admin":
            if request.method=="POST":
                stid = request.POST["A1"]
                crid = request.POST["A2"]
                crdata = StudentCoursedata.objects.filter(st_crid=crid,stid=stid)
                allcrse = Coursedata.objects.all()
                return render(request,"EditStudentCourseData.html",{"data":crdata,"data1":allcrse})
            else:
                return HttpResponseRedirect("/ADviewstudent/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def editstudentcoursedata1(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "admin":
            if request.method=="POST":
                crid = request.POST["T1"]
                stid = request.POST["T2"]
                crse = request.POST["T3"]
                dt = request.POST["T4"]
                rmk = request.POST["T5"]

                data = StudentCoursedata.objects.get(st_crid=crid,stid=stid)

                data.crname = crse
                data.fee = ""
                data.joining = dt
                data.remark = rmk

                data.save()
                return render(request,"EditStudentCourseData.html",{"msg":"Course Updated Successfully"})
            else:
                return HttpResponseRedirect("/ADviewstudent/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def deletestudentcoursedata(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "admin":
            if request.method=="POST":
                stid = request.POST["A1"]
                crid = request.POST["A2"]
                crdata = StudentCoursedata.objects.filter(st_crid=crid,stid=stid)
                return render(request,"DeleteStudentCourseData.html",{"data":crdata})
            else:
                return HttpResponseRedirect("/ADviewstudent/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def deletestudentcoursedata1(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "admin":
            if request.method=="POST":
                crid = request.POST["T1"]
                stid = request.POST["T2"]
                crdata = StudentCoursedata.objects.filter(st_crid=crid, stid=stid)
                trdata = Installmentdata.objects.filter(stcrid=crid, stid=stid)

                crdata.delete()
                trdata.delete()

                return render(request, "DeleteStudentCourseData.html", {"msg": "Course Data Deleted Successfully"})
            else:
                return HttpResponseRedirect("/ADviewstudent/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def editstdata(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut != "student":
            if request.method=="POST":
                stid = request.POST["STID1"]
                stdata = Studentdata.objects.filter(stid=stid)
                if ut == "admin":
                    return render(request,"EditStDataad.html",{"data":stdata})

            else:
                if ut == "admin":
                    return HttpResponseRedirect("/ADviewstudent/")
                else:
                    return HttpResponseRedirect("/allstudentsACC/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")

def editstdata1(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut != "student":
            if request.method=="POST":
                sid = request.POST["T1"]
                nm = request.POST["T2"]
                fnm = request.POST["T3"]
                dob = request.POST["T4"]
                gndr = request.POST["T5"]
                add = request.POST["T6"]
                quali = request.POST["T7"]
                mob = request.POST["T8"]
                em = request.POST["T9"]

                data = Studentdata.objects.get(stid=sid)

                data.stname = nm
                data.fname  = fnm
                data.dob = dob
                data.gender = gndr
                data.address = add
                data.lastquali = quali
                data.contact = mob
                data.email = em
                data.section = request.POST.get("T10", "").strip()

                data.save()
                if ut == "admin":
                    return render(request,"EditStDataad.html",{"msg":"Student Data Updated Successfully"})

            else:
                if ut == "admin":
                    return HttpResponseRedirect("/ADviewstudent/")
                else:
                    return HttpResponseRedirect("/viewstudentACC/")
        else:
            return HttpResponseRedirect("/autherror/")
    else:
        return HttpResponseRedirect("/autherror/")


def editteacherprofile(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        em = request.session["email"]
        if ut == "teacher":
            rows = Teacherdata.objects.filter(email=em)
            return render(request, "EditTeacher.html", {"data": rows})
        return HttpResponseRedirect("/autherror/")
    return HttpResponseRedirect("/autherror/")


def editteacherprofile1(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        if ut == "teacher" and request.method == "POST":
            t = Teacherdata.objects.get(email=request.POST["E1"])
            t.name = request.POST["t1"]
            t.phone = request.POST["t2"]
            t.address = request.POST["t3"]
            t.save()
            return render(request, "EditTeacher.html", {"msg": "Profile updated successfully"})
        return HttpResponseRedirect("/teacher_home/")
    return HttpResponseRedirect("/autherror/")


def teacher_pass_change(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        em = request.session["email"]
        if ut == "teacher":
            data = Logindata.objects.filter(email=em)
            return render(request, "TeacherPassChange.html", {"data": data})
        return HttpResponseRedirect("/autherror/")
    return HttpResponseRedirect("/autherror/")


def teacher_pass_change1(request):
    if request.session.has_key("email"):
        ut = request.session["ut"]
        em = request.session["email"]
        if ut == "teacher" and request.method == "POST":
            old = request.POST["t1"]
            new = request.POST["t2"]
            acc = Logindata.objects.get(email=em, password=old)
            acc.password = new
            acc.save()
            return render(request, "TeacherPassChange.html", {"msg": "Password changed"})
        return HttpResponseRedirect("/teacher_home/")
    return HttpResponseRedirect("/autherror/")


def mark_attendance(request):
    if not request.session.has_key("email") or request.session.get("ut") != "teacher":
        return HttpResponseRedirect("/autherror/")
    em = request.session["email"]
    teacher = Teacherdata.objects.filter(email__iexact=em).first()
    if not teacher:
        return HttpResponseRedirect("/autherror/")
    assignments_list = list(
        TeachingAssignment.objects.filter(teacher=teacher).select_related("course")
    )
    sections = sorted(
        {(a.section or "").strip() for a in assignments_list if (a.section or "").strip()}
    )

    raw_section = request.GET.get("section") or request.POST.get("section") or ""
    section = _match_section(sections, raw_section) or ""
    cid = request.GET.get("cid") or request.POST.get("cid")
    time_slot = (request.GET.get("time_slot") or request.POST.get("time_slot") or "").strip()

    selected_course = None
    if cid:
        try:
            selected_course = Coursedata.objects.get(cid=int(cid))
        except (ValueError, TypeError, Coursedata.DoesNotExist):
            pass

    slot_choices = _slot_choices_for_teacher_assignments(
        assignments_list, section, selected_course
    )
    courses_for_section = _courses_for_teacher_assignments(assignments_list, section)

    ctx = {
        "sections": sections,
        "time_slots": slot_choices,
        "section": section,
        "cid": cid,
        "time_slot": time_slot,
        "student_rows": [],
        "selected_course": selected_course,
        "courses_for_section": courses_for_section,
        "has_teaching_assignments": bool(sections),
    }

    if request.method == "POST" and request.POST.get("action") == "save":
        if not section:
            ctx["error"] = "Invalid section."
            ctx["time_slots"] = _slot_choices_for_teacher_assignments(
                assignments_list, section, selected_course
            )
            return render(request, "MarkAttendance.html", ctx)
        try:
            course = Coursedata.objects.get(cid=int(cid))
        except (ValueError, TypeError, Coursedata.DoesNotExist):
            ctx["error"] = "Invalid course."
            ctx["time_slots"] = _slot_choices_for_teacher_assignments(
                assignments_list, section, selected_course
            )
            return render(request, "MarkAttendance.html", ctx)
        if time_slot not in TIME_SLOT_CODES:
            ctx["error"] = "Invalid time slot."
            ctx["selected_course"] = course
            ctx["time_slots"] = _slot_choices_for_teacher_assignments(
                assignments_list, section, course
            )
            return render(request, "MarkAttendance.html", ctx)
        if not _teacher_assigned_to_slot(assignments_list, section, course, time_slot):
            ctx["error"] = "You are not assigned to teach this section, course, and time slot."
            ctx["selected_course"] = course
            ctx["time_slots"] = _slot_choices_for_teacher_assignments(
                assignments_list, section, course
            )
            return render(request, "MarkAttendance.html", ctx)

        today = timezone.localdate()
        students = list(_students_for_section_course(section, course))
        for st in students:
            key = "status_%s" % st.stid
            status = request.POST.get(key, "Absent")
            if status not in ("Present", "Absent"):
                status = "Absent"
            AttendanceRecord.objects.update_or_create(
                student=st,
                course=course,
                attendance_date=today,
                time_slot=time_slot,
                defaults={
                    "section": section,
                    "status": status,
                    "teacher": teacher,
                },
            )
        ctx["msg"] = "Attendance saved."
        ctx["students"] = students
        existing = _attendance_map_for_session(students, course, today, time_slot)
        ctx["existing"] = existing
        ctx["student_rows"] = [{"st": st, "status": existing.get(st.stid, "")} for st in students]
        ctx["courses_for_section"] = _courses_for_teacher_assignments(assignments_list, section)
        ctx["selected_course"] = course
        ctx["time_slots"] = _slot_choices_for_teacher_assignments(assignments_list, section, course)
        return render(request, "MarkAttendance.html", ctx)

    students = []
    existing = {}
    today = timezone.localdate()
    slot_choices_for_view = _slot_choices_for_teacher_assignments(
        assignments_list, section, selected_course
    )
    allowed_slots = {c for c, _ in slot_choices_for_view}

    if section and selected_course and time_slot:
        if time_slot not in TIME_SLOT_CODES:
            ctx["error"] = "Invalid time slot."
        elif time_slot not in allowed_slots:
            ctx["error"] = (
                "This time slot is not assigned to you for this section and course. "
                "Ask an admin to add it on Teaching assignments."
            )
        else:
            students = list(_students_for_section_course(section, selected_course))
            existing = _attendance_map_for_session(students, selected_course, today, time_slot)

    ctx["courses_for_section"] = _courses_for_teacher_assignments(assignments_list, section)
    ctx["students"] = students
    ctx["existing"] = existing
    ctx["student_rows"] = [{"st": st, "status": existing.get(st.stid, "")} for st in students]
    ctx["selected_course"] = selected_course
    ctx["time_slots"] = slot_choices_for_view
    if request.GET.get("msg") == "saved":
        ctx["msg"] = "Attendance saved."
    return render(request, "MarkAttendance.html", ctx)


def _attendance_map_for_session(students, course, day, time_slot):
    out = {}
    if not students:
        return out
    ids = [s.stid for s in students]
    recs = AttendanceRecord.objects.filter(
        student_id__in=ids,
        course=course,
        attendance_date=day,
        time_slot=time_slot,
    )
    for r in recs:
        out[r.student_id] = r.status
    return out


def take_attendance_face(request):
    if not request.session.has_key("email") or request.session.get("ut") != "teacher":
        return HttpResponseRedirect("/autherror/")
    return render(
        request,
        "TakeAttendanceFace.html",
        {
            "section": request.GET.get("section", ""),
            "cid": request.GET.get("cid", ""),
            "time_slot": request.GET.get("time_slot", ""),
        },
    )


def student_attendance(request):
    if not request.session.has_key("email") or request.session.get("ut") != "student":
        return HttpResponseRedirect("/autherror/")
    em = request.session["email"]
    student = get_object_or_404(Studentdata, email=em)
    records = AttendanceRecord.objects.filter(student=student).select_related("course")
    by_course = {}
    for r in records:
        cid = r.course_id
        if cid not in by_course:
            by_course[cid] = {"name": r.course.crname, "total": 0, "present": 0}
        by_course[cid]["total"] += 1
        if r.status.lower() == "present":
            by_course[cid]["present"] += 1

    rows = []
    total_sessions = 0
    total_present = 0
    for cid, d in sorted(by_course.items(), key=lambda x: x[1]["name"]):
        t = d["total"]
        p = d["present"]
        pct = round(100.0 * p / t, 1) if t else 0.0
        rows.append({"name": d["name"], "total": t, "present": p, "pct": pct})
        total_sessions += t
        total_present += p

    overall_pct = round(100.0 * total_present / total_sessions, 1) if total_sessions else 0.0
    return render(
        request,
        "StudentAttendance.html",
        {
            "rows": rows,
            "overall_pct": overall_pct,
            "total_sessions": total_sessions,
            "total_present": total_present,
        },
    )


def _teaching_assignments_page_context(error=None):
    return {
        "error": error,
        "teachers": Teacherdata.objects.all().order_by("name"),
        "courses": Coursedata.objects.all().order_by("crname"),
        "assignments": TeachingAssignment.objects.select_related("teacher", "course").order_by(
            "section", "course__crname", "time_slot"
        ),
        "time_slots": TIME_SLOTS,
    }


def teaching_assignments(request):
    if not request.session.has_key("email") or request.session.get("ut") != "admin":
        return HttpResponseRedirect("/autherror/")
    return render(request, "TeachingAssignments.html", _teaching_assignments_page_context())


def teaching_assignment_add(request):
    if not request.session.has_key("email") or request.session.get("ut") != "admin":
        return HttpResponseRedirect("/autherror/")
    if request.method != "POST":
        return HttpResponseRedirect("/teaching_assignments/")
    tid = request.POST.get("tid")
    cid = request.POST.get("cid")
    section = (request.POST.get("section") or "").strip()
    subject = (request.POST.get("subject") or "").strip()
    time_slot = (request.POST.get("time_slot") or "").strip()
    try:
        t = Teacherdata.objects.get(tid=int(tid))
        c = Coursedata.objects.get(cid=int(cid))
    except (ValueError, TypeError, Teacherdata.DoesNotExist, Coursedata.DoesNotExist):
        return render(
            request,
            "TeachingAssignments.html",
            _teaching_assignments_page_context("Invalid teacher or course."),
        )
    if not section:
        return render(
            request,
            "TeachingAssignments.html",
            _teaching_assignments_page_context("Section is required."),
        )
    if time_slot not in TIME_SLOT_CODES:
        return render(
            request,
            "TeachingAssignments.html",
            _teaching_assignments_page_context("Select a valid time slot."),
        )
    if not subject:
        subject = c.crname
    TeachingAssignment.objects.update_or_create(
        teacher=t,
        course=c,
        section=section,
        time_slot=time_slot,
        defaults={"subject": subject},
    )
    return HttpResponseRedirect("/teaching_assignments/")


def teaching_assignment_delete(request):
    if not request.session.has_key("email") or request.session.get("ut") != "admin":
        return HttpResponseRedirect("/autherror/")
    if request.method != "POST":
        return HttpResponseRedirect("/teaching_assignments/")
    try:
        aid = int(request.POST.get("aid"))
        TeachingAssignment.objects.filter(aid=aid).delete()
    except (ValueError, TypeError):
        pass
    return HttpResponseRedirect("/teaching_assignments/")
