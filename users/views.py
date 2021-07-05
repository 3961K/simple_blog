from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import Http404
from django.views.generic import ListView

from articles.models import Article
from authenticate.models import Relation

# Create your views here.

User = get_user_model()


class PostedArticleListView(ListView):
    template_name = 'users/articles.html'
    model = Article
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        try:
            author = User.objects.get(username=self.kwargs['username'])
        except ObjectDoesNotExist:
            raise Http404("そのユーザは存在しません")
        return self.model.objects.filter(author=author)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['user'] = User.objects.get(username=self.kwargs['username'])
        except ObjectDoesNotExist:
            raise Http404("そのユーザは存在しません")

        return context


class FavoriteListView(ListView):
    template_name = 'users/favorites.html'
    model = Article
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        try:
            user = User.objects.get(username=self.kwargs['username'])
        except ObjectDoesNotExist:
            raise Http404("そのユーザは存在しません")

        return self.model.objects.filter(favorite_users=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['user'] = User.objects.get(username=self.kwargs['username'])
        except ObjectDoesNotExist:
            raise Http404("そのユーザは存在しません")

        return context


class FolloweeListView(ListView):
    template_name = 'users/relations.html'
    model = Relation
    paginate_by = 8

    def get_queryset(self, *args, **kwargs):
        try:
            user = User.objects.get(username=self.kwargs['username'])
        except ObjectDoesNotExist:
            raise Http404("そのユーザは存在しません")

        return self.model.objects.filter(follower=user).select_related('followee').order_by('followee__username')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['user'] = User.objects.get(username=self.kwargs['username'])
        except ObjectDoesNotExist:
            raise Http404("そのユーザは存在しません")

        return context
