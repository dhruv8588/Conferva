from django.urls import path

from . import views

urlpatterns = [
    path('create_conference/', views.create_conference, name='create_conference'),
    path('conference_listing/', views.conference_listing, name='conference_listing'),
    # path('submit_paper/<int:conference_id>/', views.submit_paper, name="submit_paper"),
    # path('submit_paper/<int:conference_id>/<int:author_id>/', views.submit_paper, name='submit_paper'),

    path('submit_paper/<int:conference_id>/<int:author_id>/', views.submit_paper, name='submit_paper'),
    path('submit_paper/<int:conference_id>/', views.submit_paper, name='submit_paper'),
    
    path('edit_is_approved/', views.edit_is_approved, name='edit_is_approved'),
    # path('add_author/', views.add_author, name='add_author'),
    path('conference/add_author/<int:conference_id>/', views.add_author, name='add_author'),

    

    path('approve/<uidb64>/<token>/', views.approve, name='approve'),

]
