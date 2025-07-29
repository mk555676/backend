# transcribe/urls.py
from django.urls import path
from . import views
from .views import fetch_category_menu,add_to_cart
# ,initiate_payment,get_csrf_token

urlpatterns = [
    path('transcribe/', views.transcribe, name='transcribe'),
    path('api/transcribe/', views.transcribe, name='transcribe'),
    path('fetch-category-menu/', views.fetch_category_menu, name='fetch-category-menu'),
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    path('upload_profile_picture/', views.upload_profile_picture, name='upload_profile_picture'),
    path('facebook_data_deletion/', views.facebook_data_deletion, name='facebook_data_deletion'),
    #  path('initiate-payment/', initiate_payment, name='initiate_payment'),
    #  path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('create-stripe-checkout-session/', views.create_stripe_checkout_session, name='create_checkout_session'),
    path('payment/', views.JazzCashPaymentView.as_view(), name='jazzcash_payment'),
    path('callback/', views.JazzCashCallbackView.as_view(), name='jazzcash_callback'),
     path('register-voice/', views.process_voice_samples, name='register_voice'),
     path('authenticate-voice/', views.authenticate_voice, name='authenticate-voice'),
     path('check-enrollment-status/', views.check_enrollment_status_view, name='check_enrollment_status'),
     path("firebase-users/",  views.list_users, name="firebase_users"),
     path('success/', views.success_view, name='success'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe-webhook'),
     path('update-stock/', views.update_stock, name='update-stock'),
     path('create-payment-intent/', views.create_payment_intent, name='create-payment-intent'),
     path('verify-voice/', views.verify_voice_sample, name='verify_voice'),


   
   
]
