from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from .views import (
    Loglist,
    Clubcreate,
    Applylist,
    Usercreate,
    Applycreate,
    Clublist,
    Applyview,
    ApplyUpdate,
    approve_sstu,
    approve_sch,
    login_view,
    logout_view,
    no_permission,
)

urlpatterns = [
    path("login/", login_view, name='login'),
    path("logout/", logout_view, name='logout'),
    path("forbidden/", no_permission, name='no_permission'),
    path("", Loglist.as_view() ,name='log_list'),
    path("add/", Clubcreate.as_view(), name='club_create'),
    path("<int:pk>/edit/", ApplyUpdate.as_view(), name='apply_edit'),
    path("<int:pk>/approve/sstu/", approve_sstu, name='approve_sstu'),
    path("<int:pk>/approve/sch/", approve_sch, name='approve_sch'),
    path("apply/", Applylist.as_view(), name='apply_list'),
    path("user/", Usercreate.as_view(), name='user_create'),
    path("capply/", Applycreate.as_view(), name='apply_create'),
    path("club/", Clublist.as_view(), name='club_list'),
    path("<int:pk>/", Applyview.as_view(), name='apply_detail'),
]