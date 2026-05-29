from django.shortcuts import render
from .models import User, Club, Apply, Log
from django.views.generic import ListView, RedirectView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .forms import UserRegisterForm
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
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
        ctx['user_list'] = User.objects.all()
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

class Applycreate(CreateView ,UserPassesTestMixin  ,LoginRequiredMixin):
    model = Apply
    fields = ['club_after']

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.us_rank in [User.Rank.lv3, User.Rank.lv4]
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("權限不符：1級與2級人員主要負責審核，不可填寫轉社申請。")
        return super().handle_no_permission()
    

    def form_valid(self, form):
        now_user = self.request.user
        form.instance.user = now_user
        form.instance.club = now_user.club
        
        # 1. 先執行 Django 預設儲存，讓資料存入資料庫
        response = super().form_valid(form)
        apply_obj = self.object  # 剛建立成功的轉社單物件
        
        old_club = apply_obj.club        # 學生原本的社團
        new_club = apply_obj.club_after  # 學生想轉入的新社團

        # =========================================================
        # 📨 修正後的 Email 通知鏈（移除不存在的 .chairman，改用反查）
        # =========================================================

        # 🛑 信件 1：通知「原社團社長 (3級)」進行一階段審核
        if old_club:
            # 🌟 修正點：利用 user_set 撈出原社團內等級為 3 的社長
            old_chairman = old_club.user_set.filter(us_rank=3).first()
            if old_chairman and old_chairman.email:
                send_mail(
                    subject=f"【轉社待辦審核】您的社員 {now_user.username} 提出了轉社申請",
                    message=f"{old_chairman.username} 社長您好：\n\n您的社員 {now_user.username} 已在系統上提交轉社申請（預計轉出至【{new_club.club_name}】）。\n請盡速至系統查看並完成『第一階段：原社團同意』的簽核。",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[old_chairman.email],
                    fail_silently=True,
                )

        # 🛑 信件 2：通知「新社團社長 (3級)」有新社員想轉入
        if new_club:
            # 🌟 修正點：利用 user_set 撈出新社團內等級為 3 的社長
            new_chairman = new_club.user_set.filter(us_rank=3).first()
            if new_chairman and new_chairman.email:
                send_mail(
                    subject=f"【轉社通知】有新同學申請轉入您的社團【{new_club.club_name}】",
                    message=f"{new_chairman.username} 社長您好：\n\n學生 {now_user.username} 剛剛提出了轉入您的社團【{new_club.club_name}】的申請。\n目前該單據已送交原社團社長進行一階段審核，待其同意後，系統將移交給您進行二階段簽核。",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[new_chairman.email],
                    fail_silently=True,
                )

        # 🛑 信件 3：通知「校務/行政管理人員 (2級)」系統有新案件
        lv2_users = User.objects.filter(us_rank=User.Rank.lv2)
        lv2_emails = [u.email for u in lv2_users if u.email]
        
        if lv2_emails:
            send_mail(
                subject=f"【轉社系統通知】學生 {now_user.username} 提交了轉社申請單",
                message=f"2級校務管理人員您好：\n\n系統收到一筆新的轉社申請。\n申請學生：{now_user.username}\n變更內容：【{old_club.club_name if old_club else '無'}】 ➔ 【{new_club.club_name}】\n目前已啟動三方線上審核流程，特此通知。",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=lv2_emails,
                fail_silently=True,
            )

        return response
        
        # return super().form_valid(form)

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

    #   核心修正：覆寫 get_form，這才是真正動態控制網頁表單欄位的「萬靈丹」
    def get_form(self, form_class=None):
        # 先拿到預設包含 3 個欄位的原始表單
        form = super().get_form(form_class)
        user = self.request.user
        apply_obj = self.get_object()

        # 🌟 情況 A1：1級管理員 -> 擁有最高權限，3種check都可以調整，所以不拔除任何欄位
        if user.us_rank == User.Rank.lv1:
            pass  # 什麼都不做，保留原本 fields 宣告的 3 個欄位

        # 🌟 情況 A2：如果是 2 級校方人員 -> 他們只能改學校同意
        elif user.us_rank == User.Rank.lv2:
            # 把不屬於他們的欄位從表單中完全拔除
            form.fields.pop('sstu1_pass', None)
            form.fields.pop('sstu2_pass', None)

        # 情況 B：如果是 3 級社長（維持原來的嚴格分權邏輯）
        elif user.us_rank == User.Rank.lv3:
            # 檢查 1：如果他同時是原社長也是新社長（特殊極端狀況），或者只是原社長
            if user.club == apply_obj.club and user.club != apply_obj.club_after:
                form.fields.pop('sstu2_pass', None)
                form.fields.pop('sch_pass', None)
            # 檢查 2：如果他是新社團的社長
            elif user.club == apply_obj.club_after and user.club != apply_obj.club:
                form.fields.pop('sstu1_pass', None)
                form.fields.pop('sch_pass', None)
            # 檢查 3：如果他是原社長，同時也是新社長
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


            #寄送email給通過的使用者
            send_mail(
                subject="【轉社成功通知】您的轉社申請已審核通過！",
                message=f"{student.username} 同學你好：恭喜你！你的轉社申請已全數審核通過。你目前所屬社團已正式變更為【{new_club.club_name}】。",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=True,
            )
            messages.success(self.request, "審核成功，已完成自動轉社並通知學生！")

        return response

    def get_success_url(self):
        # 審核成功後導回該申請單詳細頁
        return reverse_lazy('apply_detail', kwargs={'pk': self.object.pk})


class ApplyDelete(LoginRequiredMixin,  UserPassesTestMixin, DeleteView):
    model= Apply
    def test_func(self):
        user = self.request.user
        
        # 只有登入者的身分等級 (us_rank) 為 1 (User.Rank.lv1) 時才回傳 True
        if user.is_authenticated and user.us_rank == User.Rank.lv1:
            return True
            
        return False
    success_url = reverse_lazy('success')

class UserRegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'registration/register.html'
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user if self.request.user.is_authenticated else None
        return kwargs
    success_url = reverse_lazy('success')


def success_msg(req):
    return render(req, "club/success.html",{'msg':'成功'})


class ClubUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Club
    template_name = "club/club_up_form.html"
    fields = ['club_name', 'max_people_num']
    def test_func(self):     
        user= self.request.user
        if user.is_authenticated and user.us_rank in [User.Rank.lv1, User.Rank.lv2]:
            return True
        return False
    
    def handle_no_permission(self):
        if  self.request.user.is_authenticated:
            raise  PermissionDenied("權限不足(僅1、2級人員得以修改)，無法修改")
        return super().handle_no_permission()

    success_url = reverse_lazy('success')

class ClubDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Club
    def test_func(self):
        user = self.request.user
        if user.is_authenticated and user.us_rank == User.Rank.lv1:
            return True     
        return False
    success_url = reverse_lazy('success')

class UserRankUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):  #前端使用者權限曾級管理
    model = User
    template_name = "club/user_rank_up.html"
    fields = ['us_rank', 'club']

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.us_rank in [User.Rank.lv1, User.Rank.lv2]

    # 🌟 2. 動態控制表單選項：根據登入者等級，限制他「能把對方升到哪一級」
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        current_user = self.request.user        # 目前在操作的管理員
        target_user = self.get_object()         # 被修改權限的目標使用者

        # 🚨 安全防呆：如果企圖修改同階級或更高階級的人，直接噴 403 拒絕
        if current_user.us_rank >= target_user.us_rank and current_user.us_rank != User.Rank.lv1:
            raise PermissionDenied("權限不足：您只能修改權限層級比您低的使用者！")

        # 調整下拉選單的選項 (Choices)
        if current_user.us_rank == User.Rank.lv2:
            # 2 級校方人員：只能把人設定為 3 級(社長) 或 4 級(學生)，不能指派 1、2 級
            form.fields['us_rank'].choices = [
                (User.Rank.lv3, "3級 - 社長"),
                (User.Rank.lv4, "4級 - 一般學生"),
            ]
        # 1 級管理員：可以看到並指派所有等級（1, 2, 3, 4），不需限制

        return form

    # 🌟 3. 儲存時的最後防線驗證
    def form_valid(self, form):
        current_user = self.request.user
        new_rank = form.cleaned_data.get('us_rank')

        # 2 級人員的防禦：不能偷偷把人升到 1 或 2 級
        if current_user.us_rank == User.Rank.lv2 and new_rank in [User.Rank.lv1, User.Rank.lv2]:
            raise PermissionDenied("違法操作：2級人員無法將使用者提升至 1 或 2 級！")

        return super().form_valid(form)

    # 拒絕存取時的漂亮提示
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("權限不足：只有 1 級管理員或 2 級校方人員可以調整使用者權限。")
        return super().handle_no_permission()