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

class Clubcreate(CreateView):
    model = Club
    fields = ['club_name' , 'max_people_num' , 'noe_people_num']
    def form_valid(self, form):
        form.instance.club_id = self.kwargs['cid']
        return super().form_valid(form)
    def get_success_url(self):
        return reverse_lazy('log_list')