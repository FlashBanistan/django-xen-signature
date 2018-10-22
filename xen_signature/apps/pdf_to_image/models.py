from django.db import models


class Document(models.Model):
    document_name = models.CharField(max_length=100)


class DocumentImage(models.Model):
    document = models.ForeignKey('pdf_to_image.Document', related_name='pages', on_delete=models.CASCADE)
    image = models.ImageField(height_field='image_height', width_field='image_width')
    image_height = models.PositiveIntegerField()
    image_width = models.PositiveIntegerField()
    page_no = models.PositiveSmallIntegerField(default=1)