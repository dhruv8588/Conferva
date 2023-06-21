from datetime import date
from datetime import datetime
import hashlib
from django.forms import formset_factory, inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.defaultfilters import slugify
from django.db.models import Q
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from django.urls import resolve
from django.utils.dateformat import DateFormat
from django.core.paginator import Paginator

from accounts.models import User
from conference.models import Author, Conference, Paper
# from .utils import send_approval_request_email

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
            # send_approval_request_email(request, mail_subject, email_template)

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

    # paginator = Paginator(conferences, 2)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)

    context = {
        "conferences": conferences,
        "today": today,
        # "page_obj": page_obj,
    }
    return render(request, 'conference/conference_listing.html', context)

def delete_author(request, conference_id, paper_id, author_id):
    url_name = resolve(request.path_info).url_name
    if url_name == 'delete_author':
        x = redirect('submit_paper', conference_id, paper_id)
    elif url_name == 'edit_paper_delete_author':
        x = redirect('edit_paper', conference_id, paper_id)

    paper = get_object_or_404(Paper, id=paper_id)
    paper.authors.remove(author_id)

    author = get_object_or_404(Author, id=author_id)

    papers = Paper.objects.all()
    for paper in papers:
        if author in paper.authors.all():
            return x

    author = get_object_or_404(Author, id=author_id)
    author.delete()
    return x
    

def edit_author(request, conference_id, paper_id, author_id):
    url_name = resolve(request.path_info).url_name
    if url_name == 'edit_author':
        x = redirect('submit_paper', conference_id, paper_id)
    elif url_name == 'edit_paper_edit_author':
        x = redirect('edit_paper', conference_id, paper_id)

    paper = get_object_or_404(Paper, id=paper_id)
    form = PaperForm(instance=paper)
    display_edit_author_model = True

    author = get_object_or_404(Author, id=author_id)
    if request.method == 'POST':
        aform = AuthorForm(request.POST, instance=author)
        if aform.is_valid():
            # code starts here
            entered_email = author.email.lower()
            orig = Author.objects.get(id=author_id)
            if entered_email != orig.email:
                flag = 0
                other_authors = Author.objects.exclude(id=orig.id)
                for other_author in other_authors:
                    if other_author.email == entered_email:
                        paper.authors.add(other_author.id)
                        other_author.first_name = author.first_name #
                        other_author.last_name = author.last_name #
                        other_author.save() #
                        paper.authors.remove(orig.id)
                        flag = 1
                if flag==1:
                    delete_orig = True
                    other_papers = Paper.objects.exclude(id=paper_id)
                    for other_paper in other_papers:
                        if orig in other_paper.authors.all():
                            delete_orig = False
                            return x
                    if delete_orig == True:
                        orig.delete()
                        return x     
                elif flag == 0:
                    flag2 = 0
                    other_papers = Paper.objects.exclude(id=paper_id)
                    for other_paper in other_papers:
                        if orig in other_paper.authors.all():
                            paper.authors.remove(orig.id)
                            # create a new author object with a different id and the field values of author object
                            new_author = Author.objects.create(
                                first_name = author.first_name,
                                last_name = author.last_name,
                                email = author.email
                            )
                            users = User.objects.all()
                            for user in users:
                                if user.email == new_author.email:
                                    new_author.user = user
                                    break
                            new_author.save()
                            paper.authors.add(new_author.id)
                            flag2 = 1
                    if flag2 == 0:
                        author.save()
                    return x          
            else:
                orig.first_name = author.first_name #
                orig.last_name = author.last_name #
                orig.save() #
                return x
        else:
            print(aform.errors)
    else:
        aform = AuthorForm(instance=author)

    context = {
        "aform": aform,
        "display_edit_author_model": display_edit_author_model,
        "form": form,
        "conference_id": conference_id,
        "paper": paper,
        "author_id": author_id,
    }
    if url_name == 'edit_author':
        y = render(request, 'conference/submit_paper.html', context)
    elif url_name == 'edit_paper_edit_author': 
        y = render(request, 'conference/edit_paper.html', context)
    return y       

def add_author(request, conference_id, paper_id):
    url_name = resolve(request.path_info).url_name
    if url_name == 'add_author':
        x = redirect('submit_paper', conference_id, paper_id)
    elif url_name == 'edit_paper_add_author':    
        x = redirect('edit_paper', conference_id, paper_id)
        
    paper = get_object_or_404(Paper, id=paper_id)
    form = PaperForm(instance=paper)
    display_add_author_model = True 
    if request.method == 'POST':
        aform = AuthorForm(request.POST)
        if aform.is_valid(): 
            email = aform.cleaned_data['email'].lower()
            authors = Author.objects.all()
            for author in authors:
                if author.email == email:
                    paper.authors.add(author.id)
                    author.first_name = aform.cleaned_data['first_name'] #
                    author.last_name = aform.cleaned_data['last_name'] #
                    author.save() #
                    # paper.save()
                    # return redirect('submit_paper', conference_id, paper_id)
                    return x
                
            author = aform.save(commit=False)
            users = User.objects.all()
            for user in users:
                if user.email == email:
                    author.user = user
                    break
            author.email = email
            aform.save()

            paper.authors.add(author.id)
            # paper.save()

            # return redirect('submit_paper', conference_id, paper_id)
            return x
        else:
            print(aform.errors)
    else:
        aform = AuthorForm()
              
    context = {
        "aform": aform,
        "display_add_author_model": display_add_author_model,
        "form": form,
        "conference_id": conference_id,
        "paper": paper,
    }
    if url_name == 'add_author':
        y = render(request, 'conference/submit_paper.html', context)
    elif url_name == 'edit_paper_add_author': 
        y = render(request, 'conference/edit_paper.html', context)
    return y

@login_required(login_url='login')
def submit_paper(request, conference_id, paper_id=None, author_id=None):
    paper = get_object_or_404(Paper, id=paper_id) if paper_id else None
    conference = get_object_or_404(Conference, id=conference_id)
    url_name = resolve(request.path_info).url_name

    if request.method == 'POST':
        form = PaperForm(request.POST, request.FILES, instance=paper)
        paper = form.save()   
        if form.is_valid():
            is_submitter_author = form.cleaned_data['is_submitter_author']
            if is_submitter_author == True:
                authors = Author.objects.all()
                flag = 0
                for author in authors:
                    if author.user == request.user:
                        paper.authors.add(author.id)
                        flag = 1
                        break 
                if flag==0:    
                    new_author = Author.objects.create(
                                        first_name = request.user.first_name,
                                        last_name = request.user.last_name,
                                        email = request.user.email,
                                        user = request.user,
                                    )
                    new_author.save()
                    paper.authors.add(new_author.id) 
            else:
                authors = Author.objects.all()
                for author in authors:
                    if author.user == request.user:
                        if author in paper.authors.all():
                            paper.authors.remove(author.id)
                            break

            paper.submitter = request.user
            paper.conference = conference
            paper.save()

            action = request.GET.get('action')
            if action == 'edit_author':
                return redirect('edit_author', conference_id, paper.id, author_id)
            elif action == 'delete_author':
                return redirect('delete_author', conference_id, paper.id, author_id)
            elif 'add_author' in request.POST:
                return redirect('add_author', conference_id, paper.id)
            elif 'edit_paper_add_author' in request.POST:
                return redirect('edit_paper_add_author', conference_id, paper.id)
            # elif 'edit_paper_edit_author' in request.POST:
            #     return redirect('edit_paper_edit_author', conference_id, paper.id, author_id)
            elif 'submit_paper' in request.POST:
                file_hash = hashlib.md5(paper.file.read()).hexdigest() if paper.file else None
                paper.file_hash = file_hash
                paper.save()

                if file_hash:
                    submitted_papers_with_same_file = Paper.objects.filter(Q(file_hash=file_hash) & ~Q(id=paper.id))
                    if submitted_papers_with_same_file:
                        for submitted_paper in submitted_papers_with_same_file:
                            if submitted_paper.conference==conference:
                                messages.error(request, 'This paper has already been submitted to this conference!')
                                return redirect('submit_paper', conference_id, paper.id)

                if url_name == 'submit_paper':
                    messages.success(request, 'Paper submitted successfully!')
                elif url_name == 'edit_paper':
                    messages.success(request, 'Paper edited successfully!')
                return redirect('myAccount')
        else:
            print(form.errors)         
    else:
        form = PaperForm(instance=paper)
    context = {
        "form": form,
        "conference_id": conference_id,
        "paper": paper,
    }
    if url_name == 'submit_paper':
        return render(request, 'conference/submit_paper.html', context)
    elif url_name == 'edit_paper':
        return render(request, 'conference/edit_paper.html', context)


def withdraw_paper(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    authors = paper.authors.all()
    papers = Paper.objects.exclude(id=paper_id)
    flag = 0
    for author in authors:
        for paper in papers:
            if author in paper.authors.all():
                flag = 1
                break
        if flag == 0:
            author.delete()
      
    paper.delete()
    messages.success(request, 'Paper has been deleted successfully!')            
    return redirect('myAccount')


@login_required(login_url='login')
@user_passes_test(check_role_admin)
def edit_is_approved(request):
    if request.method == 'POST':
        formset = ConferenceModelFormset(request.POST, queryset=Conference.objects.all())
        # flag = 0
        # for form in formset:
        #     if not form.is_valid():
        #         flag = 1
        # if flag==0:
        #     for form in formset:
        #         form.save()
        if formset.is_valid():    
            formset.save()  
            return redirect('myAccount')
        else:
            print(formset.errors)
    else:
        formset = ConferenceModelFormset(queryset = Conference.objects.all())

    for form in formset:
        form.instance.start_date = DateFormat(form.instance.start_date).format('Y-m-d')
        form.instance.end_date = DateFormat(form.instance.end_date).format('Y-m-d')
        form.instance.submission_deadline = DateFormat(form.instance.submission_deadline).format('Y-m-d')
    context = {
        'formset': formset,
    }
    return render(request, 'conference/edit_is_approved.html', context)


# def approve(request, uidb64, token):
#     try:
#         uid = urlsafe_base64_decode(uidb64).decode()
#         user = User._default_manager.get(pk=uid)
#     except(TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None    

#     if user is not None and default_token_generator.check_token(user, token):
#         request.session['uid'] = uid
#         messages.info(request, 'Approve/Disapprove conference')
#         return redirect('edit_is_approved')
#     else:
#         messages.error(request, 'This link has been expired!')
#         return redirect('myAccount')   




    