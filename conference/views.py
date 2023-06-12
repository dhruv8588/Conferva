from datetime import date
import hashlib
import re
from django.forms import formset_factory, inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.defaultfilters import slugify
from django.db import models
from django.db.models import Q, Func, Value
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied

from accounts.models import User
from conference.models import Author, Conference, Paper
from .utils import send_approval_request_email

from .forms import AuthorForm, ConferenceForm, ConferenceModelFormset, PaperForm
from conference import forms

def check_role_admin(user):
    if user.is_admin == True:
        return True
    else:
        raise PermissionDenied

def get_user(request):
    user = Conference.objects.get(user=request.user)
    return user

@login_required(login_url='login')
def create_conference(request):
    if request.method == 'POST':
        form = ConferenceForm(request.POST)
        if form.is_valid():
            conference = form.save(commit=False)
            conference.creator = request.user 
            conference.save()

            mail_subject = 'Request for conference approval'
            email_template = 'accounts/emails/approval_request.html'
            send_approval_request_email(request, mail_subject, email_template)

            messages.success(request, 'Your conference has been registered sucessfully! Please wait for the approval.')
            return redirect('myAccount')
    else:
        form = ConferenceForm()
    context = {
        "form": form,
    }
    return render(request, 'conference/create_conference.html', context)

@login_required(login_url='login')
def conference_listing(request):
    conferences = Conference.objects.filter(is_approved=True).order_by('created_at')
    today = date.today()
    context = {
        "conferences": conferences,
        "today": today,
    }
    return render(request, 'conference/conference_listing.html', context)


# def add_author(request, conference_id):
#     if request.method == 'POST':
#         form = AuthorForm(request.POST)
#         if form.is_valid():
#             author = form.save()
#             return redirect('submit_paper', conference_id=conference_id, author_id=author.id)
#         else:
#             print(form.errors) 
#     else:
#         form = AuthorForm()

#     context = {
#         "form": form,
#         "conference_id" : conference_id,
#     }               
#     return render(request, 'conference/add_author.html', context)


# @login_required(login_url='login')
# def submit_paper(request, conference_id, author_id=None):
#     conference = get_object_or_404(Conference, id=conference_id)
#     author = get_object_or_404(Author, id=author_id) if author_id else None
#     if request.method == 'POST':
#         form = PaperForm(request.POST, request.FILES)
#         if form.is_valid():
#             # check whether the user who is submitting the paper in this conference has not submitted any other paper in this same conference
#             # if no then 
#             # if request.user not in conference.submitters:
#             conference.submitters.add(request.user.id)
#             print(conference.submitters)

#             title = form.cleaned_data['title']
#             abstract = form.cleaned_data['abstract']
#             file = request.FILES['file']
#             file_hash = hashlib .md5(file.read()).hexdigest()
               
#             # papers = Paper.objects.all()
#             # for paper in papers:
#             #     if paper.title.replace(" ", "").lower() == title.replace(" ", "").lower() and paper.abstract.replace(" ", "").lower() == abstract.replace(" ", "").lower() and paper.file_hash == file_hash:
#             #         if not paper.conferences.filter(id=conference_id):
#             #             paper.conferences.add(conference_id)
#             #             messages.success(request, 'Paper submitted successfully!')
#             #             return redirect('myAccount')

#             # papers_with_same_file = Paper.objects.filter(
#             #     Q(file_hash=file_hash)
#             # )
#             # if papers_with_same_file:
#             #     for paper in papers_with_same_file:
#             #         if paper.conferences.filter(id=conference_id):
#             #             messages.error(request, 'This paper has already been submitted to this conference!')
#             #             return redirect('submit_paper', conference_id)
                            
#             # papers = Paper.objects.all()
#             # for paper in papers:
#             #     if paper.title.replace(" ", "").lower() == title.replace(" ", "").lower():
#             #         if paper.conferences.filter(id=conference_id):
#             #             messages.error(request, 'A paper with the same title has already been submitted to this conference!')
#             #             return redirect('submit_paper', conference_id)
                    
#             paper = form.save(commit=False)
#             paper.submitter = request.user
#             paper.file_hash = file_hash
#             paper.save()
#             paper.conferences.add(conference_id)

#             # add_author(request, conference_id)
#             # paper.authors.add()
#             if author:
#                 paper.authors.add(author)

#             paper.save()
#             messages.success(request, 'Paper submitted successfully!')
#             return redirect('myAccount')
#         else:
#             print(form.errors)
#     else:
#         form = PaperForm()
    
#     context = {
#         "form": form,
#         "conference": conference,
#         "author": author,
#     }
#     return render(request, 'conference/submit_paper.html', context)

def add_author(request, conference_id):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save()
            return redirect('submit_paper', conference_id=conference_id, author_id=author.id, title=request.POST.get('title'), abstract=request.POST.get('abstract'))
        else:
            print(form.errors)
    else:
        form = AuthorForm()

    context = {
        "form": form,
        "conference_id": conference_id,
    }
    return render(request, 'conference/add_author.html', context)


def submit_paper(request, conference_id, author_id=None):
    conference = get_object_or_404(Conference, id=conference_id)
    author = get_object_or_404(Author, id=author_id) if author_id else None
    if request.method == 'POST':
        form = PaperForm(request.POST, request.FILES)
        if form.is_valid():
            conference.submitters.add(request.user.id)

            file = request.FILES['file']
            file_hash = hashlib.md5(file.read()).hexdigest()

            paper = form.save(commit=False)
            paper.submitter = request.user
            paper.file_hash = file_hash
            paper.save()
            paper.conferences.add(conference_id)

            if author:
                paper.authors.add(author)

            paper.save()
            messages.success(request, 'Paper submitted successfully!')
            return redirect('myAccount')
        else:
            print(form.errors)
    else:
        title = request.GET.get('title')
        abstract = request.GET.get('abstract')
        form = PaperForm(initial={'title': title, 'abstract': abstract})

    context = {
        "form": form,
        "conference": conference,
        "author": author,
        "title": title,
        "abstract": abstract,
    }
    return render(request, 'conference/submit_paper.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_admin)
def edit_is_approved(request):
    if request.method == 'POST':
        formset = ConferenceModelFormset(request.POST, queryset=Conference.objects.all())
        if formset.is_valid():
            # for form in formset:
            #     form.save()
            formset.save()  
            return redirect('myAccount')
        else:
            print(formset.errors)
    else:
        formset = ConferenceModelFormset(queryset = Conference.objects.all())

    context = {
        'formset': formset,
    }

    return render(request, 'conference/edit_is_approved.html', context)


def approve(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None    

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Approve/Disapprove conference')
        return redirect('edit_is_approved')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('myAccount')   




    