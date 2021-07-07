from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseBadRequest
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, FormView


from .forms import FollowForm
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
            context['profile_user'] = User.objects.get(username=self.kwargs['username'])
        except ObjectDoesNotExist:
            raise Http404("そのユーザは存在しません")

        if not self.request.user.is_authenticated:
            return context

        # 認証ユーザの場合はFavoriteArticleFormに現在のユーザ名を設定
        username = self.request.user.username
        initial_form_dict = dict(follower=username)
        follow_form = FollowForm(initial=initial_form_dict)
        context['follow_form'] = follow_form

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

        return self.model.objects.filter(favorite_users=user).select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['profile_user'] = User.objects.get(username=self.kwargs['username'])
        except ObjectDoesNotExist:
            raise Http404("そのユーザは存在しません")

        if not self.request.user.is_authenticated:
            return context

        # 認証ユーザの場合はFavoriteArticleFormに現在のユーザ名を設定
        username = self.request.user.username
        initial_form_dict = dict(follower=username)
        follow_form = FollowForm(initial=initial_form_dict)
        context['follow_form'] = follow_form

        return context


class FolloweeListView(ListView):
    template_name = 'users/followees.html'
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
            context['profile_user'] = User.objects.get(username=self.kwargs['username'])
        except ObjectDoesNotExist:
            raise Http404("そのユーザは存在しません")

        if not self.request.user.is_authenticated:
            return context

        # 認証ユーザの場合はFavoriteArticleFormに現在のユーザ名を設定
        username = self.request.user.username
        initial_form_dict = dict(follower=username)
        follow_form = FollowForm(initial=initial_form_dict)
        context['follow_form'] = follow_form

        return context


class FollowerListView(ListView):
    template_name = 'users/followers.html'
    model = Relation
    paginate_by = 8

    def get_queryset(self, *args, **kwargs):
        try:
            user = User.objects.get(username=self.kwargs['username'])
        except ObjectDoesNotExist:
            raise Http404("そのユーザは存在しません")

        return self.model.objects.filter(followee=user).select_related('follower').order_by('follower__username')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['profile_user'] = User.objects.get(username=self.kwargs['username'])
        except ObjectDoesNotExist:
            raise Http404("そのユーザは存在しません")

        # 認証ユーザの場合はFavoriteArticleFormに現在のユーザ名を設定
        username = self.request.user.username
        initial_form_dict = dict(follower=username)
        follow_form = FollowForm(initial=initial_form_dict)
        context['follow_form'] = follow_form

        return context


class FollowView(LoginRequiredMixin, FormView):
    form_class = FollowForm
    template_name = 'users/blank.html'

    def get(self, request, *args, **kwargs):
        username = self.kwargs['username']
        return redirect('users:articles', username=username)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # Ajaxリクエストでない場合はBadRequestを返す
        if not self.request.is_ajax:
            raise HttpResponseBadRequest()

        # 送信されてきたユーザ名を取得し,送信してきたユーザと同じであるか確認する
        follower_name = form.cleaned_data['follower']
        follower = User.objects.get(username=follower_name)
        if self.request.user != follower:
            raise HttpResponseBadRequest()

        # フォロー・アンフォロー対象のユーザ名を取得
        followee_name = self.kwargs['username']
        followee = get_object_or_404(User, username=followee_name)

        # followerとfolloweeによるRelationオブジェクトが既に存在する場合(フォロー中)は
        # 削除(フォロー解除)し,存在しない場合は作成する(フォローする)
        status = ''
        if Relation.objects.filter(follower=follower, followee=followee).exists():
            relation = Relation.objects.filter(follower=follower, followee=followee).get()
            relation.delete()
            status = 'notfollow'
        else:
            relation = Relation(follower=follower, followee=followee)
            relation.save()
            status = 'follow'

        json_response = {
            'data': {
                'status': status
            }
        }

        return JsonResponse(json_response)

    def form_invalid(self, form):
        # 正しく無いデータが送信されてきた場合は500を返す
        return JsonResponse({}, status=500)
