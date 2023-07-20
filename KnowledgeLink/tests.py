from django.test import TestCase

from .models import *
# Create your tests here.

class TutorModelTests(TestCase):
    def setUp(self):
        Tutor.objects.create(username = "tutor_1", user_email= "tutor_1@email.com", bio = "I am tutor_1", sunday_availability = 0)
        Tutor.objects.create(username = "tutor_2", user_email= "tutor_2@email.com", bio = "I am tutor_2", sunday_availability = 0) 

    def test_get_Sunday_Available_Time(self):
        tutor_1 = Tutor.objects.get(username = "tutor_1")
        tutor_2 = Tutor.objects.get(username = "tutor_2")
        tutor_2.sunday_availability = 0                                 #0 = empty set
        self.assertEqual(tutor_2.get_available_times(), tutor_2.get_available_times())
        tutor_2_available = tutor_2.get_available_times()
        self.assertEqual(tutor_2_available["Sunday"], [])

    def test_get_Monday_Available_Time(self):
        tutor_1 = Tutor.objects.get(username = "tutor_1")
        tutor_2 = Tutor.objects.get(username = "tutor_2")
        tutor_2.monday_availability = 1                                 #1 = 0 hour. 
        self.assertEqual(tutor_2.get_available_times(), tutor_2.get_available_times())
        tutor_2_available = tutor_2.get_available_times()
        self.assertEqual(tutor_2_available["Monday"], [datetime.time(0,0)])

    def test_get_Tuesday_Available_Time(self):
        tutor_1 = Tutor.objects.get(username = "tutor_1")
        tutor_2 = Tutor.objects.get(username = "tutor_2")
        tutor_2.tuesday_availability = 2                                 #10 = 30 min, not 0 hour. 
        self.assertEqual(tutor_2.get_available_times(), tutor_2.get_available_times())
        tutor_2_available = tutor_2.get_available_times()
        self.assertEqual(tutor_2_available["Tuesday"], [datetime.time(0,30)])

    def test_get_Wednesday_Available_Time(self):
        tutor_1 = Tutor.objects.get(username = "tutor_1")
        tutor_2 = Tutor.objects.get(username = "tutor_2")
        tutor_2.wednesday_availability = 3                                 #11 = 30 min, 0 hour. 
        self.assertEqual(tutor_2.get_available_times(), tutor_2.get_available_times())
        tutor_2_available = tutor_2.get_available_times()
        self.assertEqual(tutor_2_available["Wednesday"], [datetime.time(0,0),datetime.time(0,30)])

    def test_get_Thursday_Available_Time(self):
        tutor_1 = Tutor.objects.get(username = "tutor_1")
        tutor_2 = Tutor.objects.get(username = "tutor_2")
        tutor_2.thursday_availability = 4                                 #100 = 1 hour, not 30 min, not 0 hour. 
        self.assertEqual(tutor_2.get_available_times(), tutor_2.get_available_times())
        tutor_2_available = tutor_2.get_available_times()
        self.assertEqual(tutor_2_available["Thursday"], [datetime.time(1,0)])

    def test_get_Friday_Available_Time(self):
        tutor_1 = Tutor.objects.get(username = "tutor_1")
        tutor_2 = Tutor.objects.get(username = "tutor_2")
        tutor_2.friday_availability = 5                                 #101 = 1 hour, not 30 min, 0 hour. 
        self.assertEqual(tutor_2.get_available_times(), tutor_2.get_available_times())
        tutor_2_available = tutor_2.get_available_times()
        self.assertEqual(tutor_2_available["Friday"], [datetime.time(0,0),datetime.time(1,0)])

    def test_get_Saturday_Available_Time(self):
        tutor_1 = Tutor.objects.get(username = "tutor_1")
        tutor_2 = Tutor.objects.get(username = "tutor_2")
        tutor_2.saturday_availability = 6                                 #110 = 1 hour, 30 min, not 0 hour. 
        self.assertEqual(tutor_2.get_available_times(), tutor_2.get_available_times())
        tutor_2_available = tutor_2.get_available_times()
        self.assertEqual(tutor_2_available["Saturday"], [datetime.time(0,30),datetime.time(1,0)])


    def test_Add_Available_Time(self):
        tutor_1 = Tutor.objects.get(username = "tutor_1")
        tutor_1.add_available_time(0,datetime.time(0,0)) #add time to sunday
        tutor_1_available = tutor_1.get_available_times()
        self.assertEqual(tutor_1_available["Sunday"], [datetime.time(0,0)])

        tutor_1.add_available_time(1,datetime.time(0,30)) #add time to monday
        tutor_1_available = tutor_1.get_available_times()
        self.assertEqual(tutor_1_available["Monday"], [datetime.time(0,30)])

        tutor_1.add_available_time(2,datetime.time(0,0)) #add times to tuesday
        tutor_1.add_available_time(2,datetime.time(0,30))
        tutor_1_available = tutor_1.get_available_times()
        self.assertEqual(tutor_1_available["Tuesday"], [datetime.time(0,0),datetime.time(0,30)])


        tutor_1.add_available_time(3,datetime.time(1,0)) #add time to wednesday
        tutor_1_available = tutor_1.get_available_times()
        self.assertEqual(tutor_1_available["Wednesday"], [datetime.time(1,0)])

        tutor_1.add_available_time(4,datetime.time(1,0)) #add time to thursday
        tutor_1.add_available_time(4,datetime.time(0,0))
        tutor_1_available = tutor_1.get_available_times()
        self.assertEqual(tutor_1_available["Thursday"], [datetime.time(0,0),datetime.time(1,0)])

        tutor_1.add_available_time(5,datetime.time(0,30)) #add time to friday
        tutor_1.add_available_time(5,datetime.time(1,0)) #add time to friday
        tutor_1_available = tutor_1.get_available_times()
        self.assertEqual(tutor_1_available["Friday"], [datetime.time(0,30),datetime.time(1,0)])

        tutor_1.add_available_time(6,datetime.time(0,0)) #add time to saturday
        tutor_1.add_available_time(6,datetime.time(0,30))
        tutor_1.add_available_time(6,datetime.time(1,0))
        tutor_1_available = tutor_1.get_available_times()
        self.assertEqual(tutor_1_available["Saturday"], [datetime.time(0,0),datetime.time(0,30),datetime.time(1,0)])




    def test_get_tutor_courses(self):
        tutor_1 = Tutor.objects.get(username = "tutor_1")
        course = Course(course_mnemonic="CS", course_number="2100", course_name="Data Structures and Algorithms 1")
        course.save()
        tutor_1.courses.add(course)
        self.assertEqual(course, tutor_1.courses.get(pk=1))