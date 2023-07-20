from django.urls import path

from KnowledgeLink.urls import views
from . import views as student_views

urlpatterns = [
    path('', views.student, name='student'),
    path('search', views.search_tutors, name="tutor_search"),
    path('search_again', views.search_tutors_error, name="tutor_search_error"),
    path('request_again', views.tutor_request_error, name="request_tutor_error"),

    path('profile', views.student_profile, name = 'student_profile'),
    path('request', views.tutor_request_page, name = 'request'),

    path('appointment', views.tutor_request, name='appointment'),
    path('appointment/<int:appointment_id>/status', student_views.appointment_status, name = 'appointment_status'),

    path('calendar_file', views.calendar_student, name="get_calendar_student"),
    path('rate_tutors_select', views.rate_tutor_select, name = 'rate_tutor_select'),
    path('rate_tutor', views.rate_tutor, name="rate_tutor"),
    path('rate_selected_tutor', views.rate_tutor_page, name = 'rate_tutor_page'),
]