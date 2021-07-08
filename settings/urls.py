from django.urls import path

from .views import UpdateUsernameView

app_name = 'settings'

urlpatterns = [
    path('username', UpdateUsernameView.as_view(), name='username'),
]
