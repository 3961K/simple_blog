from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView

from .forms import UpdateUsernameForm, UpdateEmailForm
from users.forms import FollowForm
from authenticate.models import Relation

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
    template_name = 'settings/relation.html'
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
