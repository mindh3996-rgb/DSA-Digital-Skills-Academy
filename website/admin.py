from django.contrib import admin

from .models import StudentProfile, Course, Lecture, Assignment


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "full_name",
        "phone",
        "city",
        "created_at",
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "level",
        "duration",
        "price",
        "is_active",
        "created_at",
    )

    list_filter = (
        "level",
        "is_active",
    )

    search_fields = (
        "title",
        "short_description",
        "description",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }
@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):

    list_display = (
        "course",
        "lecture_number",
        "title",
        "lecture_date",
        "lecture_type",
        "is_published",
    )

    list_filter = (
        "course",
        "lecture_type",
        "is_published",
    )

    search_fields = (
        "title",
        "description",
        "course__title",
    )

    ordering = (
        "course",
        "lecture_number",
    )
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "course",
        "lecture",
        "due_date",
        "is_published",
        "created_at",
    )

    list_filter = (
        "course",
        "is_published",
        "due_date",
    )

    search_fields = (
        "title",
        "description",
        "course__title",
        "lecture__title",
    )

    ordering = (
        "-created_at",
    )