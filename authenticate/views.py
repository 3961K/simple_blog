from django.contrib.auth.views import LoginView, LogoutView

from .forms import LoginForm

# Create your views here.


class LoginView(LoginView):
    template_name = 'authenticate/login.html'
    form_class = LoginForm


class LogoutView(LogoutView):
    template_name = ''
