from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.myAccount),
    path('register_user/', views.registerUser, name='register_user'),
    path('edit_profile/<int:user_id>/', views.edit_profile, name='edit_profile'),

    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    
    path('myAccount/', views.myAccount, name='myAccount'),

    path('guestDashboard/', views.guestDashboard, name="guestDashboard"),
    path('adminDashboard/', views.adminDashboard, name="adminDashboard"),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/', views.reset_password, name='reset_password'),

    path('conference/', include('conference.urls')),

    path('registerUser/deleteResearchArea/<int:pk>/', views.delete_research_area, name="delete_research_area"),
]  
