from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from .views import Loglist, Clubcreate, Applylist, Usercreate, Applycreate, Clublist, Applyview, register
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("", Loglist.as_view() ,name='log_list'),
    path("add/", Clubcreate.as_view(), name='club_create'),
    path("apply/", Applylist.as_view(), name='apply_list'),
    path("user/", Usercreate.as_view(), name='user_create'),
    path("capply/", Applycreate.as_view(), name='apply_create'),
    path("club/", Clublist.as_view(), name='club_list'),
    path("<int:pk>/", Applyview.as_view(), name='apply_detail'),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("login/", LoginView.as_view(), name='login'),
    path('register/', register, name='register'),
]