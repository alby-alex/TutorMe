from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
import datetime


class Student(models.Model):
    username = models.CharField(max_length=200)
    user_email = models.CharField(max_length=200)

class Course(models.Model):
    course_mnemonic = models.CharField(max_length=200)
    course_number = models.CharField(max_length=200)
    course_name = models.CharField(max_length=200)

class Tutor(models.Model):
    username = models.CharField(max_length=200)
    user_email = models.CharField(max_length=200)
    bio = models.CharField(max_length=200)
    courses = models.ManyToManyField(Course, blank=True)
    hourly_rate = models.DecimalField(editable=True, default=0, max_digits=5, decimal_places=2)
    sunday_availability = models.BigIntegerField(editable=True, default=0)
    monday_availability = models.BigIntegerField(editable=True, default=0)
    tuesday_availability = models.BigIntegerField(editable=True, default=0)
    wednesday_availability = models.BigIntegerField(editable=True, default=0)
    thursday_availability = models.BigIntegerField(editable=True, default=0)
    friday_availability = models.BigIntegerField(editable=True, default=0)
    saturday_availability = models.BigIntegerField(editable=True, default=0)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    students_rated = models.ManyToManyField(Student, blank=True)

    def get_available_times(self):
        day_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        available_times = {x:[] for x in day_of_week}
        temp = self.sunday_availability
        if temp!=0:
            day = day_of_week[0]
            for i in range(48):
                val = temp & 1
                if val:
                    time = (datetime.datetime(year=2001, month=1, day=3) + datetime.timedelta(hours=(i / 2))).time()
                    available_times[day].append(time)
                temp >>= 1
        temp = self.monday_availability
        if temp!=0:
            day = day_of_week[1]
            for i in range(48):
                val = temp & 1
                if val:
                    time = (datetime.datetime(year=2001, month=1, day=3) + datetime.timedelta(hours=(i / 2))).time()
                    available_times[day].append(time)
                temp >>= 1
        temp = self.tuesday_availability
        if temp != 0:
            day = day_of_week[2]
            for i in range(48):
                val = temp & 1
                if val:
                    time = (datetime.datetime(year=2001, month=1, day=3) + datetime.timedelta(hours=(i / 2))).time()
                    available_times[day].append(time)
                temp >>= 1
        temp = self.wednesday_availability
        if temp != 0:
            day = day_of_week[3]
            for i in range(48):
                val = temp & 1
                if val:
                    time = (datetime.datetime(year=2001, month=1, day=3) + datetime.timedelta(hours=(i / 2))).time()
                    available_times[day].append(time)
                temp >>= 1
        temp = self.thursday_availability
        if temp != 0:
            day = day_of_week[4]
            for i in range(48):
                val = temp & 1
                if val:
                    time = (datetime.datetime(year=2001, month=1, day=3) + datetime.timedelta(hours=(i / 2))).time()
                    available_times[day].append(time)
                temp >>= 1
        temp = self.friday_availability
        if temp != 0:
            day = day_of_week[5]
            for i in range(48):
                val = temp & 1
                if val:
                    time = (datetime.datetime(year=2001, month=1, day=3) + datetime.timedelta(hours=(i / 2))).time()
                    available_times[day].append(time)
                temp >>= 1
        temp = self.saturday_availability
        if temp != 0:
            day = day_of_week[6]
            for i in range(48):
                val = temp & 1
                if val:
                    time = (datetime.datetime(year=2001, month=1, day=3) + datetime.timedelta(hours=(i / 2))).time()
                    available_times[day].append(time)
                temp >>= 1
        return available_times

    def add_available_time(self, day_of_week, time):
        if day_of_week == 0:
            bit = int(((time.hour + time.minute / 60) * 2))
            flip = 1 << bit
            self.sunday_availability |= flip
        if day_of_week == 1:
            bit = int(((time.hour + time.minute / 60) * 2))
            flip = 1 << bit
            self.monday_availability |= flip
        if day_of_week == 2:
            bit = int(((time.hour + time.minute / 60) * 2))
            flip = 1 << bit
            self.tuesday_availability |= flip
        if day_of_week == 3:
            bit = int(((time.hour + time.minute / 60) * 2))
            flip = 1 << bit
            self.wednesday_availability |= flip
        if day_of_week == 4:
            bit = int(((time.hour + time.minute / 60) * 2))
            flip = 1 << bit
            self.thursday_availability |= flip
        if day_of_week == 5:
            bit = int(((time.hour + time.minute / 60) * 2))
            flip = 1 << bit
            self.friday_availability |= flip
        if day_of_week == 6:
            bit = int(((time.hour + time.minute / 60) * 2))
            flip = 1 << bit
            self.saturday_availability |= flip
        self.save()

    def remove_available_time(self, day_of_week, time):
        if day_of_week == 0:
            bit = int(((time.hour + time.minute / 60) * 2))
            flip = 1 << bit
            self.sunday_availability -= flip
        if day_of_week == 1:
            bit = int(((time.hour + time.minute / 60) * 2))
            flip = 1 << bit
            self.monday_availability -= flip
        if day_of_week == 2:
            bit = int(((time.hour + time.minute / 60) * 2))
            flip = 1 << bit
            self.tuesday_availability -= flip
        if day_of_week == 3:
            bit = int(((time.hour + time.minute / 60) * 2))
            flip = 1 << bit
            self.wednesday_availability -= flip
        if day_of_week == 4:
            bit = int(((time.hour + time.minute / 60) * 2))
            flip = 1 << bit
            self.thursday_availability -= flip
        if day_of_week == 5:
            bit = int(((time.hour + time.minute / 60) * 2))
            flip = 1 << bit
            self.friday_availability -= flip
        if day_of_week == 6:
            bit = int(((time.hour + time.minute / 60) * 2))
            flip = 1 << bit
            self.saturday_availability -= flip
        self.save()

class Appointment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    day = models.CharField(max_length=200)
    time = models.TimeField()
    # 0: REJECTED, 1: APPROVED, 2: PENDING
    status = models.IntegerField(default=2)
    is_active = models.BooleanField(default=True)

