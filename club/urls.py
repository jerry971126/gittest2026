from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from .views import Loglist, Clubcreate

urlpatterns = [
    path("", Loglist.as_view() , name='log_list'),
    path("add/", Clubcreate.as_view(),   name='club_create'),
]