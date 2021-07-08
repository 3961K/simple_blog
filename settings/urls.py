from django.urls import path

from .views import UpdateUsernameView, UpdateEmailView

app_name = 'settings'

urlpatterns = [
    path('username', UpdateUsernameView.as_view(), name='username'),
    path('email', UpdateEmailView.as_view(), name='email'),
]
