from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import Http404, HttpResponseBadRequest
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView, CreateView, DetailView, ListView
from django.shortcuts import render


from .forms import FavoriteArticleForm, PostCommentForm, SearchArticleForm
from .models import Article, Tag

# Create your views here.

User = get_user_model()


class ArticleListView(ListView):
    template_name = 'articles/articles.html'
    model = Article
    paginate_by = 5

    def fetch_get_parameter(self, parameter_name):
        if type(parameter_name) is not str or parameter_name == "":
            raise KeyError("request url is not include {}".format(parameter_name))

        if parameter_name not in self.request.GET:
            raise KeyError("request url is not include {}".format(parameter_name))

        return self.request.GET.get(parameter_name)

    def get_queryset(self):
        queryset = super().get_queryset()

        # キーワードをURLパラメータから抽出
        try:
            keyword = self.fetch_get_parameter("keyword")
            queryset = queryset.filter(Q(title__contains=keyword)
                                       | Q(content__contains=keyword))
        except KeyError:
            pass

        # tagをURLパラメータから抽出
        try:
            tag_pk = self.fetch_get_parameter("tag")
        except KeyError:
            # タグが存在しない場合は現時点での条件のクエリセットを返す
            return queryset

        # tagがallである場合は現時点でのクエリセットを返す
        if tag_pk == 'all':
            return queryset

        # タグオブジェクトを取得する
        # 存在しないタグの場合は,存在しないタグのpkを指定したクエリセットを返す
        try:
            tag = Tag.objects.get(pk__in=tag_pk)
        except ValueError:
            queryset = queryset.filter(tags=-1)
            return queryset
        except ObjectDoesNotExist:
            queryset = queryset.filter(tags=-1)
            return queryset

        queryset = queryset.filter(tags=tag)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 記事一覧を取得する,検索結果が何も無い場合は 404 を返す
        article_list = context['article_list']
        if article_list.first() is None:
            raise Http404('指定したキーワードとタグを含む記事は存在しませんでした')

        context['form'] = SearchArticleForm
        return context


class ArticleView(DetailView):
    template_name = 'articles/article.html'
    model = Article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['comment_form'] = PostCommentForm

        context['favorite_form'] = FavoriteArticleForm
        # 既にお気に入り登録しているか否かでボタンに表示する値ととお気に入りフォームのvalue
        # に設定される状態を示す文字列を決定する
        context['favorite_button_value'] = '★' \
            if self.object.is_favorited(self.request.user) else '☆'
        context['favorite_status'] = 'favorited' \
            if self.object.is_favorited(self.request.user) else 'notfavorited'

        return context

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return super().get(request, *args, **kwargs)

        # 認証ユーザの場合はFavoriteArticleFormに現在のユーザ名を設定
        username = self.request.user.username
        initial_form_dict = dict(username=username)
        favorite_form = FavoriteArticleForm(request.GET or None,
                                            initial=initial_form_dict)
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        context['favorite_form'] = favorite_form

        return render(request, self.template_name, context)


class PostCommentView(LoginRequiredMixin, CreateView):
    template_name = ''
    form_class = PostCommentForm

    def form_valid(self, form):
        article_id = self.kwargs['pk']
        article = get_object_or_404(Article, pk=article_id)
        author = User.objects.get(pk=self.request.user.pk)

        comment = form.save(commit=False)
        comment.article = article
        comment.comment_author = author
        comment.save()
        return redirect('articles:article', pk=article_id)

    # GETリクエストされた場合はとりあえずリダイレクトさせる
    def get(self, request, *args, **kwargs):
        article_id = self.kwargs['pk']
        return redirect('articles:article', pk=article_id)


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
