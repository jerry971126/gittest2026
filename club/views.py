from django.shortcuts import render
from .models import User, Club, Apply, Log
from django.views.generic import ListView, RedirectView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import UserRegisterForm
# Create your views here.

# def club_list(req):
#     clubs = Log.objects.select_related('club__club_name').all() #?不知是否可行
#     return render(req, "club/log_list.html",{'club_list':clubs})

class Loglist(ListView):
    model = Log
    
    def get_context_data(self, **kwargs):
        ctx =  super().get_context_data(**kwargs)
        ctx['club_list'] = Club.objects.all()
        now_user = self.request.user
        ctx['user_li'] = now_user
        return ctx

class Clubcreate(CreateView, LoginRequiredMixin):
    model = Club
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('success')
    
class Applylist(ListView):
    model = Apply

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['user_list'] = User.objects.all()
        ctx['club_list'] = Club.objects.all()
        ctx['log_list_check'] = Log.objects.filter(state = 1)  #不通過
        ctx['log_list_pass'] = Log.objects.filter(state = 2)   #通過
        ctx['log_list_fail'] = Log.objects.filter(state = 0)   #審核中
        return ctx

# class Usercreate(CreateView):
#     model = User
#     fields = '__all__'

#     def get_success_url(self):
#         return reverse_lazy('log_list')

class Applycreate(CreateView, LoginRequiredMixin):
    model = Apply
    fields = ['club_after']

    def form_valid(self, form):
        
        now_user = self.request.user
        form.instance.user = now_user
        form.instance.club = now_user.club

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('success')
    
class Clublist(ListView):
    model = Club
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['club_list'] = list(Club.objects.all())
        for club in ctx['club_list']:
            chief = club.user_set.filter(us_rank = 3)[:1]
            club.chief = chief[0].username if chief else ""
        #申請轉設中的人數        
        return ctx
    
class Applyview(DetailView):
    model = Apply


class ApplyUpdate(UpdateView, LoginRequiredMixin):
    model = Apply

    def form_valid(self, form):
        if self.object.sstu_pass and self.object.sch_pass:
            self.object.user.club = self.object.new_club
            self.object.user.save()            
        return form
    

class UserRegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('success')

def success_msg(req):
    return render(req, "club/success.html",{'msg':'成功'})