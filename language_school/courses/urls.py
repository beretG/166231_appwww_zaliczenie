from django.db import router
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import RegisterView
from . import views
from . import api_views 

app_name = 'courses'

router = DefaultRouter()
router.register(r'courses', api_views.CourseViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    
    # URLs dla kursów
    path('courses/', views.CourseListView.as_view(), name='course-list'),
    path('course/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('course/new/', views.CourseCreateView.as_view(), name='course-create'),
    path('course/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course-update'),
    path('course/<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course-delete'),

     # URLs dla nauczycieli
    path('teachers/', views.TeacherListView.as_view(), name='teacher-list'),
    path('teacher/<int:pk>/', views.TeacherDetailView.as_view(), name='teacher-detail'),
    
    # URLs dla studentów
    path('students/', views.StudentListView.as_view(), name='student-list'),
    path('student/<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    
    # URLs dla lekcji
    path('lessons/', views.lesson_list, name='lesson-list'),
    path('lesson/<int:pk>/', views.lesson_detail, name='lesson-detail'),

    # Urls dla jezykow
    path('languages/', views.LanguageListView.as_view(), name='language-list'),
    path('language/<int:pk>/', views.LanguageDetailView.as_view(), name='language-detail'),

    # URLs dla rejestracji
    path('register/', RegisterView.as_view(), name='register'),

    # URLs dla API 
    path('api/', include(router.urls)),
    path('api/register/', views.register_user, name='register-api'),
    path('api/student/history/', api_views.student_course_history, name='api-student-history'),
    path('api/teacher/schedule/', api_views.teacher_schedule, name='api-teacher-schedule'),
    path('api/lesson/<int:lesson_id>/attendance/', api_views.lesson_attendance, name='lesson-attendance'),
    path('api/student/<int:student_id>/attendance/', api_views.student_attendance, name='student-attendance'),

    path('teacher/schedule/', views.teacher_schedule_view, name='teacher-schedule-view'),
    path('student/history/', views.student_course_history_view, name='student-history'),
]