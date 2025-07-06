from django.urls import path

from apps.react import views

urlpatterns = [
    path("react-charts", views.charts, name="react_charts"),
]
