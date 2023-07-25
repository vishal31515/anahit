import os
import random
from django.db import models
from django.utils.timezone import now
from users.models import User
from django.urls import reverse
from users.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils.text import slugify
from anahit.storage_backends import BlogMediaStorage



class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    class Meta:
        ordering = ["-created_at"]

    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True,blank=True)
    # thumbnail  = models.ImageField(upload_to='blog_thumbnails', blank=True, null=True)
    thumbnail  = models.ImageField(storage=BlogMediaStorage(), blank=True, null=True)
    body = models.TextField()
    meta_description = models.CharField(max_length=150, blank=True)
    date_modified = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    others = models.JSONField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def post_tags(self):
        tag_list = []
        tags = self.tags.all()
        for tag in tags:
            tag_list.append(str(tag))
        return tag_list

    @property
    def get_absolute_url(self):
        return reverse('blog_view', args=(self.slug,))

    def save(self, *args, **kwargs):
        num = random.randint(10,99)
        try:
            obj = Post.objects.latest('pk')
            self.slug = "%s"%(slugify(self.title + '-'+ str((obj.id+1) + num)))
            super(Post, self).save()
        except:
            self.slug = "%s"%(slugify(self.title + '-'+ str(1+num)))
            super(Post, self).save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User,related_name="commnet_user", null=True, on_delete=models.CASCADE)
    parent = models.ForeignKey('self' , null=True , blank=True , on_delete=models.CASCADE , related_name='replies')
    text = models.TextField()
    created_date = models.DateTimeField(default=now)
    approved = models.BooleanField(default=True)


    def approve(self):
        self.approved = True
        self.save()

    @property
    def children(self):
        return Comment.objects.filter(parent=self,approved=True).reverse()

    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False

    @property
    def comment_count(self):
        return Comment.objects.filter(approved=True).count()

    def __str__(self):
        return self.text


class Newsletter(models.Model):
    email = models.CharField(max_length=80, unique=True)
    send_alert = models.BooleanField(default=True)


    def __str__(self):
        return self.email