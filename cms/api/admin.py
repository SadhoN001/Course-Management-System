from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Course, Lesson, Enrollment, LessonProgress

class UserAdmin(BaseUserAdmin):
    # যা fields দেখাবে admin এ
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'bio', 'avatar')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2','bio', 'avatar'),
        }),
    )

    list_display = ('id', 'username', 'email', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('id',)

admin.site.register(User, UserAdmin)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'instructor', 'created_at', 'updated_at', 'lesson_count', 'enrollment_count')
    list_filter = ('instructor', 'created_at')
    search_fields = ('title', 'description', 'instructor__username')
    ordering = ('-created_at',)
    readonly_fields = ('lesson_count', 'enrollment_count')  # calculated properties

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'order', 'duration')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    ordering = ('course', 'order')
    
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'course', 'enrolled_at')
    list_filter = ('course', 'enrolled_at')
    search_fields = ('student__username', 'course__title')
    ordering = ('-enrolled_at',)
    
@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'lesson', 'completed', 'completed_at')
    list_filter = ('completed',)
    search_fields = ('student__username', 'lesson__title')
    ordering = ('lesson',)