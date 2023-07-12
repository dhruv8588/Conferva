from datetime import date
from datetime import datetime
import hashlib

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
from conference.models import Author, Conference, Keywords, Paper, Reviewer
from conference.utils import send_review_invitation
# from .utils import send_approval_request_email

from .forms import AuthorForm, ConferenceForm, ConferenceModelFormset, KeywordsFormSet, PaperForm, ReviewerForm, UserModelFormset
from conference import forms

def check_role_admin(user):
    if user.is_admin == True:
        return True
    else:
        raise PermissionDenied

def get_user(request):
    user = Conference.objects.get(user=request.user)
    return user

def edit_conference(request, conference_id):
    conference = Conference.objects.get(id=conference_id)
    if request.method == 'POST':
        form = ConferenceForm(request.POST, instance=conference)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conference updated successfully!')
            return redirect('myAccount')
        else:
            print(form.errors)
    else:
        form = ConferenceForm(instance=conference)
    context = {
        "form": form,
        'conference_id': conference_id,
    }                
    return render(request, 'conference/edit_conference.html', context)

def delete_conference(request, conference_id):
    papers = Paper.objects.filter(conference=conference_id)
    for paper in papers:
        ps = Paper.objects.exclude(id=paper.id)

        authors = paper.authors.all()
        flag = 0
        for author in authors:
            for p in ps:
                if author in p.authors.all():
                    flag = 1
                    break
            if flag == 0:
                author.delete()
        
        reviewers = paper.reviewers.all()
        flag = 0
        for reviewer in reviewers:
            for p in ps:
                if reviewer in p.reviewers.all():
                    flag = 1
                    break
            if flag == 0:
                reviewer.delete()    

        paper.delete()

    conference = Conference.objects.get(id=conference_id)
    conference.delete()
    messages.success(request, 'Conference has been deleted successfully!')    

    return redirect('myAccount')

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

    paginator = Paginator(conferences, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "conferences": conferences,
        "today": today,
        "page_obj": page_obj,
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
    display_edit_author_modal = True

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
        formset = KeywordsFormSet(prefix='keywords', instance=paper)
        

    context = {
        "aform": aform,
        "display_edit_author_modal": display_edit_author_modal,
        "form": form,
        "conference_id": conference_id,
        "paper": paper,
        "author_id": author_id,
        "formset": formset,
    }
    if url_name == 'edit_author':
        y = render(request, 'conference/edit_author.html', context)
    elif url_name == 'edit_paper_edit_author': 
        y = render(request, 'conference/edit_paper_edit_author.html', context)
    return y       

def add_author(request, conference_id, paper_id):
    url_name = resolve(request.path_info).url_name
    if url_name == 'add_author':
        x = redirect('submit_paper', conference_id, paper_id)
    elif url_name == 'edit_paper_add_author':    
        x = redirect('edit_paper', conference_id, paper_id)
        
    paper = get_object_or_404(Paper, id=paper_id)
    form = PaperForm(instance=paper)
    display_add_author_modal = True 
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
        formset = KeywordsFormSet(prefix='keywords', instance=paper)
              
    context = {
        "aform": aform,
        "display_add_author_modal": display_add_author_modal,
        "form": form,
        "conference_id": conference_id,
        "paper": paper,
        "formset": formset
    }
    if url_name == 'add_author':
        y = render(request, 'conference/add_author.html', context)
    elif url_name == 'edit_paper_add_author': 
        y = render(request, 'conference/edit_paper_add_author.html', context)
    return y

@login_required(login_url='login')
def submit_paper(request, conference_id, paper_id=None, author_id=None):
    paper = get_object_or_404(Paper, id=paper_id) if paper_id else None
    conference = get_object_or_404(Conference, id=conference_id)
    url_name = resolve(request.path_info).url_name

    if request.method == 'POST':
        form = PaperForm(request.POST, request.FILES, instance=paper)
        formset = KeywordsFormSet(request.POST, prefix='keywords', instance=paper)
        paper = form.save()   
        if form.is_valid() and formset.is_valid():
            for kform in formset:
                keyword = kform.save(commit=False)
                if keyword.name != '':
                    keyword.paper = paper
                    keyword.save()
                elif keyword.name == '' and kform.instance.id:
                    kform.instance.delete()    

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

                            flag = 0
                            papers = Paper.objects.exclude(id=paper.id)
                            for paper in papers:
                                if author in paper.authors.all():
                                       flag = 1 
                            if flag == 0:
                                author.delete()           
                            break

            paper.submitter = request.user
            paper.conference = conference
            paper.save()
            action = request.GET.get('action')
            if action == 'edit_author': # submit paper
                return redirect('edit_author', conference_id, paper.id, author_id)
            elif action == 'delete_author': # submit paper
                return redirect('delete_author', conference_id, paper.id, author_id)
            elif action == 'edit_paper_edit_author':
                return redirect('edit_paper_edit_author', conference_id, paper.id, author_id)
            elif action == 'edit_paper_delete_author':
                return redirect('edit_paper_delete_author', conference_id, paper.id, author_id)
            
            if 'add_author' in request.POST: # submit paper
                return redirect('add_author', conference_id, paper.id)
            elif 'edit_paper_add_author' in request.POST:
                return redirect('edit_paper_add_author', conference_id, paper.id)
            elif 'edit_paper' in request.POST:
                return redirect('edit_paper', conference_id, paper.id)
            elif 'submit_paper' in request.POST: # submit paper
                file_hash = hashlib.md5(paper.file.read()).hexdigest() if paper.file else None
                if file_hash:
                    submitted_papers_with_same_file = Paper.objects.filter(Q(file_hash=file_hash) & ~Q(id=paper.id))
                    if submitted_papers_with_same_file:
                        for submitted_paper in submitted_papers_with_same_file:
                            if submitted_paper.conference==conference:
                                paper.file = None
                                paper.save()
                                messages.error(request, 'This paper has already been submitted to this conference!')
                                if url_name == 'submit_paper':
                                    return redirect('submit_paper', conference_id, paper.id)
                                elif url_name == 'edit_paper':
                                    return redirect('edit_paper', conference_id, paper.id)
                paper.file_hash = file_hash               
                paper.save()

            if url_name == 'submit_paper':        
                messages.success(request, 'Paper submitted successfully!')
            elif url_name == 'edit_paper':
                messages.success(request, 'Paper edited successfully!')
            return redirect('myAccount')
        else:
            print(form.errors)  
            print(formset.errors)       
    else:
        form = PaperForm(instance=paper)
        formset = KeywordsFormSet(prefix='keywords', instance=paper)
    context = {
        "form": form,
        "conference_id": conference_id,
        "paper": paper,
        "formset": formset
    }
    if url_name == 'submit_paper':
        return render(request, 'conference/submit_paper.html', context)
    elif url_name == 'edit_paper':
        return render(request, 'conference/edit_paper.html', context)


def withdraw_paper(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    papers = Paper.objects.exclude(id=paper_id)

    authors = paper.authors.all()
    flag = 0
    for author in authors:
        for paper in papers:
            if author in paper.authors.all():
                flag = 1
                break
        if flag == 0:
            author.delete()
      
    reviewers = paper.reviewers.all()
    flag = 0
    for reviewer in reviewers:
        for paper in papers:
            if reviewer in paper.reviewers.all():
                flag = 1
                break
        if flag == 0:
            reviewer.delete()    

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

def view_papers(request, conference_id):
    papers = Paper.objects.filter(conference=conference_id).order_by('created_at')
    conference = Conference.objects.get(id = conference_id)
    context = {
        "papers": papers,
        "conference": conference,
    } 
    return render(request, 'conference/view_papers.html', context)

def edit_reviewer(request, conference_id, paper_id, reviewer_id):
    papers = Paper.objects.filter(conference=conference_id).order_by('created_at')
    conference = Conference.objects.get(id = conference_id)
    
    target_paper = Paper.objects.get(id=paper_id)
    display_edit_reviewer_modal = True

    reviewer = get_object_or_404(Reviewer, id=reviewer_id)
    if request.method == 'POST':
        form = ReviewerForm(request.POST, instance=reviewer)
        if form.is_valid():
            # code starts here
            entered_email = reviewer.email.lower()
            orig = Reviewer.objects.get(id=reviewer_id)
            if entered_email != orig.email:
                flag = 0
                other_reviewers = Reviewer.objects.exclude(id=orig.id)
                for other_reviewer in other_reviewers:
                    if other_reviewer.email == entered_email:
                        target_paper.reviewers.add(other_reviewer.id)
                        other_reviewer.first_name = reviewer.first_name #
                        other_reviewer.last_name = reviewer.last_name #
                        other_reviewer.save() #
                        target_paper.reviewers.remove(orig.id)
                        flag = 1
                if flag==1:
                    delete_orig = True
                    other_papers = Paper.objects.exclude(id=paper_id)
                    for other_paper in other_papers:
                        if orig in other_paper.reviewers.all():
                            delete_orig = False
                            return redirect('view_papers', conference_id)
                    if delete_orig == True:
                        orig.delete()
                        return redirect('view_papers', conference_id)  
                elif flag == 0:
                    flag2 = 0
                    other_papers = Paper.objects.exclude(id=paper_id)
                    for other_paper in other_papers:
                        if orig in other_paper.reviewers.all():
                            target_paper.reviewers.remove(orig.id)
                            # create a new reviewer object with a different id and the field values of reviewer object
                            new_reviewer = Reviewer.objects.create(
                                first_name = reviewer.first_name,
                                last_name = reviewer.last_name,
                                email = reviewer.email
                            )
                            users = User.objects.all()
                            for user in users:
                                if user.email == new_reviewer.email:
                                    new_reviewer.user = user
                                    break
                            new_reviewer.save()
                            target_paper.reviewers.add(new_reviewer.id)
                            flag2 = 1
                    if flag2 == 0:
                        reviewer.save()
                    return redirect('view_papers', conference_id)          
            else:
                orig.first_name = reviewer.first_name #
                orig.last_name = reviewer.last_name #
                orig.save() #
                return redirect('view_papers', conference_id)
        else:
            print(form.errors)
    else:
        form = ReviewerForm(instance=reviewer)
    context = {
        'papers': papers,
        'conference': conference,
        'form': form,
        'target_paper': target_paper,
        'display_edit_reviewer_modal': display_edit_reviewer_modal,
        'reviewer_id': reviewer_id
    }
    return render(request, 'conference/view_papers.html', context)       


def add_new_reviewer(request, conference_id, paper_id):
    papers = Paper.objects.filter(conference=conference_id).order_by('created_at')
    paper = Paper.objects.get(id=paper_id)
    conference = Conference.objects.get(id = conference_id)
    display_add_new_reviewer_modal = True
    if request.method == 'POST':
        form = ReviewerForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            reviewers = Reviewer.objects.all()
            for reviewer in reviewers:
                if reviewer.email == email:
                    paper.reviewers.add(reviewer.id)

                    # email_template = 'accounts/emails/review_invitation.html'
                    # send_review_invitation(request, reviewer.user, email_template)

                    reviewer.first_name = form.cleaned_data['first_name'] #
                    reviewer.last_name = form.cleaned_data['last_name'] #
                    reviewer.save() #

                    return redirect('view_papers', conference_id)
                
            reviewer = form.save(commit=False)
            users = User.objects.all()
            for user in users:
                if user.email == email:
                    reviewer.user = user
                    break
            reviewer.email = email
            form.save()

            paper.reviewers.add(reviewer.id)
            # email_template = 'accounts/emails/review_invitation.html'
            # send_review_invitation(request, reviewer.user, email_template)

            return redirect('view_papers', conference_id)
        else:
            print(form.errors)        
    else:
        form = ReviewerForm()
    context = {
        'form': form,
        'paper': paper,
        'papers': papers,
        'display_add_new_reviewer_modal': display_add_new_reviewer_modal,
        'conference': conference,
    }
    return render(request, 'conference/view_papers.html', context)       

def add_reviewer(request, conference_id, paper_id):
    papers = Paper.objects.filter(conference=conference_id).order_by('created_at')
    paper = Paper.objects.get(id=paper_id)
    display_add_reviewer_modal = True
    conference = Conference.objects.get(id = conference_id)
    if request.method == 'POST':
        formset = UserModelFormset(request.POST)
        
        for form in formset:
            user = form.save(commit=False)
            is_invited = form.cleaned_data.get('is_invited')

            flag = 0
            if is_invited == True:
                reviewers = Reviewer.objects.all()
                for reviewer in reviewers:
                    if reviewer.user == user:
                        paper.reviewers.add(reviewer.id)
                        flag = 1
                if flag == 0:
                    reviewer = Reviewer.objects.create(user=user, first_name=user.first_name, last_name=user.last_name, email=user.email)
                    reviewer.save()
                    paper.reviewers.add(reviewer)  
                
        return redirect('view_papers', conference_id)
    else:
        # id_list = []
        # reviewers = paper.reviewers.all()
        # for reviewer in reviewers:
        #     if reviewer.user:
        #         id_list.append(reviewer.user.id)     
        # users = User.objects.exclude(id__in=id_list)
    
        # formset = UserModelFormset(queryset=users)

        # only filter(), all() and exclude() methods on User.objects will return the queryset; get() method won't
        keywords = paper.keywords.all()
        users = User.objects.all()
        id_list = []

        for user in users:
            research_areas_names = []
            for research_area in user.research_areas.all():
                research_areas_names.append(research_area.name)
            for keyword in keywords:                  
                if any(keyword.name.replace(" ", "").lower() == research_area_name.replace(" ", "").lower() for research_area_name in research_areas_names):    
                       id_list.append(user.id)
                       break

        reviewers = paper.reviewers.all()
        for reviewer in reviewers:
            if reviewer.user:
                if reviewer.user.id in id_list:
                    id_list.remove(reviewer.user.id)       

        users = User.objects.filter(id__in=id_list)
        formset = UserModelFormset(queryset=users)

    context = {
        'formset': formset,
        'paper': paper,
        'papers': papers,
        'display_add_reviewer_modal': display_add_reviewer_modal,
        'conference': conference,
    }
    return render(request, 'conference/view_papers.html', context)

def reviewer_info(request, conference_id, paper_id, reviewer_id):
    papers = Paper.objects.filter(conference=conference_id).order_by('created_at')
    conference = Conference.objects.get(id = conference_id)
    display_reviewer_info_modal = True
    reviewer = Reviewer.objects.get(id=reviewer_id)
    context = {
        "papers": papers,
        "conference": conference,
        "display_reviewer_info_modal": display_reviewer_info_modal,
        "reviewer": reviewer
    } 
    return render(request, 'conference/view_papers.html', context)

def delete_reviewer(request, conference_id, paper_id, reviewer_id):
    paper = Paper.objects.get(id=paper_id)
    paper.reviewers.remove(reviewer_id)

    reviewer = Reviewer.objects.get(id=reviewer_id)
    papers = Paper.objects.all()

    flag = 0
    for paper in papers:
        if reviewer in paper.reviewers.all():
            flag = 1

    if flag == 0:
        reviewer.delete()

    return redirect('view_papers', conference_id)    





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


def review(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link')    
        return redirect('myAccount')


    