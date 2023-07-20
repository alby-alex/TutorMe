from django.urls import path

from KnowledgeLink.urls import views


urlpatterns = [
    path('', views.tutor, name='tutor'),
    path('profile', views.tutor_profile, name = 'tutor_profile'),
    path('course_search', views.tutor_search_courses, name = 'tutor_search'),
    path('add_course', views.tutor_select, name = 'select_tutor'),
    path('set_availability', views.availability_set, name = 'set_availability'),
    path('appointment/<int:appointment_id>/', views.appointment_decision, name='appointment_decision'),
    path('accepted', views.appointment_approved, name = 'approve_appointment'),
    path('rejected', views.appointment_rejected, name = 'reject_appointment'),
    path('set_rate', views.set_rate, name = "set_rate"),
    path('set_bio', views.set_bio, name = 'set_bio'),
    path('calendar_file', views.calendar_tutor, name = 'get_calendar_tutor'),
]