from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from ckeditor_uploader.widgets import  CKEditorUploadingWidget
from django import forms
from . models import  Tag, Post, Comment, Newsletter

class PostAdminForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorUploadingWidget())
    class Meta:
        model = Post
        fields = '__all__'

class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm

admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Newsletter)
