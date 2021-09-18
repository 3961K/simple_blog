from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from io import BytesIO
import tempfile
from urllib.parse import urlencode
from PIL import Image

from .forms import UpdateUsernameForm, UpdateEmailForm, UpdatePasswordForm, \
    CreateArticleForm, UpdateArticleForm, UpdateProfileForm
from authenticate.models import Relation
from articles.models import Article, Tag

# Create your tests here.
User = get_user_model()

MEDIA_ROOT = tempfile.mkdtemp()


class UpdateUsernameFormTest(TestCase):
    # 30文字以内の文字列はユーザ名として妥当である
    def test_valid(self):
        correct_data = {
            'username': 'A' * 30
        }
        form = UpdateUsernameForm(correct_data)
        self.assertTrue(form.is_valid())

    # 31文字以上の文字列及び空文字はユーザ名として妥当でない
    def test_invalid(self):
        wrong_data_list = [
            {
                'username': 'A' * 31
            },
            {
                'username': ''
            }
        ]

        for wrong_data in wrong_data_list:
            form = UpdateUsernameForm(wrong_data)
            self.assertFalse(form.is_valid())


class UpdateUsernameViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='uuv_tester',
                                 email='uuv_test@test.com',
                                 password='uuvtester0512')
        User.objects.create_user(username='uuv_tester2',
                                 email='uuv_test2@test.com',
                                 password='uuvtester0512')
        return super().setUpClass()

    # ログインしていない場合は302が返される
    def test_redirect_nologin(self):
        response = self.client.get(reverse('settings:username'))
        self.assertEqual(response.status_code, 302)

    # ログインしている場合は200を返される
    def test_success_access(self):
        user = User.objects.get(username='uuv_tester')
        self.client.force_login(user)
        response = self.client.get(reverse('settings:username'))
        self.assertEqual(response.status_code, 200)

    # 既存のユーザ名では更新する事が出来ない
    def test_fail_update_diplicated_username(self):
        err_message = "同じユーザー名が既に登録済みです。"

        user = User.objects.get(username='uuv_tester')
        self.client.force_login(user)

        post_data = {
            'username': 'uuv_tester2'
        }
        response = self.client.post(reverse('settings:username'),
                                    post_data,
                                    format='text/html')
        self.assertContains(response, err_message)

    # 新たなユーザ名によってユーザ名を更新する事が出来る
    def test_success_update_username(self):
        user = User.objects.get(username='uuv_tester')
        self.client.force_login(user)

        post_data = {
            'username': 'uuv_tester3'
        }
        response = self.client.post(reverse('settings:username'),
                                    post_data,
                                    format='text/html')
        self.assertEqual(response.status_code, 302)

        # メールアドレスが同一であるかによってユーザ名が変更されたか確認する
        user = User.objects.get(username='uuv_tester3')
        self.assertEquals(user.email, 'uuv_test@test.com')


class UpdateEmailFormTest(TestCase):
    # 一般的なメールアドレスに近しい文字列はメールアドレスとして妥当である
    def test_valid(self):
        correct_data = {
            'email': 'ueftest@test.com'
        }
        form = UpdateEmailForm(correct_data)
        self.assertTrue(form.is_valid())

    # 一般的なメールアドレスからかけ離れている文字列と空文字はメールアドレスとして妥当である
    def test_invalid(self):
        wrong_data_list = [
            {
                'email': 'A'
            },
            {
                'email': ''
            }
        ]

        for wrong_data in wrong_data_list:
            form = UpdateEmailForm(wrong_data)
            self.assertFalse(form.is_valid())


class UpdateEmailViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='uev_tester',
                                 email='uevtest@test.com',
                                 password='uevtester0512')
        User.objects.create_user(username='uev_tester2',
                                 email='uevtest2@test.com',
                                 password='uevtester0512')
        return super().setUpClass()

    # ログインしていない場合は302が返される
    def test_redirect_nologin(self):
        response = self.client.get(reverse('settings:email'))
        self.assertEqual(response.status_code, 302)

    # ログインしている場合は200を返される
    def test_success_access(self):
        user = User.objects.get(username='uev_tester')
        self.client.force_login(user)
        response = self.client.get(reverse('settings:email'))
        self.assertEqual(response.status_code, 200)

    # 既存のメールアドレスでは更新する事が出来ない
    def test_fail_update_diplicated_username(self):
        err_message = "この メールアドレス を持った ユーザー が既に存在します。"

        user = User.objects.get(username='uev_tester')
        self.client.force_login(user)

        post_data = {
            'email': 'uevtest2@test.com'
        }
        response = self.client.post(reverse('settings:email'),
                                    post_data,
                                    format='text/html')
        self.assertContains(response, err_message)

    # 新たなユーザ名によってユーザ名を更新する事が出来る
    def test_success_update_username(self):
        user = User.objects.get(username='uev_tester')
        self.client.force_login(user)

        post_data = {
            'email': 'uevtest3@test.com'
        }
        response = self.client.post(reverse('settings:email'),
                                    post_data,
                                    format='text/html')
        self.assertEqual(response.status_code, 302)

        # ユーザ名が同一であるかによってがメールアドレス変更されたか確認する
        user = User.objects.get(email='uevtest3@test.com')
        self.assertEquals(user.username, 'uev_tester')


class UpdateFolloweeViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        for i in range(1, 11):
            User.objects.create_user(username='ufvtester{}'.format(i),
                                     email='ufvtester{}@test.com'.format(i),
                                     password='ufvtester0721')

        user1 = User.objects.filter(username='ufvtester1').get()
        for i in range(2, 11):
            followee = User.objects.get(username='ufvtester{}'.format(i))
            Relation.objects.create(followee=followee, follower=user1)

        return super().setUpClass()

    # ログインしていない場合は302が返される
    def test_redirect_nologin(self):
        response = self.client.get(reverse('settings:followees'))
        self.assertEqual(response.status_code, 302)

    # ログインしている場合は200を返される
    def test_success_access(self):
        user = User.objects.get(username='ufvtester1')
        self.client.force_login(user)
        response = self.client.get(reverse('settings:followees'))
        self.assertEqual(response.status_code, 200)

    # /?page=1・/?page=2にアクセスする事が出来る
    def test_success_access_page12(self):
        user = User.objects.get(username='ufvtester1')
        self.client.force_login(user)

        response = self.client.get(''.join([reverse('settings:followees'),
                                            '?', urlencode(dict(page='1'))]))
        self.assertEqual(response.status_code, 200)

        response2 = self.client.get(''.join([reverse('settings:followees'),
                                            '?', urlencode(dict(page='2'))]))
        self.assertEqual(response2.status_code, 200)

    # /?page=6(存在しないページ)にアクセスする事が出来ない
    def test_fail_access_page_over(self):
        user = User.objects.get(username='ufvtester1')
        self.client.force_login(user)

        response = self.client.get(''.join([reverse('settings:followees'),
                                            '?', urlencode(dict(page='6'))]))
        self.assertEqual(response.status_code, 404)


class UpdateFollowerViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        for i in range(1, 11):
            User.objects.create_user(username='ufrvtester{}'.format(i),
                                     email='ufrvtester{}@test.com'.format(i),
                                     password='ufrvtester0721')

        user1 = User.objects.filter(username='ufrvtester1').get()
        for i in range(2, 11):
            follower = User.objects.get(username='ufrvtester{}'.format(i))
            Relation.objects.create(followee=user1, follower=follower)

        return super().setUpClass()

    # ログインしていない場合は302が返される
    def test_redirect_nologin(self):
        response = self.client.get(reverse('settings:followers'))
        self.assertEqual(response.status_code, 302)

    # ログインしている場合は200を返される
    def test_success_access(self):
        user = User.objects.get(username='ufrvtester1')
        self.client.force_login(user)
        response = self.client.get(reverse('settings:followers'))
        self.assertEqual(response.status_code, 200)

    # /?page=1・/?page=2にアクセスする事が出来る
    def test_success_access_page12(self):
        user = User.objects.get(username='ufrvtester1')
        self.client.force_login(user)

        response = self.client.get(''.join([reverse('settings:followers'),
                                            '?', urlencode(dict(page='1'))]))
        self.assertEqual(response.status_code, 200)

        response2 = self.client.get(''.join([reverse('settings:followers'),
                                            '?', urlencode(dict(page='2'))]))
        self.assertEqual(response2.status_code, 200)

    # /?page=6(存在しないページ)にアクセスする事が出来ない
    def test_fail_access_page_over(self):
        user = User.objects.get(username='ufrvtester1')
        self.client.force_login(user)

        response = self.client.get(''.join([reverse('settings:followers'),
                                            '?', urlencode(dict(page='6'))]))
        self.assertEqual(response.status_code, 404)


class UpdatePasswordFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='update_password',
                                 email='updatepassword@test.com',
                                 password='update0123')
        return super().setUpClass()

    # 正しい形式の現パスワードと新パスワードは妥当である
    def test_valid_form(self):
        user = User.objects.get(username='update_password')
        new_password_data = {
            'old_password': 'update0123',
            'new_password1': 'updated0123',
            'new_password2': 'updated0123',
        }
        form = UpdatePasswordForm(user, new_password_data)
        self.assertTrue(form.is_valid())

    # 現在のパスワードが間違っている場合は妥当でない
    def test_invalid_wrong_password(self):
        user = User.objects.get(username='update_password')
        new_password_data = {
            'old_password': 'wrongpassword',
            'new_password1': 'updated0123',
            'new_password2': 'updated0123',
        }
        form = UpdatePasswordForm(user, new_password_data)
        self.assertFalse(form.is_valid())

    # 1つ目と2つ目の新しいパスワードが一致しない場合は妥当でない
    def test_invalid_mismatched_newpassword(self):
        user = User.objects.get(username='update_password')
        new_password_data = {
            'old_password': 'update0123',
            'new_password1': 'updated0123',
            'new_password2': 'updated01234',
        }
        form = UpdatePasswordForm(user, new_password_data)
        self.assertFalse(form.is_valid())


@override_settings(AXES_ENABLED=False)
class UpdatePasswordViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='update_password_view',
                                 email='updatepasswordview@test.com',
                                 password='update0123')
        return super().setUpClass()

    # ログインしている状態でアクセスする事が出来る
    def test_success_access(self):
        self.client.login(username='update_password_view',
                          password='update0123')
        response = self.client.get(reverse('settings:password'))
        self.assertEqual(response.status_code, 200)

    # ログインしていない状態ではアクセスする事が出来ない
    def test_fail_access(self):
        response = self.client.get(reverse('settings:password'))
        self.assertEqual(response.status_code, 302)

    # 正しい形式の新しいパスワードによって更新する事が出来る
    def test_success_update(self):
        self.client.login(username='update_password_view',
                          password='update0123')
        update_data = {
            'old_password': 'update0123',
            'new_password1': 'updated0123',
            'new_password2': 'updated0123',
        }
        response = self.client.post(reverse('settings:password'),
                                    update_data, format='text/html')
        self.assertEqual(response.status_code, 302)

    # 現在のパスワードが間違っている場合は更新出来ない
    def test_fail_update_wrong_password(self):
        self.client.login(username='update_password_view',
                          password='update0123')
        wrong_password_data = {
            'old_password': 'wrong_password',
            'new_password1': 'updated0123',
            'new_password2': 'updated0123',
        }
        response = self.client.post(reverse('settings:password'),
                                    wrong_password_data, format='text/html')
        self.assertNotEqual(response.status_code, 302)

    # 1つ目と2つ目の新しいパスワードが一致しない場合は更新出来ない
    def test_fail_update_missmatched_password(self):
        self.client.login(username='update_password_view',
                          password='update0123')
        missmatched_password = {
            'old_password': 'update0123',
            'new_password1': 'updated0123',
            'new_password2': 'updated01234',
        }
        response = self.client.post(reverse('settings:password'),
                                    missmatched_password, format='text/html')
        self.assertNotEqual(response.status_code, 302)


@override_settings(AXES_ENABLED=False)
class DeleteUserViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='delete_user_view',
                                 email='deleteuserview@test.com',
                                 password='delete0123')
        return super().setUpClass()

    # ログインしている状態でアクセスする事が出来る
    def test_success_access(self):
        self.client.login(username='delete_user_view',
                          password='delete0123')
        response = self.client.get(reverse('settings:deleteuser'))
        self.assertEqual(response.status_code, 200)

    # ログインしていない状態ではアクセスする事が出来ない
    def test_fail_access(self):
        response = self.client.get(reverse('settings:deleteuser'))
        self.assertEqual(response.status_code, 302)

    # ログインしている状態でPOSTリクエストを送信する事でそのユーザを削除する
    def test_success_delete(self):
        self.client.login(username='delete_user_view',
                          password='delete0123')
        response = self.client.post(reverse('settings:deleteuser'))

        self.assertEqual(response.status_code, 302)
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(username='delete_user_view')


class CreateArticleFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        Tag.objects.create(tag='post_article_post_test')
        return super().setUpClass()

    # 正しいタイトル・記事内容は妥当である
    def test_valid_form(self):
        article_tag = Tag.objects.get(tag='post_article_post_test')
        article_data = {
            'title': 'A' * 1000,
            'content': 'A' * 10000,
            'tags': [article_tag]
        }

        form = CreateArticleForm(data=article_data)
        self.assertTrue(form.is_valid())

    # 誤った形式のタイトル・記事内容は妥当でない
    def test_invalid_wrongformat(self):
        article_tag = Tag.objects.get(tag='post_article_post_test')

        wrong_format_data_list = [
            {
                'title': 'A' * 1001,
                'content': 'sample_content',
                'tags': [article_tag]
            },
            {
                'title': 'sample_title',
                'content': 'A' * 10001,
                'tags': [article_tag]
            },
            {
                'title': 'A' * 1001,
                'content': 'A' * 10001,
                'tags': []
            }
        ]

        for wrong_format_data in wrong_format_data_list:
            form = CreateArticleForm(data=wrong_format_data)
            self.assertFalse(form.is_valid())


@override_settings(AXES_ENABLED=False)
class CreateArticleViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='create_article_view',
                                 email='create_article_view@test.com',
                                 password='createart1cle')
        Tag.objects.create(tag='create_article_view_test')
        return super().setUpClass()

    # ログインしている状態でビューにアクセスする事が出来る
    def test_success_access(self):
        self.client.login(username='create_article_view',
                          password='createart1cle')
        response = self.client.get(reverse('settings:newarticle'))
        self.assertEqual(response.status_code, 200)

    # ログインしていない状態ではビューにアクセスする事が出来ない
    def test_fail_access_not_logined(self):
        response = self.client.get(reverse('settings:newarticle'))
        self.assertEqual(response.status_code, 302)

    # 正しい形式のタイトル・内容で記事を登録する事が出来る
    def test_success_post_article(self):
        self.client.login(username='create_article_view',
                          password='createart1cle')
        response = self.client.get(reverse('settings:newarticle'))
        self.assertEqual(response.status_code, 200)

        article_tag = Tag.objects.get(tag='create_article_view_test')
        article_data = {
            'title': 'A' * 1000,
            'content': 'A' * 10000,
            'tags': [article_tag.pk]
        }
        post_response = self.client.post(reverse('settings:newarticle'),
                                         article_data,
                                         format='text/html')
        self.assertEqual(post_response.status_code, 302)

        posted_article = Article.objects.get(title='A' * 1000)
        self.assertIsNotNone(posted_article)

    # 誤った形式のタイトル・内容では記事を登録する事が出来ない
    def test_fail_post_article_wrongformat(self):
        self.client.login(username='create_article_view', password='createart1cle')
        response = self.client.get(reverse('settings:newarticle'))
        self.assertEqual(response.status_code, 200)

        article_tag = Tag.objects.get(tag='create_article_view_test')
        wrong_format_data_list = [
            {
                'title': 'A' * 1001,
                'content': 'A' * 10000,
                'tags': [article_tag]
            },
            {
                'title': 'A' * 1000,
                'content': 'A' * 10001,
                'tags': [article_tag]
            },
            {
                'title': 'A' * 1001,
                'content': 'A' * 10001,
                'tags': []
            }
        ]

        for wrong_format_data in wrong_format_data_list:
            post_response = self.client.post(reverse('settings:newarticle'),
                                             wrong_format_data,
                                             format='text/html')
            self.assertEqual(post_response.status_code, 200)


@override_settings(AXES_ENABLED=False)
class PostedArticleListView(TestCase):
    # 表示する記事を作成
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='pavtester',
                                 email='pavtester@test.com',
                                 password='pavtester0123')
        user = User.objects.get(username='pavtester')
        for i in range(1, 7):
            article = Article(author=user,
                              title='test_title{}'.format(i),
                              content='test_content{}'.format(i))
            article.save()

        return super().setUpClass()

    # ログインしている状態でビューにアクセスする事が出来る
    def test_success_access(self):
        self.client.login(username='pavtester',
                          password='pavtester0123')
        response = self.client.get(reverse('settings:postedarticles'))
        self.assertEqual(response.status_code, 200)

    # ログインしていない状態ではビューにアクセスする事が出来ない
    def test_fail_access_not_logined(self):
        response = self.client.get(reverse('settings:postedarticles'))
        self.assertEqual(response.status_code, 302)

    # /?page=1・/?page=2にアクセスする事が出来る
    def test_success_access_page12(self):
        self.client.login(username='pavtester',
                          password='pavtester0123')
        response = self.client.get(''.join([reverse('settings:postedarticles'),
                                            '?', urlencode(dict(page='1'))]))
        self.assertEqual(response.status_code, 200)

        response2 = self.client.get(''.join([reverse('settings:postedarticles'),
                                             '?', urlencode(dict(page='2'))]))
        self.assertEqual(response2.status_code, 200)

    # /?page=6(存在しないページ)にアクセスする事が出来ない
    def test_fail_access_page12(self):
        self.client.login(username='pavtester',
                          password='pavtester0123')
        response = self.client.get(''.join([reverse('settings:postedarticles'),
                                            '?', urlencode(dict(page='6'))]))
        self.assertEqual(response.status_code, 404)


class UpdateArticlePostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        Tag.objects.create(tag='update_article_post_tester')
        return super().setUpClass()

    # 正しいタイトル・記事内容は妥当である
    def test_valid_form(self):
        article_tag = Tag.objects.get(tag='update_article_post_tester')
        article_data = {
            'title': 'A' * 1000,
            'content': 'A' * 10000,
            'tags': [article_tag]
        }
        form = UpdateArticleForm(data=article_data)
        self.assertTrue(form.is_valid())

    # 誤った形式のタイトル・記事内容は妥当でない
    def test_invalid_wrongformat(self):
        article_tag = Tag.objects.get(tag='update_article_post_tester')
        wrong_format_data_list = [
            {
                'title': 'A' * 1001,
                'content': 'sample_content',
                'tags': [article_tag]
            },
            {
                'title': 'A' * 1000,
                'content': 'A' * 10001,
                'tags': [article_tag]
            },
            {
                'title': 'A' * 1001,
                'content': 'A' * 10001,
                'tags': []
            }
        ]

        for wrong_format_data in wrong_format_data_list:
            form = UpdateArticleForm(data=wrong_format_data)
            self.assertFalse(form.is_valid())


@override_settings(AXES_ENABLED=False)
class UpdateArticleViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='updatearticleview_tester',
                                 email='updatearticleview@test.com',
                                 password='postarticle0123')
        User.objects.create_user(username='updatearticleview_tester2',
                                 email='updatearticleview2@test.com',
                                 password='postarticle0123')

        user = User.objects.get(username='updatearticleview_tester')
        user2 = User.objects.get(username='updatearticleview_tester2')

        Tag.objects.create(tag='updatearticleview_test_tag')
        article_tag = Tag.objects.get(tag='updatearticleview_test_tag')

        Article.objects.create(author_id=user.pk, title='test_title',
                               content='test_content')
        article = Article.objects.filter(title='test_title').first()
        article.tags.add(article_tag)
        article.save()

        Article.objects.create(author_id=user2.pk, title='test_title2',
                               content='test_content2')
        article2 = Article.objects.filter(title='test_title2').first()
        article2.tags.add(article_tag)
        article2.save()
        return super().setUpClass()

    # ログインしているユーザに関連している記事のページへアクセスする事が出来る
    def test_success_access(self):
        self.client.login(username='updatearticleview_tester',
                          password='postarticle0123')
        author = User.objects.get(username='updatearticleview_tester')
        article = Article.objects.filter(title='test_title', author=author).get()
        response = self.client.get(reverse('settings:updatearticle',
                                           kwargs={'pk': article.pk}))
        self.assertEquals(response.status_code, 200)

    # ログインしていない状態ではアクセスする事が出来ない
    def test_fail_access_notlogin(self):
        author = User.objects.get(username='updatearticleview_tester')
        article = Article.objects.filter(title='test_title', author=author).get()
        response = self.client.get(reverse('settings:updatearticle',
                                           kwargs={'pk': article.pk}))
        self.assertEquals(response.status_code, 302)

    # ログインをしている状態で存在しない記事のページへアクセスする事が出来ない
    def test_fail_access_notexist(self):
        self.client.login(username='updatearticleview_tester2',
                          password='postarticle0123')
        response = self.client.get(reverse('settings:updatearticle',
                                           kwargs={'pk': 1000}))
        self.assertEquals(response.status_code, 404)

    # ログインしているユーザが作成していない記事のページへアクセスする事が出来ない
    def test_fail_access_notauthor(self):
        self.client.login(username='updatearticleview_tester2',
                          password='postarticle0123')
        response = self.client.get(reverse('settings:updatearticle',
                                           kwargs={'pk': 1}))
        self.assertEquals(response.status_code, 403)

    # 正しい形式のタイトル・内容によって記事を変更する事が出来る
    def test_success_edit(self):
        self.client.login(username='updatearticleview_tester',
                          password='postarticle0123')
        author = User.objects.get(username='updatearticleview_tester')
        article = Article.objects.filter(title='test_title', author=author).get()
        response = self.client.get(reverse('settings:updatearticle',
                                           kwargs={'pk': article.pk}))
        self.assertEquals(response.status_code, 200)

        # タグの形式が間違っていると表示されている
        tag = Tag.objects.get(tag='updatearticleview_test_tag')
        edit_data = {
            'title': 'A' * 1000,
            'content': 'A' * 10000,
            'tags': [tag.pk],
        }
        response = self.client.post(reverse('settings:updatearticle',
                                            kwargs={'pk': article.pk}),
                                    edit_data, format='text/html')
        self.assertEquals(response.status_code, 302)

    # 誤った形式のタイトル・内容によって記事を変更する事が出来ない
    def test_fail_edit_wrongformat(self):
        self.client.login(username='updatearticleview_tester',
                          password='postarticle0123')
        author = User.objects.get(username='updatearticleview_tester')
        article = Article.objects.filter(title='test_title', author=author).get()
        response = self.client.get(reverse('settings:updatearticle',
                                           kwargs={'pk': article.pk}))
        self.assertEquals(response.status_code, 200)

        wrong_format_edit_data_list = [
            {
                'title': 'A' * 1001,
                'content': 'sample_content'
            },
            {
                'title': 'sample_title',
                'content': 'A' * 10001
            },
            {
                'title': 'A' * 1001,
                'content': 'A' * 10001
            }
        ]
        for wrong_format_edit_data in wrong_format_edit_data_list:
            response = self.client.post(reverse('settings:updatearticle',
                                                kwargs={'pk': article.pk}),
                                        wrong_format_edit_data,
                                        format='text/html')
            self.assertEquals(response.status_code, 200)


@override_settings(AXES_ENABLED=False)
class DeleteArticleViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='deletearticleview_tester',
                                 email='deletearticleview@test.com',
                                 password='postarticle0123')
        User.objects.create_user(username='deletearticleview_tester2',
                                 email='deletearticleview2@test.com',
                                 password='postarticle0123')

        user = User.objects.get(username='deletearticleview_tester')
        user2 = User.objects.get(username='deletearticleview_tester2')

        Tag.objects.create(tag='deletearticleview_test_tag')
        article_tag = Tag.objects.get(tag='deletearticleview_test_tag')

        Article.objects.create(author_id=user.pk, title='test_title',
                               content='test_content')
        article = Article.objects.filter(title='test_title').first()
        article.tags.add(article_tag)
        article.save()

        Article.objects.create(author_id=user2.pk, title='test_title2',
                               content='test_content2')
        article2 = Article.objects.filter(title='test_title2').first()
        article2.tags.add(article_tag)
        article2.save()

    # GETリクエストによるHTTPアクセスはリダイレクトされる
    def test_success_redirect(self):
        self.client.login(username='deletearticleview_tester',
                          password='postarticle0123')
        author = User.objects.get(username='deletearticleview_tester')
        article = Article.objects.filter(title='test_title', author=author).get()
        response = self.client.get(reverse('settings:deletearticle',
                                           kwargs={'pk': article.pk}))
        self.assertEquals(response.status_code, 302)

    # 作者としてログインしている状態でPOSTリクエストを送信する事で削除する事ができる
    def test_success_delete_login_as_author(self):
        self.client.login(username='deletearticleview_tester',
                          password='postarticle0123')
        author = User.objects.get(username='deletearticleview_tester')
        article = Article.objects.filter(title='test_title', author=author).get()
        response = self.client.post(reverse('settings:deletearticle',
                                            kwargs={'pk': article.pk}))
        self.assertEquals(response.status_code, 302)
        with self.assertRaises(ObjectDoesNotExist):
            Article.objects.filter(title='test_title', author=author).get()

    # 作者ではないユーザとしてログインしている場合はPOSTリクエストを送信しても削除する事は出来ない
    def test_fail_delete_login_as_other(self):
        self.client.login(username='deletearticleview_tester2',
                          password='postarticle0123')
        author = User.objects.get(username='deletearticleview_tester')
        article = Article.objects.filter(title='test_title', author=author).get()
        response = self.client.post(reverse('settings:deletearticle',
                                            kwargs={'pk': article.pk}))
        self.assertEquals(response.status_code, 403)

    # ログインしていない場合はPOSTリクエストを送信しても削除する事は出来ない
    def test_fail_delete_without_login(self):
        author = User.objects.get(username='deletearticleview_tester')
        article = Article.objects.filter(title='test_title', author=author).get()
        response = self.client.post(reverse('settings:deletearticle',
                                            kwargs={'pk': article.pk}))
        self.assertEquals(response.status_code, 302)


class NeedImageTestMxin():
    def create_image_dict(self, size=(1024, 1024)):
        img_file = BytesIO()
        img = Image.new('RGBA', size=size, color=(255, 255, 255))
        img.save(img_file, 'png')
        img_file.name = 'test.png'
        img_file.seek(0)

        img_dict = {
            'icon': SimpleUploadedFile(
                img_file.name,
                img_file.read(),
                content_type='image/png')}
        return img_dict


class UpdateProfileFormTest(NeedImageTestMxin, TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='updateproileformtester',
                                 email='updateproileformtester@test.com',
                                 password='updatepr0f1le0123')
        return super().setUpClass()

    # 縦幅・横幅1024px以下の画像と1000文字以下の文字列はアイコンとプロフィールとして妥当な値である
    def test_valid(self):
        user = User.objects.get(username='updateproileformtester')
        correct_icon_dict = self.create_image_dict()

        correct_profile = {
            'profile_message': 'A' * 1000,
        }

        form = UpdateProfileForm(user, correct_profile, correct_icon_dict)
        self.assertTrue(form.is_valid())

    # 縦幅・横幅1024px以上の画像もしくは1000文字以上の文字列はアイコンとプロフィールとして妥当な値ではない
    def test_invalid(self):
        correct_icon_dict = self.create_image_dict()
        wrong_icon_dict = self.create_image_dict(size=(1024, 1025))
        wrong_icon_dict2 = self.create_image_dict(size=(1025, 1024))

        correct_profile = {
            'profile_message': 'A' * 1000,
        }
        wrong_profile = {
            'profile_message': 'A' * 1001,
        }

        wrong_pattern_list = [
            {
                "profile": correct_profile,
                "icon": wrong_icon_dict
            },
            {
                "profile": correct_profile,
                "icon": wrong_icon_dict2
            },
            {
                "profile": wrong_profile,
                "icon": correct_icon_dict
            },
            {
                "profile": wrong_profile,
                "icon": wrong_icon_dict
            },
            {
                "profile": wrong_profile,
                "icon": wrong_icon_dict2
            }
        ]

        for wrong_pattern in wrong_pattern_list:
            form = UpdateProfileForm(wrong_pattern["profile"], wrong_pattern["icon"])
            self.assertFalse(form.is_valid())


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
@override_settings(AXES_ENABLED=False)
class UpdateProfileViewTest(NeedImageTestMxin, TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='updateprofileview_tester',
                                 email='updateprofileview@test.com',
                                 password='pr0f1le0123')
        return super().setUpClass()

    # ログインしているユーザに関連している記事のページへアクセスする事が出来る
    def test_success_access(self):
        self.client.login(username='updateprofileview_tester',
                          password='pr0f1le0123')
        response = self.client.get(reverse('settings:profile'))
        self.assertEquals(response.status_code, 200)

    # ログインしていない状態ではアクセスする事が出来ない
    def test_fail_access_notlogin(self):
        response = self.client.get(reverse('settings:profile'))
        self.assertEquals(response.status_code, 302)

    # 縦幅・横幅1024px以下の画像と1000文字以下の文字列はアイコンとプロフィールによって更新する事が出来る
    def test_success_update_profile(self):
        self.client.login(username='updateprofileview_tester',
                          password='pr0f1le0123')

        correct_icon_dict = self.create_image_dict()
        correct_profile = {
            'icon': correct_icon_dict['icon'],
            'profile_message': 'A' * 1000,
        }
        response = self.client.post(reverse('settings:profile'),
                                    correct_profile,
                                    format='text/html')
        self.assertEquals(response.status_code, 302)

        user = User.objects.get(username='updateprofileview_tester')
        self.assertEquals(user.icon, 'images/test.png')
        self.assertEquals(user.profile_message, 'A' * 1000)
