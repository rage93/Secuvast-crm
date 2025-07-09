from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_company, name='signup_company'),
    path('signup/success/', views.signup_success, name='signup_success'),
    path('choose-plan/', views.choose_plan, name='choose_plan'),
    path('info/', views.company_info, name='company_info'),
    path('users/', views.company_users, name='company_users'),
    path('billing/', views.billing_portal, name='billing_portal'),
    path('healthz/', views.healthz, name='company_healthz'),
    path('not-found/', views.company_not_found, name='company_not_found'),

]

