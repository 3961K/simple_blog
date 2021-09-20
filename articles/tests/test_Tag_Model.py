from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from ..models import Tag

# Create your tests here.

User = get_user_model()


class TagTest(TestCase):
    # タグを追加する事が出来る
    def test_success_create_tag(self):
        Tag.objects.create(tag='test')
        tag = Tag.objects.get(tag='test')
        self.assertIsNotNone(tag)

    # タグを削除する事が出来る
    def test_success_delete_tag(self):
        Tag.objects.create(tag='test2')
        tag = Tag.objects.get(tag='test2')
        self.assertIsNotNone(tag)

        tag.delete()
        with self.assertRaises(ObjectDoesNotExist):
            Tag.objects.get(tag='test2')
