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
]