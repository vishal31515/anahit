from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from upload.views import image_upload
from anahit.views import Homepage, AboutUs, ContactUs, ThankYou, ChangeTheme, LinkExpiredView

urlpatterns = [
    #path("", image_upload, name="upload"),
    path('', Homepage.as_view(), name='home'),
    path('about_us', AboutUs.as_view(), name='about_us'),
    path('contact_us', ContactUs.as_view(), name='contact_us'),
    path('users/', include('users.urls')),
    path('sub/', include('subscription.urls'), name="subscription"),
    path('blog/', include('blog.urls'), name="blog"),
    path('services/', include('services.urls'), name="services"),
    path('price/', include('price.urls'), name="price"),
    path('accounts/', include('allauth.urls'), name="accounts"),
    path("admin/", admin.site.urls, name="admin"),
    path('summernote/', include('django_summernote.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path("thankyou", ThankYou.as_view(), name="thankyou"),
    path("change_theme", ChangeTheme.as_view(), name="change_theme"),
    path('notification/', include('notifications.urls'), name="notification"),
    path('user/', include('magiclink.urls'), name='magiclink'),
    path('link-expired/',   LinkExpiredView.as_view(), name='link-expired'),

        
]

if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
