# courses/models.py
from django.db import models
from django.contrib.auth.models import User

class Language(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=2)  # np. 'en', 'de', 'es'
    
    def __str__(self):
        return self.name

class Level(models.Model):
    name = models.CharField(max_length=20)  # np. A1, A2, B1, B2, C1, C2
    description = models.TextField()
    
    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=200)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    max_students = models.IntegerField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.language} - {self.level} - {self.name}"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    languages = models.ManyToManyField(Language)
    phone = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='teachers/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['student', 'course']
        db_table = 'courses_enrollment'

    def __str__(self):
        return f"{self.student} - {self.course}"

    def get_attendance_rate(self):
        attended = self.student.attendance_set.filter(
            lesson__course=self.course,
            is_present=True
        ).count()
        total = self.student.attendance_set.filter(
            lesson__course=self.course
        ).count()
        return round(attended / total * 100) if total > 0 else 0

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    date = models.DateTimeField()
    duration = models.IntegerField(help_text="Czas trwania w minutach")
    topic = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.course} - {self.date}"

class Attendance(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    is_present = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['lesson', 'student']