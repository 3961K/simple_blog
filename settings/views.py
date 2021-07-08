from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView

from .forms import UpdateUsernameForm

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
