"""
URL configuration for student project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app2.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin_reg/', admin_reg),

    path('', home),
    path('aboutus/', about),
    path('contact/', contact),
    path('student_reg/', student_reg),
    path('course_reg/', course_reg),
    path('allcourses/', allcourses),
    path('login/', login),
    path('logout/', logout),
    path('autherror/', autherror),
    path('admin_home/', admin_home),

    path('student_home/', student_home),
    path('alladmins/', alladmins),

    path('edit_course/', edit_course),
    path('edit_course1/', edit_course1),
    path('delete_course/', delete_course),
    path('delete_course1/', delete_course1),
    path('editstprofile/', editstprofile),
    path('editstprofile1/', editstprofile1),
    path('student_pass_change/', student_pass_change),
    path('student_pass_change1/', student_pass_change1),
    path('uploadphoto/', uploadphoto),
    path('chngephoto/', chngephoto),
    path('chngephoto1/', chngephoto1),
    path('deletephoto/', deletephoto),
    path('deletephoto1/', deletephoto1),
    path('editadminprofile/', editadminprofile),
    path('editadminprofile1/', editadminprofile1),
    path('admin_pass_change/', admin_pass_change),
    path('admin_pass_change1/', admin_pass_change1),
    path('allstudentsAD/', allstudentsAD),
    path('ADviewstudent/', ADviewstudent),
    path('deletestudentprofile/', deletestudentprofile),
    path('deletestudentprofile1/', deletestudentprofile1),
    path('studentcourseadd/', studentcourseadd),
    path('studentcourseadd1/', studentcourseadd1),

    path('teacher_reg/', teacher_reg),
    path('allteachers/', allteachers),
    path('teacher_home/', teacher_home),
    path('mark_attendance/', mark_attendance),
    path('mark_attendance/face/', take_attendance_face),
    path('editteacherprofile/', editteacherprofile),
    path('editteacherprofile1/', editteacherprofile1),
    path('teacher_pass_change/', teacher_pass_change),
    path('teacher_pass_change1/', teacher_pass_change1),

    path('student_attendance/', student_attendance),

    path('teaching_assignments/', teaching_assignments),
    path('teaching_assignment_add/', teaching_assignment_add),
    path('teaching_assignment_delete/', teaching_assignment_delete),

    path('studentuploadphoto/', studentuploadphoto),
    path('studentchngephoto/', studentchngephoto),
    path('studentchngephoto1/', studentchngephoto1),
    path('studentdeletephoto/', studentdeletephoto),
    path('studentdeletephoto1/', studentdeletephoto1),
    path('editstudentcoursedata/', editstudentcoursedata),
    path('editstudentcoursedata1/', editstudentcoursedata1),
    path('deletestudentcoursedata/', deletestudentcoursedata),
    path('deletestudentcoursedata1/', deletestudentcoursedata1),
    path('editstdata/', editstdata),
    path('editstdata1/', editstdata1),
    path('student_course_info/', student_course_info),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
