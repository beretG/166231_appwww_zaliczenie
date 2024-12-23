# courses/admin.py
from django.contrib import admin
from .models import Language, Level, Course, Teacher, Student, Enrollment, Lesson, Attendance

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'language', 'level', 'start_date', 'end_date', 'price', 'is_active')
    list_filter = ('language', 'level', 'is_active')
    search_fields = ('name',)
    date_hierarchy = 'start_date'

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'phone')
    filter_horizontal = ('languages',)
    search_fields = ('user__first_name', 'user__last_name', 'phone')

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Name'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'phone', 'date_of_birth')
    search_fields = ('user__first_name', 'user__last_name', 'phone')

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Name'

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('get_student', 'get_course', 'get_date', 'get_paid_status')
    list_filter = ('is_paid',)
    search_fields = ('student__user__first_name', 'student__user__last_name', 'course__name')

    def get_student(self, obj):
        return obj.student
    get_student.short_description = 'Student'

    def get_course(self, obj):
        return obj.course
    get_course.short_description = 'Course'

    def get_date(self, obj):
        return obj.enrollment_date
    get_date.short_description = 'Date'

    def get_paid_status(self, obj):
        return obj.is_paid
    get_paid_status.short_description = 'Paid'
    
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('course', 'teacher', 'date', 'topic')
    list_filter = ('course', 'teacher')
    search_fields = ('topic',)
    date_hierarchy = 'date'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'student', 'is_present')
    list_filter = ('is_present',)