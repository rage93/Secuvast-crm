from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_company, name='signup_company'),
    path('signup/success/', views.signup_success, name='signup_success'),
    path('info/', views.company_info, name='company_info'),
    path('users/', views.company_users, name='company_users'),
]

