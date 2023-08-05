from django.urls import path

from . import views

urlpatterns = [
    # urls for paper
    path('<int:paper_id>/submit/conference/<int:conference_id>/author/<int:author_id>/', views.submit_paper, name='submit_paper'),
    path('<int:paper_id>/submit/conference/<int:conference_id>/', views.submit_paper, name='submit_paper'),
    path('submit/conference/<int:conference_id>', views.submit_paper, name='submit_paper'),

    path('<int:paper_id>/edit/conference/<int:conference_id>/author/<int:author_id>/', views.submit_paper, name='edit_paper'),
    path('<int:paper_id>/edit/conference/<int:conference_id>/', views.submit_paper, name='edit_paper'),

    path('<int:paper_id>/delete/', views.delete_paper, name='delete_paper'),

    # urls for author 
    path('<int:paper_id>/submit/conference/<int:conference_id>/add_author/', views.add_author, name='add_author'),
    path('<int:paper_id>/submit/conference/<int:conference_id>/edit_author/<int:author_id>/', views.edit_author, name='edit_author'),
    path('<int:paper_id>/submit/conference/<int:conference_id>/delete_author/<int:author_id>/', views.delete_author, name='delete_author'),

    path('<int:paper_id>/edit/conference/<int:conference_id>/add_author/', views.add_author, name='edit_paper_add_author'),
    path('<int:paper_id>/edit/conference/<int:conference_id>/edit_author/<int:author_id>/', views.edit_author, name='edit_paper_edit_author'),
    path('<int:paper_id>/edit/conference/<int:conference_id>/delete_author/<int:author_id>/', views.delete_author, name='edit_paper_delete_author'),

    # urls for reviewer
    path('<int:paper_id>/accept_or_decline_to_review/', views.accept_or_decline_to_review, name='accept_or_decline_to_review'),
    path('<int:paper_id>/review', views.review, name='review'),
    path('<int:paper_id>/decline_to_review/', views.decline_to_review, name='decline_to_review'),
    path('<int:paper_id>/delete_review/', views.delete_review, name='delete_review')
]    