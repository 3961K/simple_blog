from django.urls import path
from .views import PostedArticleListView

app_name = 'users'

urlpatterns = [
    path('<str:username>', PostedArticleListView.as_view(), name='articles'),
]
