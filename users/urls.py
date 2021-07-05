from django.urls import path
from .views import PostedArticleListView, FavoriteListView

app_name = 'users'

urlpatterns = [
    path('<str:username>', PostedArticleListView.as_view(), name='articles'),
    path('<str:username>/favorites', FavoriteListView.as_view(), name='favorites'),
]
