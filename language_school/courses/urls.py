from django.urls import path
from . import views

app_name = 'courses'

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
]