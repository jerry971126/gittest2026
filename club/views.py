from django import forms
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import ListView, RedirectView, CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from .models import User, Club, Apply, Log

# Create your views here.

ROLE_NAMES = {
    0: '學生',
    1: '社長',
    2: '指導老師',
    3: '訓育組',
}


def get_current_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None


class LoginRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not get_current_user(request):
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class RoleRequiredMixin(LoginRequiredMixin):
    allowed_roles = None

    def dispatch(self, request, *args, **kwargs):
        current_user = get_current_user(request)
        if current_user is None:
            return redirect('login')
        if self.allowed_roles is not None and current_user.us_rank not in self.allowed_roles:
            return redirect('no_permission')
        return super().dispatch(request, *args, **kwargs)


class LoginForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='選擇使用者',
        empty_label='請選擇使用者',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            request.session['user_id'] = form.cleaned_data['user'].pk
            return redirect('log_list')
    else:
        form = LoginForm()
    return render(request, 'club/login.html', {'form': form})


def logout_view(request):
    request.session.pop('user_id', None)
    return redirect('login')


def no_permission(request):
    return render(request, 'club/forbidden.html', status=403)


class Loglist(RoleRequiredMixin, ListView):
    model = Log
    allowed_roles = [0, 1, 2, 3]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['club_list'] = Club.objects.all()
        return ctx


class Clubcreate(RoleRequiredMixin, CreateView):
    model = Club
    fields = '__all__'
    allowed_roles = [3]

    def get_success_url(self):
        return reverse_lazy('log_list')


class Applylist(RoleRequiredMixin, ListView):
    model = Apply
    context_object_name = 'apply_list'
    allowed_roles = [0, 1, 2, 3]

    def get_queryset(self):
        current_user = get_current_user(self.request)
        if current_user is None:
            return Apply.objects.none()
        if current_user.us_rank == 0:
            return Apply.objects.filter(user=current_user)
        if current_user.us_rank in (1, 2):
            return Apply.objects.filter(
                Q(club=current_user.club) | Q(user__club=current_user.club)
            )
        return Apply.objects.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['user_list'] = User.objects.all()
        ctx['club_list'] = Club.objects.all()
        ctx['log_list_check'] = Log.objects.filter(state=1)
        ctx['log_list_pass'] = Log.objects.filter(state=2)
        ctx['log_list_fail'] = Log.objects.filter(state=0)
        return ctx


class Usercreate(RoleRequiredMixin, CreateView):
    model = User
    fields = '__all__'
    allowed_roles = [3]

    def get_success_url(self):
        return reverse_lazy('log_list')


class Applycreate(RoleRequiredMixin, CreateView):
    model = Apply
    fields = '__all__'
    allowed_roles = [0]

    def get_success_url(self):
        return reverse_lazy('log_list')


class Clublist(RoleRequiredMixin, ListView):
    model = Club
    allowed_roles = [0, 1, 2, 3]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['club_list'] = list(Club.objects.all())
        for club in ctx['club_list']:
            chief = club.user_set.filter(us_rank=1)[:1]
            club.chief = chief[0].us_name if chief else ""
        return ctx


class Applyview(RoleRequiredMixin, DetailView):
    model = Apply
    allowed_roles = [0, 1, 2, 3]

    def dispatch(self, request, *args, **kwargs):
        current_user = get_current_user(request)
        apply_obj = self.get_object()
        if current_user.us_rank == 0 and apply_obj.user != current_user:
            return redirect('no_permission')
        if current_user.us_rank in (1, 2):
            if apply_obj.club != current_user.club and apply_obj.user.club != current_user.club:
                return redirect('no_permission')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['logs'] = Log.objects.filter(apply=self.get_object()).order_by('-date')
        return ctx


class ApplyUpdate(RoleRequiredMixin, UpdateView):
    model = Apply
    allowed_roles = [1, 2, 3]

    def form_valid(self, form):
        if self.object.sstu_pass and self.object.sch_pass:
            if self.object.club_after:
                self.object.user.club = self.object.club_after
                self.object.user.save()
        return form


def _create_log(apply_obj, user_obj, club_obj, result=True, state=2):
    # helper to record a log entry
    try:
        Log.objects.create(apply=apply_obj, user=user_obj, club=club_obj, result=result, state=state)
    except Exception:
        pass


def approve_sstu(request, pk):
    current_user = get_current_user(request)
    if current_user is None:
        return redirect('login')

    try:
        apply_obj = Apply.objects.get(pk=pk)
    except Apply.DoesNotExist:
        return redirect('apply_list')

    # only 社長 of the applicant's current club can approve sstu
    if current_user.us_rank != 1 or current_user.club != apply_obj.user.club:
        return redirect('no_permission')

    if request.method == 'POST':
        apply_obj.sstu_pass = True
        apply_obj.save()
        _create_log(apply_obj, current_user, current_user.club, result=True, state=2)
    return redirect('apply_detail', pk=pk)


def approve_sch(request, pk):
    current_user = get_current_user(request)
    if current_user is None:
        return redirect('login')

    try:
        apply_obj = Apply.objects.get(pk=pk)
    except Apply.DoesNotExist:
        return redirect('apply_list')

    # only 指導老師 of the target club can approve school-level (sch_pass)
    if current_user.us_rank != 2 or current_user.club != apply_obj.club:
        return redirect('no_permission')

    if request.method == 'POST':
        apply_obj.sch_pass = True
        apply_obj.save()
        _create_log(apply_obj, current_user, current_user.club, result=True, state=2)
    return redirect('apply_detail', pk=pk)