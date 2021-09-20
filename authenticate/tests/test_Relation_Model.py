from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.test import TestCase

from ..models import User, Relation


class RelationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(username='relation_follower',
                            email='relation_follower@test.com',
                            password='password1234')
        User.objects.create(username='relation_followee',
                            email='relation_followee@test.com',
                            password='password1234')

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
