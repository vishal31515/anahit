from django.urls import path, include,re_path

from . import views

urlpatterns = (
    # urls for Blog
    path('blog-search/', views.BlogSearchView.as_view(), name='blog-search'),
    path('', views.BlogHome.as_view(), name='blog_home'),
    path('<str:blog_slug>/', views.BlogView, name='blog_view'),
)