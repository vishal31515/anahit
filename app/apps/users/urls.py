from django.urls import path, include,re_path
from . import views


urlpatterns = (
    # urls for Customer
    path('logout/', views.logout_view, name='logout'),
    path('user_preference/', views.UserPreferenceView.as_view(), name='user_preference'),
    path('user_preference_create/', views.UserPreferenceCreateView.as_view(), name='user_preference_create'),
    path('user_preference_edit/<pk>/', views.UserPreferenceEditView.as_view(), name='user_preference_edit'),
    path('my_account/', views.MyAccount.as_view(), name='my_account'),
    path('checkusername/', views.checkUserNameAndEmail, name='checkusername'),
    path('update_card/', views.card_update, name='update_card'),
    path('invoice/history/', views.InvoiceHisotry.as_view(), name='invoice_history'),
    path('send_invoice_pdf/', views.SendInvoiceMailPDF.as_view(), name='send_invoice_pdf'),
    path('check_email_already_exists/', views.CheckEmailExists.as_view(), name='check_email_already_exists'),


)

