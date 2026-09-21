from django.contrib import admin

from .models import StudentProfile, Course


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