from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from .views import manage_budget

urlpatterns = [
    path('', landing_page, name='landing'),
    path('register/', register, name='register'),
    path('verify-email/', verify_email, name='verify_email'),
    path('submit-contact/', submit_contact, name='submit_contact'),
    path('thank-you/', thank_you, name='thank_you'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/', reset_password , name='reset_password'),
    path('dashboard/', dashboard, name='dashboard'),
    path('settings/', settings_view, name='settings'),
    path('add_transaction/', add_transaction, name="add_transaction"),
    path('transactions/', transaction_list, name="transactions"),
    path('transactions/edit/<int:transaction_id>/', edit_transaction, name='edit_transaction'),
    path('transactions/delete/<int:transaction_id>/', delete_transaction, name='delete_transaction'),
    path('filter_transactions/', filter_transactions, name='filter_transactions'),
    path('market/', market_dashboard, name='market'),
    path('manage-budget/',manage_budget, name='manage_budget'),
    path('set-budget/',add_budget,name='add_budget'),
    path('chatbot/', chatbot_view, name='chatbot'),
    path('stock/<str:symbol>/', stock_detail, name='stock_detail'),
    path('search/', search_results, name='search_results'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
