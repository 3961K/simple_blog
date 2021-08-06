import datetime
from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()


class Tag(models.Model):
    tag = models.CharField(max_length=100, blank=False, null=False, unique=True)

    def __str__(self):
        return self.tag


class Article(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='my_articles')
    title = models.CharField(max_length=1000)
    content = models.TextField(max_length=10000)
    create_date = models.DateField(default=datetime.date.today)
    tags = models.ManyToManyField(Tag, related_name='tagged_articles')
    favorite_users = models.ManyToManyField(User,
                                            blank=True,
                                            related_name='favorited_aritcles')

    class Meta:
        ordering = ['-create_date']

    def __str__(self):
        return self.title

    def is_favorited(self, user):
        """
        Userオブジェクトである引数userが記事をお気に入りに登録しているか否かの状態を返す

        Parameters
        ----------
        user : User
            お気に入りしているユーザ(favaorite_users)の中に含まれているか確認する対象

        Raises
        ------
        TypeError
            userオブジェクトがUserクラスのインスタンスで無い場合に発生

        Returns
        -------
        False : bool
            userが認証されていないユーザの場合もしくは,favorite_usersに含まれていない場合

        True : bool
            userが認証されており,かつfavorite_usersに含まれている
        """
        if (not user.is_authenticated
                or not self.favorite_users.filter(pk=user.pk).exists()):
            return False
        return True


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    comment_author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    create_data = models.DateField(auto_now_add=True)

    def __str__(self):
        return 'comment by {} at {}'.format(self.comment_author,
                                            self.create_data)
