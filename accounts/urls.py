from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.myAccount),
    path('registerAuthor/', views.registerAuthor, name='registerAuthor'),
    path('registerEditor/', views.registerEditor, name='registerEditor'),
    path('edit_profile/<int:user_id>/', views.edit_profile, name='edit_profile'),

    path('loginAuthor/', views.loginAuthor, name="loginAuthor"),
    path('loginEditor/', views.loginEditor, name="loginEditor"),
    path('loginAdmin/', views.loginAdmin, name="loginAdmin"),
    path('logout/', views.logout, name="logout"),
    
    path('myAccount/', views.myAccount, name='myAccount'),

    path('authorDashboard/', views.authorDashboard, name="authorDashboard"),
    path('editorDashboard/', views.editorDashboard, name="editorDashboard"),
    path('adminDashboard/', views.adminDashboard, name="adminDashboard"),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    path('forgot_password/', views.forgot_password, name='forgot_password'),
    # path('author/forgot_password/', views.forgot_password, name='forgot_password_author'),
    # path('admin/forgot_password/', views.forgot_password, name='forgot_password_admin'),

    path('reset_password/', views.reset_password, name='reset_password'),

    path('conference/', include('conference.urls')),
    path('paper/', include('paper.urls')),

    path('registerUser/deleteResearchArea/<int:pk>/', views.delete_research_area, name="delete_research_area"),
]  
