from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404, HttpResponseForbidden
from .models import *
from django import forms
from .forms import SignUpForm, HourlyRateForm, TutorBioForm
from django.urls import reverse
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import *
from allauth.socialaccount import *
import time
import requests
from icalendar import Calendar, Event, vCalAddress, vText, vRecur, vDatetime
from pathlib import Path
from dateutil import relativedelta
from dateutil.relativedelta import *
import datetime
import pytz

day_index = {"Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6}

# **************************************************************************************
# *  REFERENCES
# *  Title: django-allauth set username the same as email
# *  Author: ferrangb
# *  Date: December 13, 2014
# *  URL: https://stackoverflow.com/questions/27348705/django-allauth-set-username-the-same-as-email
# *
# ********************************************************************
@receiver(pre_save, sender=User)
def update_username(sender, instance, **kwargs):
    user_email = instance.email
    location_a = instance.email.index("@")
    instance.username = user_email[:location_a]


def student(request):
    if is_Tutor(request.user):
        return HttpResponseRedirect("/KL/tutor")
    else:
        current_student = Student.objects.filter(username=request.user.username)[0]
        student_name = request.user.first_name
        active_appointments = Appointment.objects.filter(student=current_student, status = 1, is_active = True)
        pending_appointments = Appointment.objects.filter(student=current_student, status = 2)
        return render(request, 'KnowledgeLink/student/student_home_page.html', {'student_name': student_name, 'active_appointments': active_appointments, 'pending_appointments':pending_appointments})


def student_edit_profile(request):
    return render(request, 'KnowledgeLink/student/edit_account_form.html')


def tutor(request):
    if is_Student(request.user):
        return HttpResponseRedirect("/KL/student")
    else:
        current_tutor = Tutor.objects.filter(username=request.user.username)[0]
        tutor_classes = current_tutor.courses.all()
        tutor_name = request.user.first_name
        tutor_availability = current_tutor.get_available_times()
        active_appointments = Appointment.objects.filter(tutor=current_tutor, status = 1, is_active = True)
        pending_appointments = Appointment.objects.filter(tutor=current_tutor, status = 2)
        active_length = len(active_appointments)
        pending_length = len(pending_appointments)
        tutor_upvotes = current_tutor.upvotes
        tutor_downvotes = current_tutor.downvotes
        return render(request, 'KnowledgeLink/tutor/tutor_home_page.html', {'tutor_classes': tutor_classes,
                                                                        'tutor_name': tutor_name,
                                                                        "tutor_availability": tutor_availability,
                                                                        'active_appointments': active_appointments,
                                                                        'pending_appointments':pending_appointments,
                                                                        'active_length': active_length,
                                                                        'pending_length':pending_length,
                                                                        'tutor_upvotes': tutor_upvotes,
                                                                        'tutor_downvotes': tutor_downvotes})



def tutor_profile(request):
    if is_Student(request.user):
        return HttpResponseRedirect("/KL/student")
    current_tutor = Tutor.objects.filter(username=request.user.username)[0]
    tutor_classes = current_tutor.courses.all()
    courses_length = len(tutor_classes)
    tutor_name = request.user.first_name
    tutor_availability = current_tutor.get_available_times()
    tutor_hourly_rate = current_tutor.hourly_rate
    tutor_bio = current_tutor.bio
    bio_length = len(tutor_bio)
    return render(request, 'KnowledgeLink/tutor/tutor_profile_page.html', {'tutor_classes': tutor_classes,
                                                                           'tutor_name': tutor_name,
                                                                           "tutor_availability": tutor_availability,
                                                                           "tutor_hourly_rate": tutor_hourly_rate,
                                                                           "tutor_bio": tutor_bio,
                                                                           "courses_length": courses_length,
                                                                           "bio_length": bio_length})


def student_profile(request):
    if is_Tutor(request.user):
        return HttpResponseRedirect("/KL/tutor")
    current_student = Student.objects.filter(username=request.user.username)[0]
    student_name = current_student.username
    return render(request, 'KnowledgeLink/student/student_profile_page.html', {'student_name': student_name})


def signup(request):
    # if account exists in database, send to /tutor or /student

    if Tutor.objects.filter(username=request.user.username).exists():
        return HttpResponseRedirect('/KL/tutor')
    elif Student.objects.filter(username=request.user.username).exists():
        return HttpResponseRedirect("/KL/student")
    else:
        if request.method == 'POST':
            if request.POST.get("save"):
                form = SignUpForm(request.POST)
                if form.is_valid():
                    Username = request.user.username

                    Role = form.cleaned_data["Signup"]

                    # make this compatible with a dropdown box thing
                    if Role == "tutor":

                        Account = Tutor(username=request.user.username, user_email=request.user.email, bio="")
                        Account.save()
                        return HttpResponseRedirect('/KL/tutor')
                    else:
                        Account = Student(username=request.user.username, user_email=request.user.email)
                        Account.save()
                        return HttpResponseRedirect('/KL/student')
        else:
            form = SignUpForm()
    return render(request, 'KnowledgeLink/signup.html', {'form': form})


def home_page(request):
    if Student.objects.filter(user_email=request.user.email).exists():
        return HttpResponseRedirect("/KL/student")
    else:
        return HttpResponseRedirect("/KL/tutor")


def tutor_search_courses(request):
    if is_Student(request.user):
        return HttpResponseRedirect("/KL/student")
    course = []
    if 'name' in request.GET and request.GET['name'] != '' and 'mnemonic' in request.GET and request.GET[
        'mnemonic'] != '' and 'number' in request.GET and request.GET['number'] != '':
        number = request.GET['number']
        name = request.GET['name']
        name = reCaps(name)
        mnemonic = request.GET['mnemonic']
        mnemonic = mnemonic.upper()

        if Course.objects.filter(course_number=number, course_name=name, course_mnemonic=mnemonic).exists():
            course = Course.objects.filter(course_number=number, course_name=name, course_mnemonic=mnemonic)
            return render(request, 'KnowledgeLink/courses.html', {'course': course})
        else:
            return render(request, 'KnowledgeLink/courses.html', {'error': True})

    if 'name' in request.GET and request.GET['name'] != '' and 'mnemonic' in request.GET and request.GET[
        'mnemonic'] != '':
        mnemonic = request.GET['mnemonic']
        mnemonic = mnemonic.upper()
        name = request.GET['name']
        name = reCaps(name)
        print(name)
        if Course.objects.filter(course_name=name, course_mnemonic=mnemonic).exists():
            course = Course.objects.filter(course_name=name, course_mnemonic=mnemonic)
            return render(request, 'KnowledgeLink/courses.html', {'course': course})
        else:
            return render(request, 'KnowledgeLink/courses.html', {'error': True})

    if 'number' in request.GET and request.GET['number'] != '' and 'name' in request.GET and request.GET['name'] != '':
        number = request.GET['number']
        name = request.GET['name']
        name = reCaps(name)
        if Course.objects.filter(course_number=number, course_name=name).exists():
            course = Course.objects.filter(course_number=number, course_name=name)
            return render(request, 'KnowledgeLink/courses.html', {'course': course})
        else:
            return render(request, 'KnowledgeLink/courses.html', {'error': True})

    if 'number' in request.GET and request.GET['number'] != '' and 'mnemonic' in request.GET and request.GET[
        'mnemonic'] != '':
        number = request.GET['number']
        mnemonic = request.GET['mnemonic']
        mnemonic = mnemonic.upper()
        if Course.objects.filter(course_number=number, course_mnemonic=mnemonic).exists():
            course = Course.objects.filter(course_number=number, course_mnemonic=mnemonic)
            return render(request, 'KnowledgeLink/courses.html', {'course': course})
        else:
            return render(request, 'KnowledgeLink/courses.html', {'error': True})

    if 'name' in request.GET and request.GET['name'] != '':
        name = request.GET['name']
        name = reCaps(name)
        if Course.objects.filter(course_name=name).exists():
            course = Course.objects.filter(course_name=name)
            return render(request, 'KnowledgeLink/courses.html', {'course': course})
        else:
            return render(request, 'KnowledgeLink/courses.html', {'error': True})
        
    if 'number' in request.GET and request.GET['number'] != '':
        number = request.GET['number']
        if Course.objects.filter(course_number=number).exists():
            course = Course.objects.filter(course_number=number)
            return render(request, 'KnowledgeLink/courses.html', {'course': course})
        else:
            return render(request, 'KnowledgeLink/courses.html', {'error': True})

    if 'mnemonic' in request.GET and request.GET['mnemonic'] != '':
        mnemonic = request.GET['mnemonic']
        mnemonic = mnemonic.upper()
        if Course.objects.filter(course_mnemonic=mnemonic).exists():
            course = Course.objects.filter(course_mnemonic=mnemonic)
            return render(request, 'KnowledgeLink/courses.html', {'course': course})
        else:
            return render(request, 'KnowledgeLink/courses.html', {'error': True})
    return render(request, 'KnowledgeLink/courses.html', {'flag': True})


def availability_set(request):
    if is_Student(request.user):
        return HttpResponseRedirect("/KL/student")
    current_tutor = Tutor.objects.filter(username=request.user.username)[0]
    tutor_availability = current_tutor.get_available_times()
    active_appointments = Appointment.objects.filter(tutor=current_tutor, status=1, is_active=True)
    appointment_matrix = [[] for x in range(7)]
    sun_appointments = []
    mon_appointments = []
    tue_appointments = []
    wed_appointments = []
    thu_appointments = []
    fri_appointments = []
    sat_appointments = []
    for i in active_appointments:
        if i.day == "Sunday":
            sun_appointments.append(i.time)
        elif i.day == "Monday":
            mon_appointments.append(i.time)
        elif i.day == "Tuesday":
            tue_appointments.append(i.time)
        elif i.day == "Wednesday":
            wed_appointments.append(i.time)
        elif i.day == "Thursday":
            thu_appointments.append(i.time)
        elif i.day == "Friday":
            fri_appointments.append(i.time)
        else:
            sat_appointments.append(i.time)
    sun_appointments = availability_time_convert(sun_appointments)
    mon_appointments = availability_time_convert(mon_appointments)
    tue_appointments = availability_time_convert(tue_appointments)
    wed_appointments = availability_time_convert(wed_appointments)
    thu_appointments = availability_time_convert(thu_appointments)
    fri_appointments = availability_time_convert(fri_appointments)
    sat_appointments = availability_time_convert(sat_appointments)
    tutor_sunday_availability = availability_time_convert(tutor_availability['Sunday'])
    tutor_monday_availability = availability_time_convert(tutor_availability['Monday'])
    tutor_tuesday_availability = availability_time_convert(tutor_availability['Tuesday'])
    tutor_wednesday_availability = availability_time_convert(tutor_availability['Wednesday'])
    tutor_thursday_availability = availability_time_convert(tutor_availability['Thursday'])
    tutor_friday_availability = availability_time_convert(tutor_availability['Friday'])
    tutor_saturday_availability = availability_time_convert(tutor_availability['Saturday'])
    if request.method == "POST":
        sunday_selections = request.POST.getlist("sunday")
        monday_selections = request.POST.getlist("monday")
        tuesday_selections = request.POST.getlist("tuesday")
        wednesday_selections = request.POST.getlist("wednesday")
        thursday_selections = request.POST.getlist("thursday")
        friday_selections = request.POST.getlist("friday")
        saturday_selections = request.POST.getlist("saturday")

        for i in sunday_selections:
            temp = (datetime.datetime(year=2001, month=1, day=3) + datetime.timedelta(hours=float(i))).time()
            current_tutor.add_available_time(0, temp)
            current_tutor.save()

        for i in monday_selections:
            temp = (datetime.datetime(year=2001, month=1, day=3) + datetime.timedelta(hours=float(i))).time()
            current_tutor.add_available_time(1, temp)
            current_tutor.save()

        for i in tuesday_selections:
            temp = (datetime.datetime(year=2001, month=1, day=3) + datetime.timedelta(hours=float(i))).time()
            current_tutor.add_available_time(2, temp)
            current_tutor.save()

        for i in wednesday_selections:
            temp = (datetime.datetime(year=2001, month=1, day=3) + datetime.timedelta(hours=float(i))).time()
            current_tutor.add_available_time(3, temp)
            current_tutor.save()

        for i in thursday_selections:
            temp = (datetime.datetime(year=2001, month=1, day=3) + datetime.timedelta(hours=float(i))).time()
            current_tutor.add_available_time(4, temp)
            current_tutor.save()

        for i in friday_selections:
            temp = (datetime.datetime(year=2001, month=1, day=3) + datetime.timedelta(hours=float(i))).time()
            current_tutor.add_available_time(5, temp)
            current_tutor.save()

        for i in saturday_selections:
            temp = (datetime.datetime(year=2001, month=1, day=3) + datetime.timedelta(hours=float(i))).time()
            current_tutor.add_available_time(6, temp)
            current_tutor.save()

        return HttpResponseRedirect(reverse('KnowledgeLink:tutor_profile'))
    else:
        return render(request, 'KnowledgeLink/tutor/availability.html',
                      {'tutor': current_tutor, 'indexes': range(48),
                       'tutor_sunday_availability': tutor_sunday_availability,
                       'tutor_monday_availability': tutor_monday_availability,
                       'tutor_tuesday_availability': tutor_tuesday_availability,
                       'tutor_wednesday_availability': tutor_wednesday_availability,
                       'tutor_thursday_availability': tutor_thursday_availability,
                       'tutor_friday_availability': tutor_friday_availability,
                       'tutor_saturday_availability': tutor_saturday_availability,
                       'tutor_sun_appointments': sun_appointments,
                       'tutor_mon_appointments': mon_appointments,
                       'tutor_tue_appointments': tue_appointments,
                       'tutor_wed_appointments': wed_appointments,
                       'tutor_thu_appointments': thu_appointments,
                       'tutor_fri_appointments': fri_appointments,
                       'tutor_sat_appointments': sat_appointments})


def availability_time_convert(availability):
    time_converted = set()
    for time in availability:
        time_converted.add((time.hour + (time.minute / 60)) * 2)
    return time_converted


# CODE USED TO PREPOPULATE THE DATABASE TO AID WITH SEARCHING
# def get_courses(request):
#     all_courses = {}
#     page_number = 1
#     url = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term=1232&page=%d' % page_number
#     response = requests.get(url)
#     data = response.json()
#     while not data == []:
#         for i in data:
#             if not Course.objects.filter(course_mnemonic=i['subject'], course_number=i['catalog_nbr'], course_name=i['descr']).exists():
#                 course_data = Course(
#                     course_mnemonic=i['subject'],
#                     course_number=i['catalog_nbr'],
#                     course_name=i['descr']
#                 )
#                 course_data.save()
#         page_number += 1
#         time.sleep(1)
#         print(Course.objects.all().count())
#         url = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term=1232&page=%d' % page_number
#         response = requests.get(url)
#         data = response.json()
#
#     all_courses = Course.objects.all()
#
#     return HttpResponseRedirect("/KL/detail")

def tutor_select(request):
    if is_Student(request.user):
        return HttpResponseRedirect("/KL/student")
    selected_courses = request.POST.getlist('course')
    if len(selected_courses) == 0:
        return render(request, 'KnowledgeLink/courses.html', {'error_message': "You didn't select a choice. ", })
    current_tutor = Tutor.objects.filter(username=request.user.username)[0]
    for i in selected_courses:
        current_tutor.courses.add(Course.objects.get(pk=int(i)))
    return HttpResponseRedirect(reverse('KnowledgeLink:tutor_profile'))


def search_tutors(request):
    if is_Tutor(request.user):
        return HttpResponseRedirect("/KL/tutor")
    tutors = []
    if 'name' in request.GET and request.GET['name'] != '' and 'mnemonic' in request.GET and request.GET[
        'mnemonic'] != '' and 'number' in request.GET and request.GET['number'] != '':
        number = request.GET['number']
        name = request.GET['name']
        name = reCaps(name)
        mnemonic = request.GET['mnemonic']
        mnemonic = mnemonic.upper()
        if Course.objects.filter(course_number=number, course_name=name, course_mnemonic=mnemonic).exists():
            course = Course.objects.filter(course_number=number, course_name=name, course_mnemonic=mnemonic)
            for c in course:
                if c.tutor_set.exists():
                    for t in c.tutor_set.all():
                        if t not in tutors:
                            tutors.append(t)
            if tutors:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutors': tutors})
            else:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutor_error': True})
        else:
            return render(request, 'KnowledgeLink/student/tutor_search.html', {'class_error': True})

    if 'name' in request.GET and request.GET['name'] != '' and 'mnemonic' in request.GET and request.GET[
        'mnemonic'] != '':
        name = request.GET['name']
        name = reCaps(name)
        mnemonic = request.GET['mnemonic']
        mnemonic = mnemonic.upper()
        if Course.objects.filter(course_name=name, course_mnemonic=mnemonic).exists():
            course = Course.objects.filter(course_name=name, course_mnemonic=mnemonic)
            for c in course:
                if c.tutor_set.exists():
                    for t in c.tutor_set.all():
                        if t not in tutors:
                            tutors.append(t)
            if tutors:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutors': tutors})
            else:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutor_error': True})
        else:
            return render(request, 'KnowledgeLink/student/tutor_search.html', {'class_error': True})

    if 'name' in request.GET and request.GET['name'] != '' and 'number' in request.GET and request.GET['number'] != '':
        number = request.GET['number']
        name = request.GET['name']
        name = reCaps(name)
        if Course.objects.filter(course_number=number, course_name=name).exists():
            course = Course.objects.filter(course_number=number, course_name=name)
            for c in course:
                if c.tutor_set.exists():
                    for t in c.tutor_set.all():
                        if t not in tutors:
                            tutors.append(t)
            if tutors:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutors': tutors})
            else:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutor_error': True})
        else:
            return render(request, 'KnowledgeLink/student/tutor_search.html', {'class_error': True})

    if 'mnemonic' in request.GET and request.GET[
        'mnemonic'] != '' and 'number' in request.GET and request.GET['number'] != '':
        number = request.GET['number']
        mnemonic = request.GET['mnemonic']
        mnemonic = mnemonic.upper()
        if Course.objects.filter(course_number=number, course_mnemonic=mnemonic).exists():
            course = Course.objects.filter(course_number=number, course_mnemonic=mnemonic)
            for c in course:
                if c.tutor_set.exists():
                    for t in c.tutor_set.all():
                        if t not in tutors:
                            tutors.append(t)
            if tutors:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutors': tutors})
            else:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutor_error': True})
        else:
            return render(request, 'KnowledgeLink/student/tutor_search.html', {'class_error': True})

    if 'name' in request.GET and request.GET['name'] != '':
        name = request.GET['name']
        name = reCaps(name)
        if Course.objects.filter(course_name=name).exists():
            course = Course.objects.filter(course_name=name)
            for c in course:
                if c.tutor_set.exists():
                    for t in c.tutor_set.all():
                        if t not in tutors:
                            tutors.append(t)
            if tutors:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutors': tutors})
            else:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutor_error': True})
        else:
            return render(request, 'KnowledgeLink/student/tutor_search.html', {'class_error': True})

    if 'number' in request.GET and request.GET['number'] != '':
        number = request.GET['number']
        if Course.objects.filter(course_number=number).exists():
            course = Course.objects.filter(course_number=number)
            for c in course:
                if c.tutor_set.exists():
                    for t in c.tutor_set.all():
                        if t not in tutors:
                            tutors.append(t)
            if tutors:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutors': tutors})
            else:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutor_error': True})
        else:
            return render(request, 'KnowledgeLink/student/tutor_search.html', {'class_error': True})

    if 'mnemonic' in request.GET and request.GET[
        'mnemonic'] != '':
        mnemonic = request.GET['mnemonic']
        mnemonic = mnemonic.upper()
        if Course.objects.filter(course_mnemonic=mnemonic).exists():
            course = Course.objects.filter(course_mnemonic=mnemonic)
            for c in course:
                if c.tutor_set.exists():
                    for t in c.tutor_set.all():
                        if t not in tutors:
                            tutors.append(t)
            if tutors:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutors': tutors})
            else:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutor_error': True})
        else:
            return render(request, 'KnowledgeLink/student/tutor_search.html', {'class_error': True})

    return render(request, 'KnowledgeLink/student/tutor_search.html')





def search_tutors_error(request):
    if is_Tutor(request.user):
        return HttpResponseRedirect("/KL/tutor")
    tutors = []
    

    if 'name' in request.GET and request.GET['name'] != '' and 'mnemonic' in request.GET and request.GET[
        'mnemonic'] != '' and 'number' in request.GET and request.GET['number'] != '':
        number = request.GET['number']
        name = request.GET['name']
        name = reCaps(name)
        mnemonic = request.GET['mnemonic']
        mnemonic = mnemonic.upper()
        if Course.objects.filter(course_number=number, course_name=name, course_mnemonic=mnemonic).exists():
            course = Course.objects.filter(course_number=number, course_name=name, course_mnemonic=mnemonic)
            for c in course:
                if c.tutor_set.exists():
                    for t in c.tutor_set.all():
                        if t not in tutors:
                            tutors.append(t)
            if tutors:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutors': tutors})
            else:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutor_error': True})
        else:
            return render(request, 'KnowledgeLink/student/tutor_search.html', {'class_error': True})

    if 'name' in request.GET and request.GET['name'] != '' and 'mnemonic' in request.GET and request.GET[
        'mnemonic'] != '':
        name = request.GET['name']
        name = reCaps(name)
        mnemonic = request.GET['mnemonic']
        mnemonic = mnemonic.upper()
        if Course.objects.filter(course_name=name, course_mnemonic=mnemonic).exists():
            course = Course.objects.filter(course_name=name, course_mnemonic=mnemonic)
            for c in course:
                if c.tutor_set.exists():
                    for t in c.tutor_set.all():
                        if t not in tutors:
                            tutors.append(t)
            if tutors:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutors': tutors})
            else:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutor_error': True})
        else:
            return render(request, 'KnowledgeLink/student/tutor_search.html', {'class_error': True})

    if 'name' in request.GET and request.GET['name'] != '' and 'number' in request.GET and request.GET['number'] != '':
        number = request.GET['number']
        name = request.GET['name']
        name = reCaps(name)
        if Course.objects.filter(course_number=number, course_name=name).exists():
            course = Course.objects.filter(course_number=number, course_name=name)
            for c in course:
                if c.tutor_set.exists():
                    for t in c.tutor_set.all():
                        if t not in tutors:
                            tutors.append(t)
            if tutors:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutors': tutors})
            else:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutor_error': True})
        else:
            return render(request, 'KnowledgeLink/student/tutor_search.html', {'class_error': True})

    if 'mnemonic' in request.GET and request.GET[
        'mnemonic'] != '' and 'number' in request.GET and request.GET['number'] != '':
        number = request.GET['number']
        mnemonic = request.GET['mnemonic']
        mnemonic = mnemonic.upper()
        if Course.objects.filter(course_number=number, course_mnemonic=mnemonic).exists():
            course = Course.objects.filter(course_number=number, course_mnemonic=mnemonic)
            for c in course:
                if c.tutor_set.exists():
                    for t in c.tutor_set.all():
                        if t not in tutors:
                            tutors.append(t)
            if tutors:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutors': tutors})
            else:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutor_error': True})
        else:
            return render(request, 'KnowledgeLink/student/tutor_search.html', {'class_error': True})

    if 'name' in request.GET and request.GET['name'] != '':
        name = request.GET['name']
        name = reCaps(name)
        if Course.objects.filter(course_name=name).exists():
            course = Course.objects.filter(course_name=name)
            for c in course:
                if c.tutor_set.exists():
                    for t in c.tutor_set.all():
                        if t not in tutors:
                            tutors.append(t)
            if tutors:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutors': tutors})
            else:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutor_error': True})
        else:
            return render(request, 'KnowledgeLink/student/tutor_search.html', {'class_error': True})

    if 'number' in request.GET and request.GET['number'] != '':
        number = request.GET['number']
        if Course.objects.filter(course_number=number).exists():
            course = Course.objects.filter(course_number=number)
            for c in course:
                if c.tutor_set.exists():
                    for t in c.tutor_set.all():
                        if t not in tutors:
                            tutors.append(t)
            if tutors:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutors': tutors})
            else:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutor_error': True})
        else:
            return render(request, 'KnowledgeLink/student/tutor_search.html', {'class_error': True})

    if 'mnemonic' in request.GET and request.GET[
        'mnemonic'] != '':
        mnemonic = request.GET['mnemonic']
        mnemonic = mnemonic.upper()
        if Course.objects.filter(course_mnemonic=mnemonic).exists():
            course = Course.objects.filter(course_mnemonic=mnemonic)
            for c in course:
                if c.tutor_set.exists():
                    for t in c.tutor_set.all():
                        if t not in tutors:
                            tutors.append(t)
            if tutors:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutors': tutors})
            else:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutor_error': True})
        else:
            return render(request, 'KnowledgeLink/student/tutor_search.html', {'class_error': True})

    return render(request, 'KnowledgeLink/student/tutor_search.html')



    if 'name' in request.GET and request.GET['name'] != '':
        name = request.GET['name']
        name = reCaps(name)
        if Course.objects.filter(course_name=name).exists():
            course = Course.objects.filter(course_name=name)
            for c in course:
                if c.tutor_set.exists():
                    for t in c.tutor_set.all():
                        if t not in tutors:
                            tutors.append(t)
            if tutors:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutors': tutors})
            else:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutor_error': True})
        else:
            return render(request, 'KnowledgeLink/student/tutor_search.html', {'class_error': True})

    if 'number' in request.GET and request.GET['number'] != '':
        number = request.GET['number']
        if Course.objects.filter(course_number=number).exists():
            course = Course.objects.filter(course_number=number)
            for c in course:
                if c.tutor_set.exists():
                    for t in c.tutor_set.all():
                        if t not in tutors:
                            tutors.append(t)
            if tutors:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutors': tutors})
            else:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutor_error': True})
        else:
            return render(request, 'KnowledgeLink/student/tutor_search.html', {'class_error': True})

    if 'mnemonic' in request.GET and request.GET[
        'mnemonic'] != '':
        mnemonic = request.GET['mnemonic']
        mnemonic = mnemonic.upper()
        if Course.objects.filter(course_mnemonic=mnemonic).exists():
            course = Course.objects.filter(course_mnemonic=mnemonic)
            for c in course:
                if c.tutor_set.exists():
                    for t in c.tutor_set.all():
                        if t not in tutors:
                            tutors.append(t)
            if tutors:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutors': tutors})
            else:
                return render(request, 'KnowledgeLink/student/tutor_search.html', {'tutor_error': True})
        else:
            return render(request, 'KnowledgeLink/student/tutor_search.html', {'class_error': True})

    return render(request, 'KnowledgeLink/student/tutor_search.html', {'button_error': True})


def tutor_request(request):
    if is_Tutor(request.user):
        return HttpResponseRedirect("/KL/tutor")
    if 'time' in request.POST and request.POST['time'] != '':    
        selected_tutor = request.POST.get('tutor')
        tutor = Tutor.objects.get(pk=int(selected_tutor))
        selected_course = request.POST.get('course')
        course = Course.objects.get(pk=int(selected_course))
        selected_day = request.POST.get('selected_day')
        selected_time = request.POST.get('time')
        print(selected_time)
        split_time = selected_time.split(':')
        if split_time[1] == "30":
            time = datetime.time(int(split_time[0]), 30)
        else:
            time = datetime.time(int(split_time[0]), 0)
        current_student = Student.objects.filter(username=request.user.username)[0]
        appointment = Appointment(student=current_student, tutor=tutor, course=course, day=selected_day, time=time)
        appointment.save()
        return HttpResponseRedirect('/KL/student/appointment/{}/status'.format(appointment.id))
    else:
        return redirect('KnowledgeLink:request_tutor_error')


def appointment_decision(request, appointment_id):
    if is_Student(request.user):
        return HttpResponseRedirect("/KL/student")
    try:
        current_appointment = Appointment.objects.get(pk=appointment_id)
    except Appointment.DoesNotExist:
        raise Http404("Appointment does not exist")
    if request.user.username == current_appointment.tutor.username:
        return render(request, "KnowledgeLink/appointment.html", context={'appointment': current_appointment})


def appointment_approved(request):
    current_appointment = request.POST.get('appointment')
    appointment = Appointment.objects.get(pk=int(current_appointment))
    appointment.status = 1
    appointment.tutor.remove_available_time(day_of_week=day_index[appointment.day], time=appointment.time)
    appointment.tutor.save()
    appointment.save()
    return HttpResponseRedirect('/KL/tutor')


def appointment_rejected(request):
    current_appointment = request.POST.get('appointment')
    appointment = Appointment.objects.get(pk=int(current_appointment))
    appointment.status = 0
    appointment.is_active = False
    appointment.save()
    return HttpResponseRedirect('/KL/tutor')


def tutor_request_page(request):
    if is_Tutor(request.user):
        return HttpResponseRedirect("/KL/tutor")
    if 'tutor' in request.POST and request.POST['tutor'] != '':
        selected_tutor = request.POST.get('tutor')
        tutor = Tutor.objects.get(pk=int(selected_tutor))
        tutor_courses = tutor.courses.all()
        tutor_availability = tutor.get_available_times()

        tutor_sunday_availability = convert_time(tutor_availability['Sunday'])
        tutor_monday_availability = convert_time(tutor_availability['Monday'])
        tutor_tuesday_availability = convert_time(tutor_availability['Tuesday'])
        tutor_wednesday_availability = convert_time(tutor_availability['Wednesday'])
        tutor_thursday_availability = convert_time(tutor_availability['Thursday'])
        tutor_friday_availability = convert_time(tutor_availability['Friday'])
        tutor_saturday_availability = convert_time(tutor_availability['Saturday'])
        return render(request, 'KnowledgeLink/student/tutor_request.html', {'tutor': tutor, 'tutor_courses': tutor_courses,
                                                                            'tutor_sunday_availability': tutor_sunday_availability,
                                                                            'tutor_monday_availability': tutor_monday_availability,
                                                                            'tutor_tuesday_availability': tutor_tuesday_availability,
                                                                            'tutor_wednesday_availability': tutor_wednesday_availability,
                                                                            'tutor_thursday_availability': tutor_thursday_availability,
                                                                            'tutor_friday_availability': tutor_friday_availability,
                                                                            'tutor_saturday_availability': tutor_saturday_availability})
    else:
        return redirect('KnowledgeLink:tutor_search_error')

def tutor_request_error(request):
    if is_Tutor(request.user):
        return HttpResponseRedirect("/KL/tutor")
    if 'tutor' in request.POST and request.POST['tutor'] != '':
        selected_tutor = request.POST.get('tutor')
        tutor = Tutor.objects.get(pk=int(selected_tutor))
        tutor_courses = tutor.courses.all()
        tutor_availability = tutor.get_available_times()

        tutor_sunday_availability = convert_time(tutor_availability['Sunday'])
        tutor_monday_availability = convert_time(tutor_availability['Monday'])
        tutor_tuesday_availability = convert_time(tutor_availability['Tuesday'])
        tutor_wednesday_availability = convert_time(tutor_availability['Wednesday'])
        tutor_thursday_availability = convert_time(tutor_availability['Thursday'])
        tutor_friday_availability = convert_time(tutor_availability['Friday'])
        tutor_saturday_availability = convert_time(tutor_availability['Saturday'])
        return render(request, 'KnowledgeLink/student/tutor_request.html', {'tutor': tutor, 'error': True, 'tutor_courses': tutor_courses,
                                                                            'tutor_sunday_availability': tutor_sunday_availability,
                                                                            'tutor_monday_availability': tutor_monday_availability,
                                                                            'tutor_tuesday_availability': tutor_tuesday_availability,
                                                                            'tutor_wednesday_availability': tutor_wednesday_availability,
                                                                            'tutor_thursday_availability': tutor_thursday_availability,
                                                                            'tutor_friday_availability': tutor_friday_availability,
                                                                            'tutor_saturday_availability': tutor_saturday_availability})
    else:
        return redirect('KnowledgeLink:tutor_search_error')


def convert_time(availability):
    time_converted = []
    for time in availability:
        time_converted.append(time.strftime("%H:%M"))
    return time_converted


def set_rate(request):
    if is_Student(request.user):
        return HttpResponseRedirect("/KL/student")
    if request.method == "POST":
        if request.POST.get("save"):
            form = HourlyRateForm(request.POST)
            if form.is_valid():
                curr_tutor = Tutor.objects.filter(username=request.user.username)[0]
                curr_tutor.hourly_rate = form.cleaned_data["rate"]
                curr_tutor.save()
                return HttpResponseRedirect("profile")
            else:
                form = HourlyRateForm()
                return render(request, 'KnowledgeLink/tutor/tutor_rate.html', {'form': form, 'error': True})
    else:
        form = HourlyRateForm()
        return render(request, 'KnowledgeLink/tutor/tutor_rate.html', {'form': form})


def set_bio(request):
    if is_Student(request.user):
        return HttpResponseRedirect("/KL/student")
    if request.method == "POST":
        if request.POST.get("save"):
            form = TutorBioForm(request.POST)
            if form.is_valid():
                curr_tutor = Tutor.objects.filter(username=request.user.username)[0]
                curr_tutor.bio = form.cleaned_data["bio"]
                curr_tutor.save()
                return HttpResponseRedirect("profile")
            else:
                return HttpResponseRedirect("set_bio")
    else:
        form = TutorBioForm()
        return render(request, 'KnowledgeLink/tutor/tutor_bio.html', {'form': form})

# **************************************************************************************
# *  REFERENCES
# *  Title: Working With iCalendar in Python
# *  Author: Xavier Rigoulet
# *  Date: February 15th, 2022
# *  URL: https://learnpython.com/blog/working-with-icalendar-with-python/
# *
# ********************************************************************

def calendar_tutor(request):
    curr_tutor = Tutor.objects.filter(username=request.user.username)[0]
    active_appointments = Appointment.objects.filter(tutor=curr_tutor, status=1, is_active=True)
    if len(active_appointments) == 0:
        return HttpResponseRedirect('KL/tutor')
    tutor_cal = Calendar()
    tutor_cal.add('prodid', '-//Group A-19//tutorme-a19.herokuapp.com//')
    tutor_cal.add('version', '2.0')
    next_sun = datetime.date.today() + relativedelta(weekday=SU(1))
    next_mon = datetime.date.today() + relativedelta(weekday=MO(1))
    next_tue = datetime.date.today() + relativedelta(weekday=TU(1))
    next_wed = datetime.date.today() + relativedelta(weekday=WE(1))
    next_thu = datetime.date.today() + relativedelta(weekday=TH(1))
    next_fri = datetime.date.today() + relativedelta(weekday=FR(1))
    next_sat = datetime.date.today() + relativedelta(weekday=SA(1))
    for i in active_appointments:
        curr_event = Event()
        curr_event.add('SUMMARY', 'Tutoring Appointment with: {}'.format(i.student.username))
        if i.day == "Sunday":
            time = datetime.datetime(next_sun.year, next_sun.month, next_sun.day, i.time.hour, i.time.minute,
                                     i.time.second, tzinfo=pytz.timezone('US/Eastern'))
        elif i.day == "Monday":
            time = datetime.datetime(next_mon.year, next_mon.month, next_mon.day, i.time.hour, i.time.minute,
                                     i.time.second, tzinfo=pytz.timezone('US/Eastern'))
        elif i.day == "Tuesday":
            time = datetime.datetime(next_tue.year, next_tue.month, next_tue.day, i.time.hour, i.time.minute,
                                     i.time.second, tzinfo=pytz.timezone('US/Eastern'))
        elif i.day == "Wednesday":
            time = datetime.datetime(next_wed.year, next_wed.month, next_wed.day, i.time.hour, i.time.minute,
                                     i.time.second, tzinfo=pytz.timezone('US/Eastern'))
        elif i.day == "Thursday":
            time = datetime.datetime(next_thu.year, next_thu.month, next_thu.day, i.time.hour, i.time.minute,
                                     i.time.second, tzinfo=pytz.timezone('US/Eastern'))
        elif i.day == "Friday":
            time = datetime.datetime(next_fri.year, next_fri.month, next_fri.day, i.time.hour, i.time.minute,
                                     i.time.second, tzinfo=pytz.timezone('US/Eastern'))
        else:
            time = datetime.datetime(next_sat.year, next_sat.month, next_sat.day, i.time.hour, i.time.minute,
                                     i.time.second, tzinfo=pytz.timezone('US/Eastern'))
        curr_event.add('dtstart', time)
        end_time = time + datetime.timedelta(minutes=30)
        curr_event.add('dtend', end_time)
        tutor_cal.add_component(curr_event)
        time_iter = time + datetime.timedelta(days=7)
        for j in range(16):
            next_event = Event()
            next_event.add('SUMMARY', 'Tutoring Appointment with: {}'.format(i.student.username))
            next_event.add('dtstart', time_iter)
            end_time_iter = time_iter + datetime.timedelta(minutes=30)
            next_event.add('dtend', end_time_iter)
            tutor_cal.add_component(next_event)
            time_iter = time_iter + datetime.timedelta(days=7)

    response = HttpResponse(tutor_cal.to_ical(), content_type="text/calendar")
    response["Content-Disposition"] = "attachment; filename={}.ics".format(curr_tutor.username)
    return response


def calendar_student(request):
    curr_student = Student.objects.filter(username=request.user.username)[0]
    active_appointments = Appointment.objects.filter(student=curr_student, status=1, is_active=True)
    if len(active_appointments) == 0:
        return HttpResponseRedirect('KL/student')
    student_cal = Calendar()
    student_cal.add('prodid', '-//Group A-19//tutorme-a19.herokuapp.com//')
    student_cal.add('version', '2.0')
    next_sun = datetime.date.today() + relativedelta(weekday=SU(1))
    next_mon = datetime.date.today() + relativedelta(weekday=MO(1))
    next_tue = datetime.date.today() + relativedelta(weekday=TU(1))
    next_wed = datetime.date.today() + relativedelta(weekday=WE(1))
    next_thu = datetime.date.today() + relativedelta(weekday=TH(1))
    next_fri = datetime.date.today() + relativedelta(weekday=FR(1))
    next_sat = datetime.date.today() + relativedelta(weekday=SA(1))
    for i in active_appointments:
        curr_event = Event()
        curr_event.add('SUMMARY', 'Tutoring Session with: {}'.format(i.tutor.username))
        curr_event.add('DESCRIPTION', 'For {}'.format(i.course.course_name))
        if i.day == "Sunday":
            time = datetime.datetime(next_sun.year, next_sun.month, next_sun.day, i.time.hour, i.time.minute,
                                     i.time.second, tzinfo=pytz.timezone('US/Eastern'))
        elif i.day == "Monday":
            time = datetime.datetime(next_mon.year, next_mon.month, next_mon.day, i.time.hour, i.time.minute,
                                     i.time.second, tzinfo=pytz.timezone('US/Eastern'))
        elif i.day == "Tuesday":
            time = datetime.datetime(next_tue.year, next_tue.month, next_tue.day, i.time.hour, i.time.minute,
                                     i.time.second, tzinfo=pytz.timezone('US/Eastern'))
        elif i.day == "Wednesday":
            time = datetime.datetime(next_wed.year, next_wed.month, next_wed.day, i.time.hour, i.time.minute,
                                     i.time.second, tzinfo=pytz.timezone('US/Eastern'))
        elif i.day == "Thursday":
            time = datetime.datetime(next_thu.year, next_thu.month, next_thu.day, i.time.hour, i.time.minute,
                                     i.time.second, tzinfo=pytz.timezone('US/Eastern'))
        elif i.day == "Friday":
            time = datetime.datetime(next_fri.year, next_fri.month, next_fri.day, i.time.hour, i.time.minute,
                                     i.time.second, tzinfo=pytz.timezone('US/Eastern'))
        else:
            time = datetime.datetime(next_sat.year, next_sat.month, next_sat.day, i.time.hour, i.time.minute,
                                     i.time.second, tzinfo=pytz.timezone('US/Eastern'))
        curr_event.add('dtstart', time)
        end_time = time + datetime.timedelta(minutes=30)
        curr_event.add('dtend', end_time)
        student_cal.add_component(curr_event)
        time_iter = time + datetime.timedelta(days=7)
        for j in range(16):
            next_event = Event()
            next_event.add('SUMMARY', 'Tutoring Session with: {}'.format(i.tutor.username))
            next_event.add('DESCRIPTION', 'For {}'.format(i.course.course_name))
            next_event.add('dtstart', time_iter)
            end_time_iter = time_iter + datetime.timedelta(minutes=30)
            next_event.add('dtend', end_time_iter)
            student_cal.add_component(next_event)
            time_iter = time_iter + datetime.timedelta(days=7)

    response = HttpResponse(student_cal.to_ical(), content_type="text/calendar")
    response["Content-Disposition"] = "attachment; filename={}.ics".format(curr_student.username)
    return response

def rate_tutor_select(request):
    if is_Tutor(request.user):
        return HttpResponseRedirect("/KL/tutor")
    current_student = Student.objects.filter(username=request.user.username)[0]
    appointments = Appointment.objects.filter(student=current_student)
    appointment_tutors = []
    for appointment in appointments:
        appointment_tutors.append(appointment.tutor)
    appointment_tutors= [*set(appointment_tutors)]
    for tutor in appointment_tutors:
        if current_student in tutor.students_rated.all():
            appointment_tutors.remove(tutor)
    return render(request, 'KnowledgeLink/student/rate_tutors.html', {"appointment_tutors": appointment_tutors})

def rate_tutor(request):
    current_student = Student.objects.filter(username=request.user.username)[0]
    if is_Tutor(request.user):
        return HttpResponseRedirect("/KL/tutor")
    selected_tutor = request.POST.get("tutor")
    tutor = Tutor.objects.get(pk=int(selected_tutor))
    vote_type = request.POST.get("vote_type")
    if vote_type == "upvote":
        tutor.upvotes += 1
    else:
        tutor.downvotes += 1
    tutor.students_rated.add(current_student)
    tutor.save()
    return HttpResponseRedirect('/KL/student')

def rate_tutor_page(request):
    if is_Tutor(request.user):
        return HttpResponseRedirect("/KL/tutor")
    if 'tutor' in request.POST and request.POST['tutor'] != '':
        selected_tutor = request.POST.get('tutor')
        tutor = Tutor.objects.get(pk=int(selected_tutor))

        return render(request, 'KnowledgeLink/student/rate_tutor_selected.html', {'tutor': tutor})
    else:
        return redirect('KnowledgeLink:tutor_search_error')


def is_Student(user):
    if Student.objects.filter(username=user.username).exists():
        return True
    return False

def is_Tutor(user):
    if Tutor.objects.filter(username=user.username).exists():
        return True
    return False

def reCaps(string):
    string = string.capitalize()
    low_words = ["a", "an", "the", "and", "but", "or", "nor", "for", "yet", "so", "at", "by", "for", "in", "of", "on", "to", "up", "as", "with", "from", "into", "onto", "than", "that", "this", "down", "off", "out", "over", "till", "up", "via", "among", "amid", "around", "as", "despite", "during", "except", "into", "like", "near", "past", "per", "plus", "sans", "save", "than", "unlike", "upon", "via", "worth"]
    string_arr = string.split(" ")
    if len(string_arr) == 1:
        return string
    for word in range(1,len(string_arr)):
        if not(string_arr[word] in low_words):

            string_arr[word] = string_arr[word].capitalize()
        else:
            string_arr[word] = string_arr[word].lower()
    finalstring = " ".join(string_arr)
    finalstring = finalstring.strip()
    return finalstring


