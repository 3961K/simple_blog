from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class FavoriteArticleForm(forms.Form):
    """
    記事をお気にいりに登録する際にユーザ名を送信するためのフォーム

    Parameters
    ----------
    username : str
        ユーザ名を表す文字列
    """
    username = forms.CharField(max_length=30, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget = forms.HiddenInput()

    def clean_username(self):
        username = self.cleaned_data['username']

        # ユーザ名に一致するユーザが存在しない場合はバリデーションエラーを発生させる
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("user is not exist")

        return username
