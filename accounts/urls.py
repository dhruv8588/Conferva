from django.urls import path
from . import views

urlpatterns = [
    path('registerUser/', views.registerUser, name='registerUser'),
    path('myAccount/', views.myAccount, name='myAccount'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]  
