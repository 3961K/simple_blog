from django.urls import path
from .views import PostedArticleListView, FavoriteListView, FolloweeListView

app_name = 'users'

urlpatterns = [
    path('<str:username>', PostedArticleListView.as_view(), name='articles'),
    path('<str:username>/favorites', FavoriteListView.as_view(), name='favorites'),
    path('<str:username>/followees', FolloweeListView.as_view(), name='followees'),
]
