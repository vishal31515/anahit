from django.urls import path, include,re_path

from . import views


urlpatterns = (
    # urls for Price
    path('', views.PriceView.as_view(), name='price'),
)