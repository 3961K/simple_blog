from django.test import TestCase, override_settings
from django.db.utils import IntegrityError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse


from .models import User, Relation
from .forms import LoginForm, RegisterForm

# Create your tests here.


class UserTest(TestCase):
    # 必須フィールドのみでユーザを作成出来る
    def test_success_create_user_only_required(self):
        User(username='onlyrequired', email='onlyrequired@test.com',
             password='onlyrequiredtest').save()
        usr = User.objects.get(username='onlyrequired')
        self.assertIsNotNone(usr)

    # 必須フィールド以外のフィールドも指定してユーザを作成出来る
    def test_success_create_user_with_optional(self):
        User(username='optional', email='optional@test.com',
             password='optionaltest', icon='dummy.png',
             profile_message='sample profile message',
             first_name='optional', last_name='user').save()
        usr = User.objects.get(username='optional')
        self.assertIsNotNone(usr)

    # 正確にデータを登録する事が出来る (password除く)
    def test_correct_registered_data(self):
        register_data = {
            'username': 'register',
            'email': 'register@test.com',
            'icon': 'register.png',
            'profile_message': 'sample profile message',
            'first_name': 'register',
            'last_name': 'tester'
        }
        User(username=register_data['username'], email=register_data['email'],
             password='register1234', icon=register_data['icon'],
             profile_message=register_data['profile_message'],
             first_name=register_data['first_name'],
             last_name=register_data['last_name']).save()

        # password以外の各フィールドがregister_dataと同じであるか検証
        usr = User.objects.get(username='register')
        for key, value in register_data.items():
            self.assertEqual(value, getattr(usr, key))

    # 重複が許されていないユーザ名・メールアドレスにおいて既に登録されている情報では登録する事が出来ない
    def test_fail_create_user_duplicated(self):
        User(username='dummy', email='dummy@test.com',
             password='password1234').save()

        def create_duplicated_username():
            try:
                with transaction.atomic():
                    User(username='dummy', email='failduplicated@test.com',
                         password='failduplicated').save()
            except IntegrityError:
                raise IntegrityError()

        with self.assertRaises(IntegrityError):
            create_duplicated_username()

        def create_duplicated_email():
            try:
                with transaction.atomic():
                    User(username='failduplicated', email='dummy@test.com',
                         password='failduplicated').save()
            except IntegrityError:
                raise IntegrityError()

        with self.assertRaises(IntegrityError):
            create_duplicated_email()

    # 正しい値でユーザのフィールドを更新する事が出来る
    def test_success_update(self):
        username_for_update = 'updated_dummy4update'
        email_for_update = 'updated_dummy4update@test.com'
        User(username='dummy4update', email='dummy4update@test.com',
             password='password1234').save()

        user = User.objects.get(username='dummy4update')
        user.username = username_for_update
        user.email = email_for_update
        user.save()

        updated_user = User.objects.get(username='updated_dummy4update')
        self.assertEqual(updated_user.username, username_for_update)
        self.assertEqual(updated_user.email, email_for_update)

    # 重複が許されていないユーザ名・メールアドレスにおいて既に登録されている情報では更新する事が出来ない
    def test_fail_update_duplicated(self):
        User(username='dummy', email='dummy@test.com',
             password='password1234').save()
        User(username='dummy2', email='dummy2@test.com',
             password='password1234').save()

        user = User.objects.get(username='dummy2')

        def update_duplicated_username():
            user.username = 'dummy'
            try:
                with transaction.atomic():
                    user.save()
            except IntegrityError:
                raise IntegrityError()

        with self.assertRaises(IntegrityError):
            update_duplicated_username()

        def update_duplicated_email():
            user.email = 'dummy@test.com'
            try:
                with transaction.atomic():
                    user.save()
            except IntegrityError:
                raise IntegrityError()

        with self.assertRaises(IntegrityError):
            update_duplicated_email()

    # 指定したユーザを削除する事が出来る
    def test_succes_delete(self):
        User(username='dummy4delete', email='dummy4delete@test.com',
             password='password1234').save()
        user = User.objects.get(username='dummy4delete')
        user.delete()
        with self.assertRaises(ObjectDoesNotExist):
            user = User.objects.get(username='dummy4delete')

    # 指定したユーザをフォローする事が出来る
    def test_success_follow(self):
        User.objects.create(username='follower', email='follower@test.com',
                            password='password1234')
        User.objects.create(username='followee', email='followee@test.com',
                            password='password1234')

        follower = User.objects.get(username='follower')
        followee = User.objects.get(username='followee')

        # followerがfolloweeをフォローするリレーションが作成される
        follower.followee_relations.create(followee=followee)
        relation = follower.followee_relations.get(followee=followee)
        self.assertIsNotNone(relation)

    # 指定したユーザ間のフォロー関係を削除する
    def test_success_unfollow(self):
        User.objects.create(username='follower', email='follower@test.com',
                            password='password1234')
        User.objects.create(username='followee', email='followee@test.com',
                            password='password1234')

        follower = User.objects.get(username='follower')
        followee = User.objects.get(username='followee')

        # followerがfolloweeをフォローする
        follower.followee_relations.create(followee=followee)
        relation = follower.followee_relations.get(followee=followee)
        self.assertIsNotNone(relation)

        # followerがfolloweeがフォローしている関係を削除する
        relation.delete()
        with self.assertRaises(ObjectDoesNotExist):
            follower.followee_relations.get(followee=followee)


class RelationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create(username='relation_follower',
                            email='relation_follower@test.com',
                            password='password1234')
        User.objects.create(username='relation_followee',
                            email='relation_followee@test.com',
                            password='password1234')
        return super().setUpClass()

    # 関係を作成する事が出来る
    def test_success_create_relation(self):
        follower = User.objects.get(username='relation_follower')
        followee = User.objects.get(username='relation_followee')

        Relation.objects.create(follower=follower, followee=followee)
        relation = Relation.objects.get(follower=follower, followee=followee)
        self.assertIsNotNone(relation)

    # 関係を削除する事が出来る
    def test_success_delete_relation(self):
        follower = User.objects.get(username='relation_follower')
        followee = User.objects.get(username='relation_followee')

        Relation.objects.create(follower=follower, followee=followee)
        relation = Relation.objects.get(follower=follower, followee=followee)
        self.assertIsNotNone(relation)

        relation.delete()
        with self.assertRaises(ObjectDoesNotExist):
            Relation.objects.get(follower=follower, followee=followee)

    # 重複した関係は作成する事が出来ない
    def test_fail_create_duplicated_relation(self):
        follower = User.objects.get(username='relation_follower')
        followee = User.objects.get(username='relation_followee')

        Relation.objects.create(follower=follower, followee=followee)
        relation = Relation.objects.get(follower=follower, followee=followee)
        self.assertIsNotNone(relation)

        with self.assertRaises(IntegrityError):
            Relation.objects.create(follower=follower, followee=followee)


@override_settings(AXES_ENABLED=False)
class LoginFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='loginformtester',
                                 email='loginform@test.com',
                                 password='l0g1nt3st3r')
        return super().setUpClass()

    # 正しいユーザ名・パスワードは妥当な入力値である
    def test_valid_login(self):
        login_data = {
            'username': 'loginformtester',
            'password': 'l0g1nt3st3r'
        }
        form = LoginForm(data=login_data)
        # エラー
        self.assertTrue(form.is_valid())

    # 存在しないユーザ名は妥当な入力値ではない
    def test_invalid_notexist_username(self):
        login_data = {
            'username': 'notexistuseraname',
            'password': 'l0g1nt3st3r'
        }
        # エラー
        form = LoginForm(data=login_data)
        self.assertFalse(form.is_valid())

    # ユーザ名に対して誤ったパスワードは妥当な入力値ではない
    def test_invalid_wrong_password(self):
        login_data = {
            'username': 'loginformtester',
            'password': 'wrongpassword'
        }
        # エラー
        form = LoginForm(data=login_data)
        self.assertFalse(form.is_valid())


class LoginViewTest(TestCase):
    # ログイン用のユーザを作成
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='loginviewtester',
                                 email='loginview@test.com',
                                 password='l0g1nt3st3r')
        return super().setUpClass()

    # ログインビューにアクセスする事が出来る
    def test_success_access(self):
        response = self.client.get(reverse('authenticate:login'))
        self.assertEqual(response.status_code, 200)

    # 正しいユーザ名・パスワードの組み合わせを用いてログインする事が出来る
    def test_success_login(self):
        login_data = {
            'username': 'loginviewtester',
            'password': 'l0g1nt3st3r'
        }
        response = self.client.post(reverse('authenticate:login'),
                                    login_data,
                                    format='text/html')
        self.assertEqual(response.status_code, 302)

    # 正しくないユーザ名・パスワードの組み合わせではログインする事が出来ず,
    # 4回目のログイン失敗によってアカウントがロックされる
    def test_fail_login(self):
        err_message = '正しいユーザー名とパスワードを入力してください。'\
            'どちらのフィールドも大文字と小文字は区別されます。'

        wrong_value_list = [
            ['loginviewtester', 'wrongpassword'],
            ['wrongusername', 'l0g1nt3st3r'],
            ['wrongusername', 'wrongpassword']
        ]

        for wrong_value in wrong_value_list:
            response = self.client.post(reverse('authenticate:login'),
                                        {'username': wrong_value[0],
                                        'password': wrong_value[1]},
                                        format='text/html')
            self.assertContains(response, err_message)

        # 4回目においてアカウントロックが行われる
        forth_response = self.client.post(reverse('authenticate:login'),
                                          {'username': wrong_value[0],
                                           'password': wrong_value[1]},
                                          format='text/html')

        self.assertEquals(forth_response.status_code, 403)


class LogoutViewTest(TestCase):
    # ログアウトページ自体に対するアクセスが可能か確認するテスト
    def test_success_access(self):
        response = self.client.get(reverse('authenticate:logout'))
        self.assertEqual(response.status_code, 302)


class RegisterFormTest(TestCase):
    # 正しい形式の値は妥当である
    def test_valid_form(self):
        register_info = {
            'username': 'formtester',
            'email': 'formtester@test.com',
            'password1': 'f0rmt3st3r0123',
            'password2': 'f0rmt3st3r0123'
        }
        form = RegisterForm(data=register_info)
        self.assertTrue(form.is_valid())

    # 必須フィールドが欠けた値は妥当でない
    def test_invalid_missed_required(self):
        missied_register_info_list = [
            {
                'email': 'formtester@test.com',
                'password1': 'f0rmt3st3r0123',
                'password2': 'f0rmt3st3r0123'
            },
            {
                'username': 'formtester',
                'password1': 'f0rmt3st3r0123',
                'password2': 'f0rmt3st3r0123'
            },
            {
                'username': 'formtester',
                'email': 'formtester@test.com',
                'password2': 'f0rmt3st3r0123'
            },
            {
                'username': 'formtester',
                'email': 'formtester@test.com',
                'password1': 'f0rmt3st3r0123'
            },
        ]

        for missied_register_info in missied_register_info_list:
            form = RegisterForm(data=missied_register_info)
            self.assertFalse(form.is_valid())

    # 誤った形式の値は妥当では無い
    def test_invalid_wrong_format(self):
        wrong_format_register_info_list = [
            {
                'username': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
                'email': 'formtester@test.com',
                'password1': 'f0rmt3st3r0123',
                'password2': 'f0rmt3st3r0123'
            },
            {
                'username': 'formtester',
                'email': 'formtester@a.a',
                'password1': 'f0rmt3st3r0123',
                'password2': 'f0rmt3st3r0123'
            },
            {
                'username': 'formtester',
                'email': 'formtester@a.a',
                'password1': 'f0rmt3st3r0123',
                'password2': 'f0rmt3st3r0124'
            }
        ]

        for wrong_format_register_info in wrong_format_register_info_list:
            form = RegisterForm(data=wrong_format_register_info)
            self.assertFalse(form.is_valid())

    # 重複が禁止されているため既に登録されているユーザ名・メールアドレスを含んだ値は妥当でない
    def test_invalid_duplicated(self):
        User(username='exited',
             email='exited@test.com',
             password='ex1te3dpass').save()

        exited_register_info_list = [
            {
                'username': 'exited',
                'email': 'formtester@test.com',
                'password1': 'f0rmt3st3r0123',
                'password2': 'f0rmt3st3r0123'
            },
            {
                'username': 'formtester',
                'email': 'exited@test.com',
                'password1': 'f0rmt3st3r0123',
                'password2': 'f0rmt3st3r0123'
            },
        ]

        for exited_register_info in exited_register_info_list:
            form = RegisterForm(data=exited_register_info)
            self.assertFalse(form.is_valid())


class RegisterViewTest(TestCase):
    # ユーザ登録ページにアクセス出来る
    def test_success_access(self):
        response = self.client.get(reverse('authenticate:register'))
        self.assertEqual(response.status_code, 200)

    # 必須フィールドのみ入力する事でユーザ登録する事が出来る
    def test_success_register(self):
        register_info = {
            'username': 'viewtester',
            'email': 'viewtester@test.com',
            'password1': 'v1ewt3st3r1234',
            'password2': 'v1ewt3st3r1234',
        }
        response = self.client.post(reverse('authenticate:register'),
                                    register_info,
                                    format='text/html')
        self.assertEqual(response.status_code, 302)

    # 誤った形式のユーザ名・メールアドレスでは登録する事が出来ない
    def test_fail_register_wrongformat(self):
        err_message_username = 'この値は 30 文字以下でなければなりません'
        err_message_email = '有効なメールアドレスを入力してください。'

        wrong_format_username = {
            'username': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            'email': 'viewtester@test.com',
            'password1': 'v1ewt3st3r1234',
            'password2': 'v1ewt3st3r1234',
        }
        response = self.client.post(reverse('authenticate:register'),
                                    wrong_format_username,
                                    format='text/html')
        self.assertContains(response, err_message_username)

        wrong_format_email = {
            'username': 'viewtester',
            'email': 'viewtester@a.a',
            'password1': 'v1ewt3st3r1234',
            'password2': 'v1ewt3st3r1234',
        }
        response = self.client.post(reverse('authenticate:register'),
                                    wrong_format_email,
                                    format='text/html')
        self.assertContains(response, err_message_email)

    # 既に登録済みのユーザ名・メールアドレスでは登録する事が出来ない
    def test_fail_register_duplicated(self):
        User.objects.create_user(username='viewtester',
                                 email='viewtester@test.com',
                                 password='v1ewt3st3r1234')

        err_message_duplicated_username = '同じユーザー名が既に登録済みです。'
        duplicated_username = {
            'username': 'viewtester',
            'email': 'viewtester2@test.com',
            'password1': 'v1ewt3st3r1234',
            'password2': 'v1ewt3st3r1234',
        }
        response = self.client.post(reverse('authenticate:register'),
                                    duplicated_username,
                                    format='text/html')
        self.assertContains(response, err_message_duplicated_username)

        err_message_duplicated_email = 'この メールアドレス を持った ユーザー '\
            'が既に存在します。'
        duplicated_email = {
            'username': 'viewtester2',
            'email': 'viewtester@test.com',
            'password1': 'v1ewt3st3r1234',
            'password2': 'v1ewt3st3r1234',
        }
        response = self.client.post(reverse('authenticate:register'),
                                    duplicated_email,
                                    format='text/html')
        self.assertContains(response, err_message_duplicated_email)
