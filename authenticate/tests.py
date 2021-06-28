from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .models import User, Relation

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
