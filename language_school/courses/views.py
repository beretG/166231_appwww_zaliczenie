from datetime import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Attendance, Course, Enrollment, Language, Lesson, Student, Teacher
from django.utils import timezone

# Widok strony głównej
def home(request):
    return render(request, 'courses/home.html', {
        'courses_count': Course.objects.count(),
        'languages_count': Language.objects.count(),
        'teachers_count': Teacher.objects.count(),
        'students_count': Student.objects.count(),
    })

# Widoki dla kursów
class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    ordering = ['-start_date']

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'

class CourseCreateView(CreateView):
    model = Course
    template_name = 'courses/course_form.html'
    fields = ['name', 'language', 'level', 'start_date', 'end_date', 
              'price', 'max_students', 'description', 'is_active']
    success_url = reverse_lazy('courses:course-list')

class CourseUpdateView(UpdateView):
    model = Course
    template_name = 'courses/course_form.html'
    fields = ['name', 'language', 'level', 'start_date', 'end_date', 
              'price', 'max_students', 'description', 'is_active']
    success_url = reverse_lazy('courses:course-list')

class CourseDeleteView(DeleteView):
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('courses:course-list')

# Widoki dla nauczycieli
class TeacherListView(ListView):
    model = Teacher
    template_name = 'courses/teacher_list.html'
    context_object_name = 'teachers'

class TeacherDetailView(DetailView):
    model = Teacher
    template_name = 'courses/teacher_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_lessons'] = Lesson.objects.filter(
            teacher=self.object,
            date__gte=timezone.now()
        ).order_by('date')
        return context

# Widoki dla studentów
class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'courses/student_list.html'
    context_object_name = 'students'

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'courses/student_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enrollments'] = self.object.enrollment_set.all()
        return context

# Widoki dla lekcji
class LanguageListView(ListView):
    model = Language
    template_name = 'courses/language_list.html'
    context_object_name = 'languages'

class LanguageDetailView(DetailView):
    model = Language
    template_name = 'courses/language_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = self.object.course_set.all()
        context['teachers'] = self.object.teacher_set.all()
        return context
    
# Widok dla lekcji
@login_required
def lesson_list(request):
    if hasattr(request.user, 'teacher'):
        lessons = Lesson.objects.filter(teacher=request.user.teacher)
    elif hasattr(request.user, 'student'):
        enrolled_courses = request.user.student.courses.all()
        lessons = Lesson.objects.filter(course__in=enrolled_courses)
    else:
        lessons = []
    
    return render(request, 'courses/lesson_list.html', {'lessons': lessons})

@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    attendances = Attendance.objects.filter(lesson=lesson)
    
    if request.method == 'POST' and hasattr(request.user, 'teacher'):
        # Obsługa zapisywania obecności
        for student_id, is_present in request.POST.items():
            if student_id.startswith('student_'):
                student_id = student_id.replace('student_', '')
                student = get_object_or_404(Student, id=student_id)
                attendance, created = Attendance.objects.get_or_create(
                    lesson=lesson,
                    student=student,
                    defaults={'is_present': is_present == 'true'}
                )
                if not created:
                    attendance.is_present = is_present == 'true'
                    attendance.save()
        
        messages.success(request, 'Obecność została zapisana.')
        return redirect('courses:lesson-detail', pk=pk)
    
    return render(request, 'courses/lesson_detail.html', {
        'lesson': lesson,
        'attendances': attendances
    })

class RegisterView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'courses/register.html'

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    if request.method == 'POST':
        try:
            data = request.data
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            token = Token.objects.create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
def teacher_schedule_view(request):
    today = timezone.now()
    week_later = today + timezone.timedelta(days=7)
    lessons = Lesson.objects.filter(
        teacher=request.user.teacher,
        date__range=[today, week_later]
    ).order_by('date')
    return render(request, 'courses/teacher_schedule.html', {'lessons': lessons})        

def student_course_history_view(request):
   enrollments = Enrollment.objects.filter(student=request.user.student)
   return render(request, 'courses/student_course_history.html', {'enrollments': enrollments})