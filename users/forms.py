from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class FollowForm(forms.Form):
    follower = forms.CharField(max_length=30, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['follower'].widget = forms.HiddenInput()

    def clean_follower(self):
        follower = self.cleaned_data['follower']

        # ユーザ名に一致するユーザが存在しない場合はバリデーションエラーを発生させる
        if not User.objects.filter(username=follower).exists():
            raise forms.ValidationError("user is not exist")

        return follower
