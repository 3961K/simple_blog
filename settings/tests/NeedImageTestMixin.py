from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image


class NeedImageTestMixin():
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
