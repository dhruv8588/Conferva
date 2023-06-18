from django.urls import path

from . import views

urlpatterns = [
    path('create_conference/', views.create_conference, name='create_conference'),
    path('conference_listing/', views.conference_listing, name='conference_listing'),
    
    path('<int:conference_id>/submit_paper/<int:paper_id>/', views.submit_paper, name='submit_paper'),
    path('<int:conference_id>/submit_paper/', views.submit_paper, name='submit_paper'),

    path('<int:conference_id>/submit_paper/<int:paper_id>/add_author/', views.add_author, name='add_author'),
    path('<int:conference_id>/submit_paper/<int:paper_id>/edit_author/<int:author_id>/', views.edit_author, name='edit_author'),
    path('<int:conference_id>/submit_paper/<int:paper_id>/delete_author/<int:author_id>/', views.delete_author, name='delete_author'),

    path('edit_is_approved/', views.edit_is_approved, name='edit_is_approved'),
    
    path('approve/<uidb64>/<token>/', views.approve, name='approve'),

]
