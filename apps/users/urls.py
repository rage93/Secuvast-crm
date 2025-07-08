from django.urls import path
from apps.users import views


urlpatterns = [
    path('profile/', views.profile, name='user_profile'),
    path('upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('change-password/', views.change_password, name='change_password'),
    path('change-mode/', views.change_mode, name='change_mode'),
    path('create/', views.create_user, name='tenant_create_user'),
    path('invite/', views.invite_user, name='invite_user'),
    path('accept-invite/<str:token>/', views.accept_invite, name='accept_invite'),
]
