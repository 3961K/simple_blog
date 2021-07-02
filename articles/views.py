from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import FormView

from .forms import FavoriteArticleForm
from .models import Article

# Create your views here.

User = get_user_model()


class FavoriteArticleView(LoginRequiredMixin, FormView):
    form_class = FavoriteArticleForm
    template_name = 'articles/blank.html'

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
        username = form.cleaned_data['username']
        user = User.objects.get(username=username)
        if self.request.user != user:
            raise HttpResponseBadRequest()

        # 更新対象のArticleオブジェクトを取得
        article_id = self.kwargs['pk']
        article = get_object_or_404(Article, pk=article_id)

        # お気に入りユーザとして登録していない場合は追加を行い,
        # 既にお気に入りユーザとして登録している場合は削除を行い,状態を保存して更新する
        if article.favorite_users.filter(username=username).exists():
            article.favorite_users.remove(user)
            status = 'notfavorited'
        else:
            article.favorite_users.add(user)
            status = 'favorited'
        article.save()

        # 処理の結果を格納するJSONオブジェクトを返す
        json_response = {
            'data': {
                'status': status
            }
        }
        return JsonResponse(json_response)

    def form_invalid(self, form):
        # 正しく無いデータが送信されてきた場合は500を返す
        return JsonResponse({}, status=500)
