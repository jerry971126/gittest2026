from django.shortcuts import render
from .models import User, Club, Apply, Log
from django.views.generic import ListView, RedirectView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .forms import UserRegisterForm
from django.core.exceptions import PermissionDenied
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
    context_object_name = 'apply'             # 在 HTML 中使用 {{ apply }} 來稱呼這筆資料

    def get_queryset(self):
        return super().get_queryset().select_related('user', 'club', 'club_after')


class ApplyUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):  #用來判斷審核是否通過
    model = Apply
    template_name= 'club/apply_up_form.html'
# 1. 這裡宣告要處理的所有可能欄位，滿足 Django 的基本初始化檢查
    fields = ['sstu1_pass', 'sstu2_pass', 'sch_pass'] 

    # 安全權限防護（維持不變）
    def test_func(self):
        user = self.request.user
        apply_obj = self.get_object()
        if user.us_rank in [User.Rank.lv1, User.Rank.lv2]:
            return True
        if user.us_rank == User.Rank.lv3:
            if user.club == apply_obj.club or user.club == apply_obj.club_after:
                return True
        return False

    # 🌟 核心修正：覆寫 get_form，這才是真正動態控制網頁表單欄位的「萬靈丹」
    def get_form(self, form_class=None):
        # 先拿到預設包含 3 個欄位的原始表單
        form = super().get_form(form_class)
        user = self.request.user
        apply_obj = self.get_object()

        # 情況 A：如果是 1 級管理員或 2 級校方人員 -> 他們只能改學校同意
        if user.us_rank in [User.Rank.lv1, User.Rank.lv2]:
            # 把不屬於他們的欄位從表單中完全拔除
            form.fields.pop('sstu1_pass', None)
            form.fields.pop('sstu2_pass', None)

        # 情況 B：如果是 3 級社長
        elif user.us_rank == User.Rank.lv3:
            # 檢查 1：如果他同時是原社長也是新社長（特殊極端狀況），或者只是原社長
            if user.club == apply_obj.club and user.club != apply_obj.club_after:
                form.fields.pop('sstu2_pass', None)
                form.fields.pop('sch_pass', None)
            # 檢查 2：如果他是新社團的社長
            elif user.club == apply_obj.club_after and user.club != apply_obj.club:
                form.fields.pop('sstu1_pass', None)
                form.fields.pop('sch_pass', None)
            # 檢查 3：如果他是原社長，同時也是新社長（比如學生申請轉入同一個社團被防呆擋下前的極端狀況）
            elif user.club == apply_obj.club and user.club == apply_obj.club_after:
                form.fields.pop('sch_pass', None)
            else:
                # 保險防呆：如果這社長不屬於這兩個社團，什麼欄位都不給他
                form.fields.clear()

        return form

    # 資料儲存後的邏輯更新
    def form_valid(self, form):
        response = super().form_valid(form)
        apply_obj = self.object

        # 人數控管與自動轉社邏輯（維持你之前的寫法）
        if apply_obj.sstu1_pass and apply_obj.sstu2_pass and apply_obj.sch_pass:
            student = apply_obj.user
            old_club = apply_obj.club
            new_club = apply_obj.club_after

            if new_club.now_people_num >= new_club.max_people_num:
                raise PermissionDenied("新社團名額已滿，無法完成轉社程序！")

            student.club = new_club
            student.save()

            if old_club.now_people_num > 0:
                old_club.now_people_num -= 1
                old_club.save()

            new_club.now_people_num += 1
            new_club.save()

        return response

    def get_success_url(self):
        # 審核成功後導回該申請單詳細頁
        return reverse_lazy('apply_detail', kwargs={'pk': self.object.pk})


class ApplyDelete(DeleteView):
    model= Apply
    success_url = reverse_lazy('success')

class UserRegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('success')


def success_msg(req):
    return render(req, "club/success.html",{'msg':'成功'})


class ClubUpdate(UpdateView):
    pass