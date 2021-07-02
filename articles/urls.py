from django.urls import path

from .views import FavoriteArticleView

app_name = 'articles'

urlpatterns = [
    path('<int:pk>/favorite', FavoriteArticleView.as_view(), name='favorite'),
]
