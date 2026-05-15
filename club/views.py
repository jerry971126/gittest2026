from django.shortcuts import render
from .models import User, Club, Apply, Log
from django.views.generic import ListView, DeleteView, RedirectView, CreateView
from django.urls import reverse_lazy
# Create your views here.

def club_list(req):
    clubs = Club.objects
    return render(req, "club/log_list.html",{'club_list':clubs})

class Loglist(ListView):
    model = Log

    def get_queryset(self):
        return Log.objects.filter(result=False)


    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['club_list'] = Club.objects.all()
        return ctx

class Clubcreate(CreateView):
    model = Club
    fields = '__all__'
    def get_success_url(self):
        return reverse_lazy('log_list')