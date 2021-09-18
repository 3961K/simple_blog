from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView, CreateView, DeleteView

from .forms import UpdateUsernameForm, UpdateEmailForm, UpdatePasswordForm, \
    CreateArticleForm, UpdateArticleForm, UpdateProfileForm
from users.forms import FollowForm
from authenticate.models import Relation
from articles.models import Article

# Create your views here.

User = get_user_model()


class UpdateUsernameView(LoginRequiredMixin, UpdateView):
    template_name = 'settings/username.html'
    form_class = UpdateUsernameForm
    model = User
    success_url = reverse_lazy('settings:username')

    def get_object(self, queryset=None):
        user = self.request.user
        return User.objects.get(username=user.username)


class UpdateEmailView(LoginRequiredMixin, UpdateView):
    template_name = 'settings/email.html'
    form_class = UpdateEmailForm
    model = User
    success_url = reverse_lazy('settings:username')

    def get_object(self, queryset=None):
        user = self.request.user
        return User.objects.get(username=user.username)


class UpdateFolloweeView(LoginRequiredMixin, ListView):
    template_name = 'settings/followee.html'
    model = Relation
    paginate_by = 8

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        return self.model.objects.filter(follower=user).select_related('followee').order_by('followee__username')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 自身のユーザ名をフォームに設定
        username = self.request.user.username
        initial_form_dict = dict(follower=username)
        follow_form = FollowForm(initial=initial_form_dict)
        context['follow_form'] = follow_form

        return context


class UpdateFollowerView(LoginRequiredMixin, ListView):
    template_name = 'settings/follower.html'
    model = Relation
    paginate_by = 8

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        return self.model.objects.filter(followee=user).select_related('follower').order_by('follower__username')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 自身のユーザ名をフォームに設定
        username = self.request.user.username
        initial_form_dict = dict(follower=username)
        follow_form = FollowForm(initial=initial_form_dict)
        context['follow_form'] = follow_form

        return context


class UpdatePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'settings/password.html'
    form_class = UpdatePasswordForm
    success_url = reverse_lazy('settings:username')


class DeleteUserView(LoginRequiredMixin, DeleteView):
    template_name = 'settings/delete_user.html'
    model = User
    success_url = reverse_lazy('articles:articles')

    def get_object(self, queryset=None):
        user = self.request.user
        return User.objects.get(username=user.username)


class CreateArticleView(LoginRequiredMixin, CreateView):
    template_name = 'settings/newarticle.html'
    form_class = CreateArticleForm
    model = Article
    success_url = reverse_lazy('settings:username')

    def form_valid(self, form):
        article = form.save(commit=False)
        article.author = self.request.user
        article.save()
        form.save_m2m()
        return HttpResponseRedirect(self.success_url)


class PostedArticleListView(LoginRequiredMixin, ListView):
    template_name = 'settings/articles.html'
    model = Article
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.filter(author=self.request.user)


class OnlyAuthorMixin(UserPassesTestMixin):
    """
    記事の編集ページを作者のみがアクセスするためのMixin
    """

    def test_func(self):
        user = self.request.user

        article = get_object_or_404(Article.objects.filter(pk=self.kwargs['pk']).select_related('author'),
                                    pk=self.kwargs['pk'])
        if article.author == user:
            return True

        return False


class UpdateArticleView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Article
    form_class = UpdateArticleForm
    template_name = 'settings/update_article.html'
    success_url = reverse_lazy('settings:postedarticles')


class DeleteArticleView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    model = Article
    template_name = 'base/blank.html'
    success_url = reverse_lazy('settings:postedarticles')

    def get(self, request, *args, **kwargs):
        # GETリクエストによってアクセスされた場合は投稿された記事一覧ページへリダイレクト
        return redirect('settings:postedarticles')


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'settings/profile.html'
    form_class = UpdateProfileForm
    model = User
    success_url = reverse_lazy('settings:profile')

    def dispatch(self, *args, **kwargs):
        return super(UpdateProfileView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UpdateProfileView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_object(self, queryset=None):
        return User.objects.get(username=self.request.user)
