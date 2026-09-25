from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    full_name = models.CharField(
        max_length=150,
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    bio = models.TextField(
        blank=True
    )

    profile_picture = models.ImageField(
        upload_to="student_profiles/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.user.username
class Course(models.Model):

    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        unique=True
    )

    short_description = models.CharField(
        max_length=300
    )

    description = models.TextField()

    duration = models.CharField(
        max_length=100
    )

    level = models.CharField(
        max_length=50,
        choices=[
            ("Beginner", "Beginner"),
            ("Intermediate", "Intermediate"),
            ("Advanced", "Advanced"),
        ],
        default="Beginner"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    image = models.ImageField(
        upload_to="courses/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title
class Lecture(models.Model):

    LECTURE_TYPE_CHOICES = [
        ("recorded", "Recorded Lecture"),
        ("live", "Live Lecture"),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lectures"
    )

    title = models.CharField(max_length=200)

    lecture_number = models.PositiveIntegerField(default=1)

    description = models.TextField(blank=True)

    lecture_date = models.DateField()

    lecture_type = models.CharField(
        max_length=20,
        choices=LECTURE_TYPE_CHOICES,
        default="recorded"
    )

    video_url = models.URLField(
        blank=True,
        null=True
    )

    live_url = models.URLField(
        blank=True,
        null=True
    )

    notes = models.FileField(
        upload_to="lecture_notes/",
        blank=True,
        null=True
    )

    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["lecture_number", "lecture_date"]

    def __str__(self):
        return f"{self.course.title} - Lecture {self.lecture_number}: {self.title}"
class Assignment(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.CASCADE,
        related_name="assignments",
        blank=True,
        null=True
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    assignment_file = models.FileField(
        upload_to="assignments/",
        blank=True,
        null=True
    )

    due_date = models.DateField(
        blank=True,
        null=True
    )

    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
class AssignmentSubmission(models.Model):

    STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("reviewed", "Reviewed"),
    ]

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions"
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assignment_submissions"
    )

    # Student Assignment Picture
    submission_image = models.ImageField(
        upload_to="assignment_submissions/images/",
        blank=True,
        null=True
    )

    # Student Assignment Video
    submission_video = models.FileField(
        upload_to="assignment_submissions/videos/",
        blank=True,
        null=True
    )

    student_comment = models.TextField(
        blank=True
    )

    teacher_feedback = models.TextField(
        blank=True
    )
    marks = models.PositiveIntegerField(
    blank=True,
    null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="submitted"
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    reviewed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"