from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.shortcuts import render

from .models import StudentProfile, Course


def home(request):
    return render(request, "website/home.html")
def courses(request):

    all_courses = Course.objects.filter(
        is_active=True
    ).order_by("-created_at")

    return render(
        request,
        "website/courses.html",
        {
            "courses": all_courses
        }
    )
def course_detail(request, slug):

    course = Course.objects.get(
        slug=slug,
        is_active=True
    )

    return render(
        request,
        "website/course_detail.html",
        {
            "course": course
        }
    )


def register_student(request):

    if request.user.is_authenticated:
        return redirect("student_dashboard")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not email or not password:
            messages.error(
                request,
                "Please fill in all required fields."
            )

            return render(
                request,
                "website/register.html"
            )

        if password != confirm_password:
            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "website/register.html"
            )

        if len(password) < 8:
            messages.error(
                request,
                "Password must contain at least 8 characters."
            )

            return render(
                request,
                "website/register.html"
            )

        if User.objects.filter(username=username).exists():
            messages.error(
                request,
                "This username is already registered."
            )

            return render(
                request,
                "website/register.html"
            )

        if User.objects.filter(email=email).exists():
            messages.error(
                request,
                "An account with this email already exists."
            )

            return render(
                request,
                "website/register.html"
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        StudentProfile.objects.create(
            user=user
        )

        login(request, user)

        messages.success(
            request,
            "Your DSA student account has been created successfully!"
        )

        return redirect("student_dashboard")

    return render(
        request,
        "website/register.html"
    )


def student_login(request):

    if request.user.is_authenticated:
        return redirect("student_dashboard")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            messages.success(
                request,
                f"Welcome back, {user.username}!"
            )

            return redirect("student_dashboard")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "website/login.html"
    )


@login_required(login_url="student_login")
def student_dashboard(request):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        "website/dashboard.html",
        {
            "profile": profile
        }
    )


@login_required(login_url="student_login")
def edit_profile(request):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        full_name = request.POST.get(
            "full_name",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        city = request.POST.get(
            "city",
            ""
        ).strip()

        bio = request.POST.get(
            "bio",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        profile.full_name = full_name
        profile.phone = phone
        profile.city = city
        profile.bio = bio

        request.user.email = email
        request.user.save()

        if request.FILES.get("profile_picture"):
            profile.profile_picture = request.FILES[
                "profile_picture"
            ]

        profile.save()

        messages.success(
            request,
            "Your profile has been updated successfully."
        )

        return redirect("student_dashboard")

    return render(
        request,
        "website/edit_profile.html",
        {
            "profile": profile
        }
    )


@login_required(login_url="student_login")
def student_logout(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("home")
def about(request):
    return render(request, "website/about.html")
def contact(request):
    return render(request, "website/contact.html")