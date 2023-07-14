from django.urls import path

from . import views

urlpatterns = [
    # urls for conference
    path('create_conference/<int:conference_id>/<int:editor_id>/', views.create_conference, name='create_conference'),
    path('create_conference/<int:conference_id>/', views.create_conference, name='create_conference'),
    path('create_conference/', views.create_conference, name='create_conference'),

    path('edit_conference/<int:conference_id>/<int:editor_id>/', views.create_conference, name='edit_conference'),
    path('edit_conference/<int:conference_id>/', views.create_conference, name='edit_conference'),

    path('delete_conference/<int:conference_id>/', views.delete_conference, name='delete_conference'),
    
    path('conference_listing/', views.conference_listing, name='conference_listing'),
    
    # urls for editor
    path('create_conference/<int:conference_id>/add_editor/', views.add_editor, name='add_editor'),
    path('create_conference/<int:conference_id>/edit_editor/<int:editor_id>/', views.edit_editor, name='edit_editor'),
    path('create_conference/<int:conference_id>/delete_editor/<int:editor_id>/', views.delete_editor, name='delete_editor'),

    path('edit_conference/<int:conference_id>/add_editor/', views.add_editor, name='edit_conference_add_editor'),
    path('edit_conference/<int:conference_id>/edit_editor/<int:editor_id>/', views.edit_editor, name='edit_conference_edit_editor'),
    path('edit_conference/<int:conference_id>/delete_editor/<int:editor_id>/', views.delete_editor, name='edit_conference_delete_editor'),

    # urls for paper
    path('<int:conference_id>/submit_paper/<int:paper_id>/<int:author_id>/', views.submit_paper, name='submit_paper'),
    path('<int:conference_id>/submit_paper/<int:paper_id>/', views.submit_paper, name='submit_paper'),
    path('<int:conference_id>/submit_paper/', views.submit_paper, name='submit_paper'),

    path('<int:conference_id>/edit_paper/<int:paper_id>/<int:author_id>/', views.submit_paper, name='edit_paper'),
    path('<int:conference_id>/edit_paper/<int:paper_id>/', views.submit_paper, name='edit_paper'),

    path('withdraw_paper/<int:paper_id>/', views.withdraw_paper, name='withdraw_paper'),

    # urls for author
    path('<int:conference_id>/submit_paper/<int:paper_id>/add_author/', views.add_author, name='add_author'),
    path('<int:conference_id>/submit_paper/<int:paper_id>/edit_author/<int:author_id>/', views.edit_author, name='edit_author'),
    path('<int:conference_id>/submit_paper/<int:paper_id>/delete_author/<int:author_id>/', views.delete_author, name='delete_author'),

    path('<int:conference_id>/edit_paper/<int:paper_id>/add_author/', views.add_author, name='edit_paper_add_author'),
    path('<int:conference_id>/edit_paper/<int:paper_id>/edit_author/<int:author_id>/', views.edit_author, name='edit_paper_edit_author'),
    path('<int:conference_id>/edit_paper/<int:paper_id>/delete_author/<int:author_id>/', views.delete_author, name='edit_paper_delete_author'),


    path('edit_is_approved/', views.edit_is_approved, name='edit_is_approved'),

    path('<int:conference_id>/view_papers/', views.view_papers, name='view_papers'),
    path('<int:conference_id>/paper/<int:paper_id>/add_reviewer/', views.add_reviewer, name='add_reviewer'),
    path('<int:conference_id>/paper/<int:paper_id>/add_new_reviewer/', views.add_new_reviewer, name='add_new_reviewer'),
    path('<int:conference_id>/paper/<int:paper_id>/edit_reviewer/<int:reviewer_id>/', views.edit_reviewer, name='edit_reviewer'),
    path('<int:conference_id>/paper/<int:paper_id>/delete_reviewer/<int:reviewer_id>/', views.delete_reviewer, name='delete_reviewer'),
    path('<int:conference_id>/paper/<int:paper_id>/reviewer/<int:reviewer_id>/', views.reviewer_info, name='reviewer_info'),
    # path('approve/<uidb64>/<token>/', views.approve, name='approve'),
    path('review/<uidb64>/<token>/', views.review, name='review'),



    path('paper/<int:paper_id>/accept_or_decline_to_review/', views.accept_or_decline_to_review, name='accept_or_decline_to_review'),
    path('paper/<int:paper_id>/review', views.review, name='review'),
    path('paper/<int:paper_id>/decline_to_review/', views.decline_to_review, name='decline_to_review'),
    path('paper/<int:paper_id>/delete_review/', views.delete_review, name='delete_review')

]

