from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import resolve
from django.contrib.auth.decorators import login_required, user_passes_test
import hashlib
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from accounts.models import User
from conference.models import Conference

from .forms import AuthorForm, KeywordsFormSet, PaperForm, ReviewForm
from .models import Author, Paper, Paper_Reviewer, Review

# Create your views here.

def check_role_author(user):
    if user.role == 'Author':
        return True
    else:
        raise PermissionDenied  

def add_author(request, paper_id, conference_id):
    url_name = resolve(request.path_info).url_name
    if url_name == 'add_author':
        x = redirect('submit_paper', paper_id, conference_id)
    elif url_name == 'edit_paper_add_author':    
        x = redirect('edit_paper', paper_id, conference_id)

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

            try:
                user = User.objects.get(email=email, role='Author')
            except:
                user = None     
            if user: 
                author.user = user

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
        y = render(request, 'paper/add_author.html', context)
    elif url_name == 'edit_paper_add_author': 
        y = render(request, 'paper/edit_paper_add_author.html', context)
    return y


def edit_author(request, paper_id, conference_id, author_id):
    url_name = resolve(request.path_info).url_name
    if url_name == 'edit_author':
        x = redirect('submit_paper', paper_id, conference_id)
    elif url_name == 'edit_paper_edit_author':
        x = redirect('edit_paper', paper_id, conference_id)

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

                            try:
                                user = User.objects.get(email=new_author.email, role='Author')
                            except:
                                user = None   
                            if user: 
                                new_author.user = user

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
        y = render(request, 'paper/edit_author.html', context)
    elif url_name == 'edit_paper_edit_author': 
        y = render(request, 'paper/edit_paper_edit_author.html', context)
    return y       


def delete_author(request, paper_id, conference_id, author_id):
    url_name = resolve(request.path_info).url_name
    if url_name == 'delete_author':
        x = redirect('submit_paper', paper_id, conference_id)
    elif url_name == 'edit_paper_delete_author':
        x = redirect('edit_paper', paper_id, conference_id)

    paper = get_object_or_404(Paper, id=paper_id)
    paper.authors.remove(author_id)

    author = get_object_or_404(Author, id=author_id)

    papers = Paper.objects.all()
    for paper in papers:
        if author in paper.authors.all():
            return x

    author.delete()
    return x


@login_required(login_url='login')
def submit_paper(request, paper_id=None, conference_id=None, author_id=None):
    paper = get_object_or_404(Paper, id=paper_id) if paper_id else None
    conference = get_object_or_404(Conference, id=conference_id)
    url_name = resolve(request.path_info).url_name

    if request.method == 'POST':
        form = PaperForm(request.POST, request.FILES, instance=paper)
        formset = KeywordsFormSet(request.POST, prefix='keywords', instance=paper)
          
        if form.is_valid() and formset.is_valid():
            paper = form.save() 
            
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
                return redirect('edit_author', paper.id, conference_id, author_id)
            elif action == 'delete_author': # submit paper
                return redirect('delete_author', paper.id, conference_id, author_id)
            elif action == 'edit_paper_edit_author':
                return redirect('edit_paper_edit_author', paper.id, conference_id, author_id)
            elif action == 'edit_paper_delete_author':
                return redirect('edit_paper_delete_author', paper.id, conference_id, author_id)
            
            if 'add_author' in request.POST: # submit paper
                print(1)
                return redirect('add_author', paper.id, conference_id)
            elif 'edit_paper_add_author' in request.POST:
                return redirect('edit_paper_add_author', paper.id, conference_id)
            elif 'edit_paper' in request.POST:
                return redirect('edit_paper', paper.id, conference_id)
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
                                    return redirect('submit_paper', paper.id, conference_id)
                                elif url_name == 'edit_paper':
                                    return redirect('edit_paper', paper.id, conference_id)
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
        return render(request, 'paper/submit_paper.html', context)
    elif url_name == 'edit_paper':
        return render(request, 'paper/edit_paper.html', context)


def delete_paper(request, paper_id):
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

@login_required(login_url='loginAuthor')
@user_passes_test(check_role_author)
def accept_or_decline_to_review(request, paper_id):
    paper = Paper.objects.get(id=paper_id)
    context = {
        "paper": paper
    }
    return render(request, 'paper/accept_or_decline_to_review.html', context)

def decline_to_review(request, paper_id):
    paper_reviewer = Paper_Reviewer.objects.get(paper=paper_id, reviewer__user=request.user)
    paper_reviewer.status = 'declined'
    paper_reviewer.save()

    messages.info(request, 'You have declined to review the paper- %s' % paper_reviewer.paper.title)  
    return redirect('myAccount')

def delete_review(request, paper_id):
    review = Review.objects.get(paper=paper_id, reviewer__user=request.user) 
    review.delete()
    messages.info(request, 'You have successfully deleted your review of the paper- %s' % review.paper.title)
    return redirect('myAccount')

def review(request, paper_id):
    paper = Paper.objects.get(id=paper_id)

    paper_reviewer = Paper_Reviewer.objects.get(paper=paper_id, reviewer__user=request.user)
    paper_reviewer.status = 'accepted'
    paper_reviewer.save()

    try:
        review = Review.objects.get(paper=paper_id, reviewer__user=request.user) 
    except:
        review = None

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        review = form.save(commit=False)
        review.paper = paper
        review.reviewer = paper_reviewer.reviewer
        review.save()
        messages.info(request, 'You have successfully reviewed the paper- %s' % paper_reviewer.paper.title)
        return redirect('myAccount')
    else:
        form = ReviewForm(instance=review)    
    context = {
        'form': form,
        'paper': paper,
        'review': review
    }
    return render(request, 'paper/review.html', context)

