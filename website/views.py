from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.shortcuts import render
from decimal import Decimal, InvalidOperation
from django.utils.text import slugify
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import (
    StudentProfile,
    Course,
    Lecture,
    Assignment,
    AssignmentSubmission,
)

from .models import (
    StudentProfile,
    Course,
    Lecture,
    Assignment,
    AssignmentSubmission
)


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
def lecture_detail(request, course_slug, lecture_id):

    course = Course.objects.get(
        slug=course_slug,
        is_active=True
    )

    lecture = Lecture.objects.get(
        id=lecture_id,
        course=course,
        is_published=True
    )

    return render(
        request,
        "website/lecture_detail.html",
        {
            "course": course,
            "lecture": lecture,
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

        if request.user.is_staff:
            return redirect("teacher_dashboard")

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

            # Admin / Teacher → Teacher Dashboard
            if user.is_staff:
                return redirect("teacher_dashboard")

            # Student → Student Dashboard
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

    submissions = AssignmentSubmission.objects.filter(
        student=request.user
    ).select_related(
        "assignment",
        "assignment__course",
        "assignment__lecture"
    ).order_by("-submitted_at")

    return render(
        request,
        "website/dashboard.html",
        {
            "submissions": submissions,
        }
    )
@login_required(login_url="student_login")
def teacher_dashboard(request):

    # Only staff/teacher can access
    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access the teacher dashboard."
        )
        return redirect("student_dashboard")

    # -----------------------------
    # Dashboard Statistics
    # -----------------------------

    total_students = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).count()

    total_courses = Course.objects.count()

    total_lectures = Lecture.objects.count()

    total_assignments = Assignment.objects.count()

    total_submissions = AssignmentSubmission.objects.count()

    pending_submissions = AssignmentSubmission.objects.filter(
        status="submitted"
    ).count()

    reviewed_submissions = AssignmentSubmission.objects.filter(
        status="reviewed"
    ).count()

    # -----------------------------
    # Recent Submissions
    # -----------------------------

    recent_submissions = AssignmentSubmission.objects.select_related(
        "student",
        "assignment",
        "assignment__course",
        "assignment__lecture"
    ).order_by("-submitted_at")[:10]

    # -----------------------------
    # Dashboard Context
    # -----------------------------

    context = {
        "total_students": total_students,
        "total_courses": total_courses,
        "total_lectures": total_lectures,
        "total_assignments": total_assignments,
        "total_submissions": total_submissions,
        "pending_submissions": pending_submissions,
        "reviewed_submissions": reviewed_submissions,
        "recent_submissions": recent_submissions,
    }

    return render(
        request,
        "website/teacher_dashboard.html",
        context
    )
@login_required(login_url="student_login")
def teacher_students(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access the teacher dashboard."
        )
        return redirect("student_dashboard")

    students = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).select_related(
        "student_profile"
    ).order_by("-date_joined")

    return render(
        request,
        "website/teacher_students.html",
        {
            "students": students,
        }
    )


@login_required(login_url="student_login")
def teacher_student_detail(request, student_id):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access the teacher dashboard."
        )
        return redirect("student_dashboard")

    student = get_object_or_404(
        User.objects.select_related("student_profile"),
        id=student_id,
        is_staff=False,
        is_superuser=False
    )

    submissions = AssignmentSubmission.objects.filter(
        student=student
    ).select_related(
        "assignment",
        "assignment__course",
        "assignment__lecture"
    ).order_by("-submitted_at")

    total_submissions = submissions.count()

    reviewed_submissions = submissions.filter(
        status="reviewed"
    ).count()

    pending_submissions = submissions.filter(
        status="submitted"
    ).count()

    return render(
        request,
        "website/teacher_student_detail.html",
        {
            "student": student,
            "submissions": submissions,
            "total_submissions": total_submissions,
            "reviewed_submissions": reviewed_submissions,
            "pending_submissions": pending_submissions,
        }
    )
@login_required(login_url="student_login")
def teacher_add_course(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access the teacher dashboard."
        )
        return redirect("student_dashboard")

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        slug = request.POST.get("slug", "").strip()
        short_description = request.POST.get(
            "short_description", ""
        ).strip()
        description = request.POST.get(
            "description", ""
        ).strip()
        duration = request.POST.get(
            "duration", ""
        ).strip()
        level = request.POST.get(
            "level", "Beginner"
        ).strip()
        price_text = request.POST.get(
            "price", "0"
        ).strip()
        image = request.FILES.get("image")

        is_active = request.POST.get("is_active") == "on"

        # Required field validation

        if not title:
            messages.error(
                request,
                "Course title is required."
            )

            return render(
                request,
                "website/teacher_course_form.html",
                {
                    "course": None,
                    "form_title": "Add New Course",
                }
            )

        # Automatically create slug if empty

        if not slug:
            slug = slugify(title)

        # Check duplicate slug

        if Course.objects.filter(slug=slug).exists():

            messages.error(
                request,
                "A course with this slug already exists."
            )

            return render(
                request,
                "website/teacher_course_form.html",
                {
                    "course": None,
                    "form_title": "Add New Course",
                }
            )

        # Price validation

        try:
            price = Decimal(price_text or "0")
        except (InvalidOperation, ValueError):

            messages.error(
                request,
                "Please enter a valid course price."
            )

            return render(
                request,
                "website/teacher_course_form.html",
                {
                    "course": None,
                    "form_title": "Add New Course",
                }
            )

        # Create course

        Course.objects.create(
            title=title,
            slug=slug,
            short_description=short_description,
            description=description,
            duration=duration,
            level=level,
            price=price,
            image=image,
            is_active=is_active,
        )

        messages.success(
            request,
            f"{title} has been added successfully."
        )

        return redirect("teacher_courses")

    return render(
        request,
        "website/teacher_course_form.html",
        {
            "course": None,
            "form_title": "Add New Course",
        }
    )


@login_required(login_url="student_login")
def teacher_edit_course(request, course_id):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access the teacher dashboard."
        )
        return redirect("student_dashboard")

    course = get_object_or_404(
        Course,
        id=course_id
    )

    if request.method == "POST":

        title = request.POST.get(
            "title", ""
        ).strip()

        slug = request.POST.get(
            "slug", ""
        ).strip()

        short_description = request.POST.get(
            "short_description", ""
        ).strip()

        description = request.POST.get(
            "description", ""
        ).strip()

        duration = request.POST.get(
            "duration", ""
        ).strip()

        level = request.POST.get(
            "level", "Beginner"
        ).strip()

        price_text = request.POST.get(
            "price", "0"
        ).strip()

        is_active = request.POST.get(
            "is_active"
        ) == "on"

        image = request.FILES.get("image")

        if not title:

            messages.error(
                request,
                "Course title is required."
            )

            return render(
                request,
                "website/teacher_course_form.html",
                {
                    "course": course,
                    "form_title": "Edit Course",
                }
            )

        if not slug:
            slug = slugify(title)

        # Check slug against other courses

        slug_exists = Course.objects.filter(
            slug=slug
        ).exclude(
            id=course.id
        ).exists()

        if slug_exists:

            messages.error(
                request,
                "Another course is already using this slug."
            )

            return render(
                request,
                "website/teacher_course_form.html",
                {
                    "course": course,
                    "form_title": "Edit Course",
                }
            )

        try:
            price = Decimal(price_text or "0")

        except (InvalidOperation, ValueError):

            messages.error(
                request,
                "Please enter a valid course price."
            )

            return render(
                request,
                "website/teacher_course_form.html",
                {
                    "course": course,
                    "form_title": "Edit Course",
                }
            )

        # Update course

        course.title = title
        course.slug = slug
        course.short_description = short_description
        course.description = description
        course.duration = duration
        course.level = level
        course.price = price
        course.is_active = is_active

        # Replace image only if new image uploaded

        if image:
            course.image = image

        course.save()

        messages.success(
            request,
            f"{course.title} has been updated successfully."
        )

        return redirect("teacher_courses")

    return render(
        request,
        "website/teacher_course_form.html",
        {
            "course": course,
            "form_title": "Edit Course",
        }
    )


@login_required(login_url="student_login")
def teacher_delete_course(request, course_id):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access the teacher dashboard."
        )
        return redirect("student_dashboard")

    course = get_object_or_404(
        Course,
        id=course_id
    )

    if request.method == "POST":

        course_title = course.title

        course.delete()

        messages.success(
            request,
            f"{course_title} has been deleted successfully."
        )

    return redirect("teacher_courses")
@login_required(login_url="student_login")
def teacher_course_manage(request, course_id):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access the teacher dashboard."
        )
        return redirect("student_dashboard")

    course = get_object_or_404(
        Course,
        id=course_id
    )

    lectures = course.lectures.all().order_by(
        "lecture_number",
        "lecture_date"
    )

    assignments = course.assignments.all().order_by(
        "-created_at"
    )

    enrolled_students = User.objects.filter(
        assignment_submissions__assignment__course=course
    ).distinct()

    return render(
        request,
        "website/teacher_course_manage.html",
        {
            "course": course,
            "lectures": lectures,
            "assignments": assignments,
            "enrolled_students": enrolled_students,
        }
    )
@login_required(login_url="student_login")
def teacher_courses(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access the teacher dashboard."
        )
        return redirect("student_dashboard")

    courses = Course.objects.all().order_by("-created_at")

    return render(
        request,
        "website/teacher_courses.html",
        {
            "courses": courses,
        }
    )
@login_required(login_url="student_login")
def submission_detail(request, submission_id):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access the teacher dashboard."
        )
        return redirect("student_dashboard")

    submission = get_object_or_404(
        AssignmentSubmission.objects.select_related(
            "student",
            "assignment",
            "assignment__course",
            "assignment__lecture"
        ),
        id=submission_id
    )

    if request.method == "POST":

        marks_text = request.POST.get(
            "marks",
            ""
        ).strip()

        teacher_feedback = request.POST.get(
            "teacher_feedback",
            ""
        ).strip()

        # Marks validation
        if marks_text:

            try:
                marks = int(marks_text)

            except ValueError:

                messages.error(
                    request,
                    "Marks must be a valid number."
                )

                return render(
                    request,
                    "website/submission_detail.html",
                    {
                        "submission": submission
                    }
                )

            if marks < 0 or marks > 100:

                messages.error(
                    request,
                    "Marks must be between 0 and 100."
                )

                return render(
                    request,
                    "website/submission_detail.html",
                    {
                        "submission": submission
                    }
                )

            submission.marks = marks

        else:
            submission.marks = None

        submission.teacher_feedback = teacher_feedback
        submission.status = "reviewed"

        from django.utils import timezone

        submission.reviewed_at = timezone.now()

        submission.save()

        messages.success(
            request,
            "Assignment has been reviewed successfully."
        )

        return redirect(
            "submission_detail",
            submission_id=submission.id
        )

    return render(
        request,
        "website/submission_detail.html",
        {
            "submission": submission
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
def assignments(request, course_slug):
    course = Course.objects.get(
        slug=course_slug,
        is_active=True
    )

    all_assignments = Assignment.objects.filter(
        course=course,
        is_published=True
    ).order_by("due_date", "-created_at")

    return render(
        request,
        "website/assignments.html",
        {
            "course": course,
            "assignments": all_assignments,
        }
    )

from django.shortcuts import get_object_or_404, redirect, render

from .models import Assignment, AssignmentSubmission


@login_required(login_url="student_login")
def submit_assignment(request, assignment_id):

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        is_published=True
    )

    if request.method == "POST":

        submission_image = request.FILES.get("submission_image")
        submission_video = request.FILES.get("submission_video")

        student_comment = request.POST.get(
            "student_comment",
            ""
        ).strip()

        # Check that at least one file is uploaded
        if not submission_image and not submission_video:

            messages.error(
                request,
                "Please upload at least one assignment picture or video."
            )

            return render(
                request,
                "website/submit_assignment.html",
                {
                    "assignment": assignment,
                }
            )

        # Create submission
        AssignmentSubmission.objects.create(
            assignment=assignment,
            student=request.user,
            submission_image=submission_image,
            submission_video=submission_video,
            student_comment=student_comment,
            status="submitted"
        )

        messages.success(
            request,
            "Your assignment has been submitted successfully."
        )

        return redirect(
            "assignments",
            course_slug=assignment.course.slug
        )

    return render(
        request,
        "website/submit_assignment.html",
        {
            "assignment": assignment,
        }
    )
@login_required(login_url="student_login")
def teacher_add_lecture(request, course_id):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access the teacher dashboard."
        )
        return redirect("student_dashboard")

    course = get_object_or_404(
        Course,
        id=course_id
    )

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        lecture_number = request.POST.get(
            "lecture_number",
            "1"
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        lecture_date = request.POST.get(
            "lecture_date",
            ""
        ).strip()

        lecture_type = request.POST.get(
            "lecture_type",
            "recorded"
        ).strip()

        video_url = request.POST.get(
            "video_url",
            ""
        ).strip()

        live_url = request.POST.get(
            "live_url",
            ""
        ).strip()

        notes = request.FILES.get("notes")

        is_published = request.POST.get(
            "is_published"
        ) == "on"


        if not title:
            messages.error(
                request,
                "Lecture title is required."
            )

            return render(
                request,
                "website/teacher_lecture_form.html",
                {
                    "course": course,
                    "lecture": None,
                    "form_title": "Add New Lecture",
                }
            )


        try:
            lecture_number = int(
                lecture_number or 1
            )
        except ValueError:

            messages.error(
                request,
                "Lecture number must be a valid number."
            )

            return render(
                request,
                "website/teacher_lecture_form.html",
                {
                    "course": course,
                    "lecture": None,
                    "form_title": "Add New Lecture",
                }
            )


        Lecture.objects.create(
            course=course,
            title=title,
            lecture_number=lecture_number,
            description=description,
            lecture_date=lecture_date,
            lecture_type=lecture_type,
            video_url=video_url,
            live_url=live_url,
            notes=notes,
            is_published=is_published,
        )


        messages.success(
            request,
            f"{title} has been added successfully."
        )

        return redirect(
            "teacher_course_manage",
            course_id=course.id
        )


    return render(
        request,
        "website/teacher_lecture_form.html",
        {
            "course": course,
            "lecture": None,
            "form_title": "Add New Lecture",
        }
    )
@login_required(login_url="student_login")
def teacher_edit_lecture(request, lecture_id):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access the teacher dashboard."
        )
        return redirect("student_dashboard")

    lecture = get_object_or_404(
        Lecture,
        id=lecture_id
    )

    course = lecture.course

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        lecture_number = request.POST.get(
            "lecture_number",
            "1"
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        lecture_date = request.POST.get(
            "lecture_date",
            ""
        ).strip()

        lecture_type = request.POST.get(
            "lecture_type",
            "recorded"
        ).strip()

        video_url = request.POST.get(
            "video_url",
            ""
        ).strip()

        live_url = request.POST.get(
            "live_url",
            ""
        ).strip()

        notes = request.FILES.get("notes")

        is_published = request.POST.get(
            "is_published"
        ) == "on"


        if not title:

            messages.error(
                request,
                "Lecture title is required."
            )

            return render(
                request,
                "website/teacher_lecture_form.html",
                {
                    "course": course,
                    "lecture": lecture,
                    "form_title": "Edit Lecture",
                }
            )


        try:

            lecture_number = int(
                lecture_number or 1
            )

        except ValueError:

            messages.error(
                request,
                "Lecture number must be a valid number."
            )

            return render(
                request,
                "website/teacher_lecture_form.html",
                {
                    "course": course,
                    "lecture": lecture,
                    "form_title": "Edit Lecture",
                }
            )


        lecture.title = title
        lecture.lecture_number = lecture_number
        lecture.description = description
        lecture.lecture_date = lecture_date
        lecture.lecture_type = lecture_type
        lecture.video_url = video_url
        lecture.live_url = live_url
        lecture.is_published = is_published

        if notes:
            lecture.notes = notes

        lecture.save()


        messages.success(
            request,
            f"{lecture.title} has been updated successfully."
        )

        return redirect(
            "teacher_course_manage",
            course_id=course.id
        )


    return render(
        request,
        "website/teacher_lecture_form.html",
        {
            "course": course,
            "lecture": lecture,
            "form_title": "Edit Lecture",
        }
    )


@login_required(login_url="student_login")
def teacher_delete_lecture(request, lecture_id):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access the teacher dashboard."
        )
        return redirect("student_dashboard")

    lecture = get_object_or_404(
        Lecture,
        id=lecture_id
    )

    course_id = lecture.course.id
    lecture_title = lecture.title

    if request.method == "POST":

        lecture.delete()

        messages.success(
            request,
            f"{lecture_title} has been deleted successfully."
        )

    return redirect(
        "teacher_course_manage",
        course_id=course_id
    )
@login_required(login_url="student_login")
def teacher_add_assignment(request, course_id):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access the teacher dashboard."
        )
        return redirect("student_dashboard")

    course = get_object_or_404(
        Course,
        id=course_id
    )

    lectures = course.lectures.all().order_by(
        "lecture_number",
        "lecture_date"
    )

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        lecture_id = request.POST.get(
            "lecture",
            ""
        ).strip()

        due_date = request.POST.get(
            "due_date",
            ""
        ).strip()

        assignment_file = request.FILES.get(
            "assignment_file"
        )

        is_published = request.POST.get(
            "is_published"
        ) == "on"

        if not title:
            messages.error(
                request,
                "Assignment title is required."
            )

            return render(
                request,
                "website/teacher_assignment_form.html",
                {
                    "course": course,
                    "lectures": lectures,
                }
            )

        if not description:
            messages.error(
                request,
                "Assignment description is required."
            )

            return render(
                request,
                "website/teacher_assignment_form.html",
                {
                    "course": course,
                    "lectures": lectures,
                }
            )

        lecture = None

        if lecture_id:
            lecture = get_object_or_404(
                Lecture,
                id=lecture_id,
                course=course
            )

        Assignment.objects.create(
            course=course,
            lecture=lecture,
            title=title,
            description=description,
            assignment_file=assignment_file,
            due_date=due_date if due_date else None,
            is_published=is_published
        )

        messages.success(
            request,
            "Assignment has been added successfully."
        )

        return redirect(
            "teacher_course_manage",
            course_id=course.id
        )

    return render(
        request,
        "website/teacher_assignment_form.html",
        {
            "course": course,
            "lectures": lectures,
        }
    )
@login_required(login_url="student_login")
def teacher_edit_assignment(request, assignment_id):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access the teacher dashboard."
        )
        return redirect("student_dashboard")

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id
    )

    course = assignment.course

    lectures = course.lectures.all().order_by(
        "lecture_number",
        "lecture_date"
    )

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        lecture_id = request.POST.get(
            "lecture",
            ""
        ).strip()

        due_date = request.POST.get(
            "due_date",
            ""
        ).strip()

        assignment_file = request.FILES.get(
            "assignment_file"
        )

        is_published = request.POST.get(
            "is_published"
        ) == "on"

        if not title:
            messages.error(
                request,
                "Assignment title is required."
            )

            return render(
                request,
                "website/teacher_assignment_form.html",
                {
                    "course": course,
                    "lectures": lectures,
                    "assignment": assignment,
                    "edit_mode": True,
                }
            )

        if not description:
            messages.error(
                request,
                "Assignment description is required."
            )

            return render(
                request,
                "website/teacher_assignment_form.html",
                {
                    "course": course,
                    "lectures": lectures,
                    "assignment": assignment,
                    "edit_mode": True,
                }
            )

        lecture = None

        if lecture_id:
            lecture = get_object_or_404(
                Lecture,
                id=lecture_id,
                course=course
            )

        assignment.title = title
        assignment.description = description
        assignment.lecture = lecture
        assignment.due_date = due_date if due_date else None
        assignment.is_published = is_published

        if assignment_file:
            assignment.assignment_file = assignment_file

        assignment.save()

        messages.success(
            request,
            "Assignment has been updated successfully."
        )

        return redirect(
            "teacher_course_manage",
            course_id=course.id
        )

    return render(
        request,
        "website/teacher_assignment_form.html",
        {
            "course": course,
            "lectures": lectures,
            "assignment": assignment,
            "edit_mode": True,
        }
    )
@login_required(login_url="student_login")
def teacher_delete_assignment(request, assignment_id):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access the teacher dashboard."
        )
        return redirect("student_dashboard")

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id
    )

    course_id = assignment.course.id

    if request.method == "POST":

        assignment.delete()

        messages.success(
            request,
            "Assignment has been deleted successfully."
        )

        return redirect(
            "teacher_course_manage",
            course_id=course_id
        )

    return render(
        request,
        "website/teacher_assignment_delete.html",
        {
            "assignment": assignment,
        }
    )