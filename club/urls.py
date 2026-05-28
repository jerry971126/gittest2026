from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from .views import Loglist, Clubcreate, Applylist, Applycreate, Clublist, Applyview, UserRegisterView, success_msg, ApplyDelete,ApplyUpdate

urlpatterns = [
    path("", Loglist.as_view() ,name='log_list'),
    path("add/", Clubcreate.as_view(), name='club_create'),
    path("apply/", Applylist.as_view(), name='apply_list'),
    path("<int:pk>/aupdate/", ApplyUpdate.as_view(), name='apply_update'),
    # path("user/", Usercreate.as_view(), name='user_create'),
    path("capply/", Applycreate.as_view(), name='apply_create'),
    path("club/", Clublist.as_view(), name='club_list'),
    path("<int:pk>/", Applyview.as_view(), name='apply_detail'),
    path("register/", UserRegisterView.as_view(), name='register'),
    path("success/", success_msg, name= 'success'),
    path("<int:pk>/adelete/", ApplyDelete.as_view(), name='apply_delete'),
]