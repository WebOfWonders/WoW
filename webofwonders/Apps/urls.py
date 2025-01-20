from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/',views.register,name='register'),
    path('otp/', views.otp_verify, name='otp_verify'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),  # Add this line
    path('dashboard/',views.dashboard,name='dashboard'),
    path('login/',views.login,name='login'),
    path('weather/', views.weather, name='weather'),
    path('ocr/', views.ocr, name='ocr'),
    path('md5/', views.md5, name='md5'),
    path('nearby/', views.nearby, name='nearby'),
    path('download_video/', views.download_video, name='download_video'),
    path('downloadsuccess/', views.downloadsuccess, name='downloadsuccess'),
    path('timing/', views.timing, name='timing'),
    path('timer/', views.timer, name='timer'),
    path('stopwatch/', views.stopwatch, name='stopwatch'),
    path('international-time/', views.international_time, name='international_time'),
    path('shorten/', views.shorten_url, name='shorten_url'),
    path('<str:short_code>', views.redirect_url, name='redirect_url'),
]