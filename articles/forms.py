from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Tag

User = get_user_model()


class SearchArticleForm(forms.Form):
    keyword = forms.CharField(max_length=100, required=False)

    all_article_tag = Tag.objects.order_by('pk').all()
    TAG_CHOICES = [(article_tag.pk, article_tag.tag)
                   for article_tag in all_article_tag]
    TAG_CHOICES.insert(0, ('all', '全てのタグ'))
    tag = forms.ChoiceField(choices=TAG_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class PostCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5, 'cols': 30}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'mt-2 mb-3 font-weight-normal'


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
