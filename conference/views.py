from datetime import date
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

# for submit paper
def delete_author(request, conference_id, paper_id, author_id):
    paper = get_object_or_404(Paper, id=paper_id)
    paper.authors.remove(author_id)

    author = get_object_or_404(Author, id=author_id)

    papers = Paper.objects.all()
    for paper in papers:
        if author in paper.authors.all():
            return redirect('submit_paper', conference_id, paper_id)

    author = get_object_or_404(Author, id=author_id)
    author.delete()
    return redirect('submit_paper', conference_id, paper_id)   
    

def edit_author(request, conference_id, paper_id, author_id):
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
                            return redirect('submit_paper', conference_id, paper_id)
                    if delete_orig == True:
                        orig.delete()
                        return redirect('submit_paper', conference_id, paper_id)        
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
                    return redirect('submit_paper', conference_id, paper_id)           
            else:
                orig.first_name = author.first_name #
                orig.last_name = author.last_name #
                orig.save() #
                return redirect('submit_paper', conference_id, paper_id)
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
    return render(request, 'conference/submit_paper.html', context)         

def add_author(request, conference_id, paper_id):
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
                    return redirect('submit_paper', conference_id, paper_id)
                
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

            return redirect('submit_paper', conference_id, paper_id)
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
    return render(request, 'conference/submit_paper.html', context)

@login_required(login_url='login')
def submit_paper(request, conference_id, paper_id=None):
    paper = get_object_or_404(Paper, id=paper_id) if paper_id else None

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

        
            if 'add_author' in request.POST:
                return redirect('add_author', conference_id, paper.id)
            elif 'submit_paper' in request.POST:
                file_hash = hashlib.md5(paper.file.read()).hexdigest() if paper.file else None
                title = paper.title
                abstract = paper.abstract
                authors = paper.authors.all()
                paper.file_hash = file_hash

                submitted_papers_with_same_file = Paper.objects.filter(Q(file_hash=file_hash) & ~Q(id=paper.id))
                if submitted_papers_with_same_file:
                    for submitted_paper in submitted_papers_with_same_file:
                        if submitted_paper.conferences.filter(id=conference_id):
                            messages.error(request, 'This paper has already been submitted to this conference!')
                            return redirect('submit_paper', conference_id, paper.id)
                
                conference = get_object_or_404(Conference, id=conference_id)
                conference.submitters.add(request.user.id)

                submitted_papers = Paper.objects.exclude(id=paper_id) 
                for submitted_paper in submitted_papers:
                    if submitted_paper.title.replace(" ", "").lower() == title.replace(" ", "").lower() and submitted_paper.abstract.replace(" ", "").lower() == abstract.replace(" ", "").lower() and set(submitted_paper.authors.all()) == set(authors) and submitted_paper.file_hash == file_hash:
                        if not submitted_paper.conferences.filter(id=conference_id):
                            submitted_paper.submitters.add(request.user.id)
                            submitted_paper.conferences.add(conference_id)
                            paper.delete()
                            messages.success(request, 'Paper submitted successfully!')
                            return redirect('myAccount')
                
                paper.submitters.add(request.user.id)
                paper.conferences.add(conference_id)
                paper.save() 
                messages.success(request, 'Paper submitted successfully!')
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
    return render(request, 'conference/submit_paper.html', context)


def withdraw_paper(request, conference_id, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    conferences = Conference.objects.exclude(id=conference_id)
    flag = 0
    for conference in conferences:
        if conference in paper.conferences.all():
            flag = 1
            break
    if flag == 0:
        authors = paper.authors.all()
        paper.delete()
        papers = Paper.objects.all()
        flag2 = 0
        for author in authors:
            if author in paper.authors.all():
                flag2 = 1
                break;
        if flag2==0:
            author.delete()
    else:
        paper.conferences.remove(conference_id)
    
        # submitters = paper.submitters.all()
        # for submitter in submitters:
        #     if submitter == request.user:
        #         break

        s = paper.submitters.get(request.user.id)
        print(s)
        flag3 = 0
        for submitter in paper.submitters:
            for conference in paper.conferences:  # .exclude(id=conference_id):
                if submitter in conference.submitters:
                    if submitter == s:
                        flag3 = 1
        if flag3 == 0:
            paper.submitters.remove(request.user.id)

        flag4 = 0
        papers = Paper.objects.exclude(id=paper_id)
        for paper in papers:
            if conference in paper.conferences.all():
                if request.user in paper.submitters:
                    flag4 = 1
        if flag4 == 0:
            conference.submitters.remove(request.user.id)

        return redirect('myAccount')


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




    