from django.urls import path

from .views import UpdateUsernameView, UpdateEmailView, UpdateFolloweeView, \
    UpdateFollowerView, UpdatePasswordView, CreateArticleView, \
    PostedArticleListView, UpdateArticleView, UpdateProfileView, \
    DeleteUserView

app_name = 'settings'

urlpatterns = [
    path('username', UpdateUsernameView.as_view(), name='username'),
    path('email', UpdateEmailView.as_view(), name='email'),
    path('followees', UpdateFolloweeView.as_view(), name='followees'),
    path('followers', UpdateFollowerView.as_view(), name='followers'),
    path('password', UpdatePasswordView.as_view(), name='password'),
    path('profile', UpdateProfileView.as_view(), name='profile'),
    path('newarticle', CreateArticleView.as_view(), name='newarticle'),
    path('postedarticles', PostedArticleListView.as_view(), name='postedarticles'),
    path('postedarticles/<int:pk>', UpdateArticleView.as_view(), name='updatearticle'),
    path('delete-user/', DeleteUserView.as_view(), name='delete_user')
]
