from django.urls import path, include
from django.views.generic import TemplateView
from . import views

app_name = 'KnowledgeLink'
urlpatterns = [
    # path('', TemplateView.as_view(template_name="index.html")),
    path('', views.signup, name='signup'),
    path('tutor/', include('tutor.urls')),
    path('student/', include('student.urls')),
    path('course/', views.tutor_search_courses, name='search'),
    path('profile/', views.tutor_profile, name = 'tutor_profile'),
    path('home/', views.home_page, name = 'home_page')
]
#