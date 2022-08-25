from django.db import models
from django.contrib.auth.models import User

# Create your models here.

cat=(('Option1','Option1'),('Option2','Option2'),('Option3','Option3'),('Option4','Option4'))


class Course(models.Model):
    course_name = models.CharField(max_length=50)
    course_title = models.CharField(max_length=50)
    course_desc = models.CharField(max_length=200)

    def __str__(self):
        return self.course_name

class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    question = models.CharField(max_length=600)
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    answer = models.CharField(max_length=200, choices=cat)

    def __str__(self):
        return self.course.course_name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/student', blank=True, null=True)

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"
    @property
    def get_instance(self):
        return self
    def __str__(self) -> str:
        return self.user.first_name

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Course, on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.student.matric_no



    