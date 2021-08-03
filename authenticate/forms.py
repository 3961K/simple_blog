from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

    def clean(self):
        cleaned_data = super().clean()

        # superuser権限もしくはstaff権限を持つユーザアカウントのログインは禁止する
        username = self.cleaned_data.get('username')
        user = User.objects.get(username=username)
        if user.is_superuser:
            raise self.get_invalid_login_error()

        return cleaned_data


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'mt-2 mb-3 font-weight-normal'
