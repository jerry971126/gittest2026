from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="電子信箱")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'club','us_rank']