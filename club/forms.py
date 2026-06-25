from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="電子信箱")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'club','us_rank']
    # 🌟 核心：傳入目前操作的 user 來決定表單長怎樣
    def __init__(self, *args, **kwargs):
        # 從 kwargs 中把當前登入的管理者 user 抽出來
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

        # 如果目前沒有人登入（代表是前台公開註冊），或是登入的人等級是 3、4 級（下層階級）
        if current_user is None or current_user.us_rank in [User.Rank.lv3, User.Rank.lv4]:
            # 1. 隱藏等級與社團欄位（不讓一般學生或社長自己調整）
            if 'us_rank' in self.fields:
                self.fields['us_rank'].widget = forms.HiddenInput()
                self.fields['us_rank'].initial = User.Rank.lv4 # 預設強制為 4級學生
            # if 'club' in self.fields:
            #     self.fields['club'].widget = forms.HiddenInput()
            #     self.fields['club'].required = False