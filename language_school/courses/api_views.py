from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from .models import Attendance, Course, Language, Teacher, Student, Lesson, Enrollment
from .serializers import CourseSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_course_history(request):
    student = request.user.student
    enrollments = Enrollment.objects.filter(student=student)
    data = [{
        'course': enrollment.course.name,
        'start_date': enrollment.course.start_date,
        'end_date': enrollment.course.end_date,
        'attendance_rate': enrollment.get_attendance_rate(),
        'is_paid': enrollment.is_paid
    } for enrollment in enrollments]
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_schedule(request):
    if not hasattr(request.user, 'teacher'):
        return Response({'error': 'User is not a teacher'}, status=403)
    
    today = timezone.now()
    week_later = today + timezone.timedelta(days=7)
    lessons = Lesson.objects.filter(
        teacher=request.user.teacher,
        date__range=[today, week_later]
    ).values('date', 'course__name', 'topic')
    return Response(lessons)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def lesson_attendance(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    if request.method == 'GET':
        # Pobierz studentów zapisanych na kurs
        enrolled_students = Student.objects.filter(
            enrollment__course=lesson.course
        ).distinct()
        
        # Pobierz obecności dla tej lekcji
        attendances = Attendance.objects.filter(lesson=lesson)
        
        data = []
        for student in enrolled_students:
            attendance = attendances.filter(student=student).first()
            data.append({
                'student_id': student.id,
                'student_name': f"{student.user.first_name} {student.user.last_name}",
                'is_present': attendance.is_present if attendance else False
            })
        return Response(data)

    elif request.method == 'POST':
        if not hasattr(request.user, 'teacher') or request.user.teacher != lesson.teacher:
            return Response({'error': 'Only the lesson teacher can mark attendance'}, status=403)
        
        student_id = request.data.get('student_id')
        is_present = request.data.get('is_present', False)
        
        if not student_id:
            return Response({'error': 'Student ID is required'}, status=400)
            
        student = get_object_or_404(Student, id=student_id)
        
        # Sprawdź czy student jest zapisany na kurs
        if not Enrollment.objects.filter(student=student, course=lesson.course).exists():
            return Response({'error': 'Student is not enrolled in this course'}, status=400)
        
        attendance, created = Attendance.objects.update_or_create(
            lesson=lesson,
            student=student,
            defaults={'is_present': is_present}
        )
        
        return Response({
            'student_id': student.id,
            'student_name': f"{student.user.first_name} {student.user.last_name}",
            'is_present': attendance.is_present
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_attendance(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    # Sprawdź uprawnienia
    if not (request.user.is_staff or 
            (hasattr(request.user, 'student') and request.user.student == student) or
            (hasattr(request.user, 'teacher') and 
             Lesson.objects.filter(teacher=request.user.teacher, course__enrollment__student=student).exists())):
        return Response({'error': 'Permission denied'}, status=403)
    
    attendances = Attendance.objects.filter(student=student)
    data = [{
        'lesson_date': attendance.lesson.date,
        'course': attendance.lesson.course.name,
        'teacher': f"{attendance.lesson.teacher.user.first_name} {attendance.lesson.teacher.user.last_name}",
        'is_present': attendance.is_present
    } for attendance in attendances]
    
    return Response(data)