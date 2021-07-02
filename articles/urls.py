from django.urls import path

from .views import ArticleView, FavoriteArticleView, PostCommentView

app_name = 'articles'

urlpatterns = [
    path('<int:pk>', ArticleView.as_view(), name='article'),
    path('<int:pk>/comments', PostCommentView.as_view(), name='comments'),
    path('<int:pk>/favorite', FavoriteArticleView.as_view(), name='favorite'),
]
