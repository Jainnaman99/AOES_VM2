from django.urls import path
from . import views

urlpatterns = [
    path("<int:year>/<int:month>/", views.calendar, name="calendar"),
    path("summary/", views.summary, name="summary")
]