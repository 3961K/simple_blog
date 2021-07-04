from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import LoginForm, RegisterForm

# Create your views here.


class LoginView(LoginView):
    template_name = 'authenticate/login.html'
    form_class = LoginForm


class LogoutView(LogoutView):
    template_name = ''


class RegisterView(CreateView):
    template_name = 'authenticate/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('articles:articles')

    def form_valid(self, form):
        user = form.save()
        login(self.request,
              user,
              backend='django.contrib.auth.backends.ModelBackend')
        self.object = user
        return HttpResponseRedirect(self.get_success_url())
