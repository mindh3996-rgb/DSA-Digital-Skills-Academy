from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.home,
        name="home"
    ),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

    path(
        "register/",
        views.register_student,
        name="register_student"
    ),

    path(
        "login/",
        views.student_login,
        name="student_login"
    ),

    path(
        "dashboard/",
        views.student_dashboard,
        name="student_dashboard"
    ),

    path(
        "profile/edit/",
        views.edit_profile,
        name="edit_profile"
    ),

    path(
        "logout/",
        views.student_logout,
        name="student_logout"
    ),
    path(
    "courses/",
    views.courses,
    name="courses"
),

path(
    "courses/<slug:slug>/",
    views.course_detail,
    name="course_detail"
),
path(
    "courses/<slug:course_slug>/lecture/<int:lecture_id>/",
    views.lecture_detail,
    name="lecture_detail"
),
path(
    "courses/<slug:course_slug>/assignments/",
    views.assignments,
    name="assignments"
),
path(
    "assignment/<int:assignment_id>/submit/",
    views.submit_assignment,
    name="submit_assignment"
),
path(
    "teacher/dashboard/",
    views.teacher_dashboard,
    name="teacher_dashboard"
),
path(
    "teacher/submission/<int:submission_id>/",
    views.submission_detail,
    name="submission_detail"
),
path(
    "teacher/students/",
    views.teacher_students,
    name="teacher_students"
),

path(
    "teacher/student/<int:student_id>/",
    views.teacher_student_detail,
    name="teacher_student_detail"
),
path(
    "teacher/courses/",
    views.teacher_courses,
    name="teacher_courses"
),
path(
    "teacher/course/add/",
    views.teacher_add_course,
    name="teacher_add_course"
),

path(
    "teacher/course/<int:course_id>/edit/",
    views.teacher_edit_course,
    name="teacher_edit_course"
),

path(
    "teacher/course/<int:course_id>/delete/",
    views.teacher_delete_course,
    name="teacher_delete_course"
),
path(
    "teacher/course/<int:course_id>/manage/",
    views.teacher_course_manage,
    name="teacher_course_manage"
),
path(
    "teacher/course/<int:course_id>/lecture/add/",
    views.teacher_add_lecture,
    name="teacher_add_lecture"
),

path(
    "teacher/lecture/<int:lecture_id>/edit/",
    views.teacher_edit_lecture,
    name="teacher_edit_lecture"
),

path(
    "teacher/lecture/<int:lecture_id>/delete/",
    views.teacher_delete_lecture,
    name="teacher_delete_lecture"
),
path(
    "teacher/course/<int:course_id>/assignment/add/",
    views.teacher_add_assignment,
    name="teacher_add_assignment"
),
path(
    "teacher/assignment/<int:assignment_id>/edit/",
    views.teacher_edit_assignment,
    name="teacher_edit_assignment"
),

path(
    "teacher/assignment/<int:assignment_id>/delete/",
    views.teacher_delete_assignment,
    name="teacher_delete_assignment"
),
]