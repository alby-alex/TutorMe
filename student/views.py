from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from KnowledgeLink.models import *
from django.urls import reverse
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import *
from allauth.socialaccount import *
import time
import requests


def appointment_status(request, appointment_id):
    try:
        current_appointment = Appointment.objects.get(pk=appointment_id)
    except Appointment.DoesNotExist:
        raise Http404("Appointment does not exist")
    current_student = current_appointment.student
    if current_student.username != request.user.username:
        raise Http404("You cannot access this appointment")
    else:
        return render(request, "KnowledgeLink/student/appointment_status.html",
                    {"current_appointment": current_appointment})
