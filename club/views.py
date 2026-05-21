from django.shortcuts import render
from .models import User, Club, Apply, Log
from django.views.generic import ListView, DeleteView, RedirectView, CreateView
from django.urls import reverse_lazy
# Create your views here.

def club_list(req):
    clubs = Log.objects.select_related('club__club_name').all() #?不知是否可行
    return render(req, "club/log_list.html",{'club_list':clubs})

class Loglist(ListView):
    model = Log
    
    def get_context_data(self, **kwargs):
        ctx =  super().get_context_data(**kwargs)
        ctx['club_list'] = Club.objects.all()
        return ctx

class Clubcreate(CreateView):
    model = Club
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('log_list')
    
class Applylist(ListView):
    model = Apply

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['user_list'] = User.objects.all()
        ctx['log_list_check'] = Log.objects.filter(state = 1)
        ctx['log_list_pass'] = Log.objects.filter(state = 2)
        ctx['log_list_fail'] = Log.objects.filter(state = 0)
        return ctx

class Usercreate(CreateView):
    model = User
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('log_list')

class Applycreate(CreateView):
    model = Apply
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('log_list')
    
class Clublist(ListView):
    model = Club
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['club_list'] = Club.objects.all()
        #社長姓名
        #申請轉設中的人數        
        return ctx