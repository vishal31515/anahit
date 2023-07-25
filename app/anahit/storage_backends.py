from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = settings.AWS_USER_AVATAR_MEDIA_LOCATION
    file_overwrite = False

class BlogMediaStorage(S3Boto3Storage):
    location = settings.AWS_BLOG_MEDIA_LOCATION
    file_overwrite = False

class ServiceMediaStorage(S3Boto3Storage):
    location = settings.AWS_SERVICE_MEDIA_LOCATION
    file_overwrite = False
