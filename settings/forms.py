from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from articles.models import Article, Tag

User = get_user_model()


class UpdateUsernameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UpdateEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class UpdatePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class CreateArticleForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(),
                                          widget=forms.CheckboxSelectMultiple,
                                          required=True)

    class Meta:
        model = Article
        fields = ['title', 'content', 'tags']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'mt-2 mb-3 font-weight-normal'


class UpdateArticleForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(),
                                          widget=forms.CheckboxSelectMultiple,
                                          required=True)

    class Meta:
        model = Article
        fields = ['title', 'content', 'tags']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'mt-2 mb-3 font-weight-normal'


class UpdateProfileForm(forms.ModelForm):
    # [エラー] 画像ファイルをアップロードしなかった場合,'ImageFieldFile' object has no attribute 'image'が発生してしまう
    # iconが指定されなかった場合は現在のファイル名が指定されるためである
    icon = forms.ImageField(label=_('Icon'),
                            required=False,
                            error_messages={'invalid': _('画像ファイルをアップロードしてください')},
                            widget=forms.FileInput)

    class Meta:
        model = User
        fields = ['icon', 'profile_message']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(self.fields.keys())
        self.fields['icon'].widget.attrs['class'] = 'mt-2 mb-3 font-weight-normal'
        self.fields['profile_message'].widget.attrs['class'] = 'form-control'
        # ログインユーザを取得する
        self.user = user

    def clean_icon(self):
        cleaned_icon = self.cleaned_data['icon']

        if not cleaned_icon:
            raise ValidationError('画像ファイルをアップロードしてください')

        try:
            if cleaned_icon.image.width > 1024 or cleaned_icon.image.height > 1024:
                raise ValidationError('縦幅・横幅が1024pxより大きい画像はアップロードする事が出来ません')
        except AttributeError:
            # ログインユーザの現在のアイコンと異なるファイルにも関わらず画像データが無い場合はエラーとする
            if self.user.icon != cleaned_icon:
                raise ValidationError('画像ファイルをアップロードしてください')

        return cleaned_icon
