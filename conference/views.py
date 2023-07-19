from datetime import date
from datetime import datetime

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.urls import resolve
from django.utils.dateformat import DateFormat
from django.core.paginator import Paginator

from accounts.models import User
from conference.models import Conference, Editor
from paper.models import Paper, Paper_Reviewer, Reviewer
from conference.utils import send_conference_approval_request_email, send_review_invitation_email
# from .utils import send_approval_request_email

from .forms import AlternateConferenceForm, ConferenceModelFormset, UserModelFormset, ConferenceForm, EditorForm, ReviewerForm

def check_role_admin(user):
    if user.is_admin == True:
        return True
    else:
        raise PermissionDenied

def get_user(request):
    user = Conference.objects.get(user=request.user)
    return user

def delete_conference(request, conference_id):
    conference = Conference.objects.get(id=conference_id)
    conferences = Conference.objects.exclude(id=conference_id)
    editors = conference.editors.all()
    
    for editor in editors: 
        flag = 0
        for c in conferences:
            if editor in c.editors.all():
                flag = 1
                break
        if flag == 0:
            editor.delete()

    conference.delete()
    messages.success(request, 'Conference has been deleted successfully!')    

    return redirect('myAccount')


@login_required(login_url='login')
def create_conference(request, conference_id=None, editor_id=None):
    conference = get_object_or_404(Conference, id=conference_id) if conference_id else None
    url_name = resolve(request.path_info).url_name

    if request.method == 'POST':
        form = ConferenceForm(request.POST, instance=conference)  
        if form.is_valid():
            conference = form.save() 
            
            is_creator_editor = form.cleaned_data['is_creator_editor']
            if is_creator_editor == True:
                editors = Editor.objects.all()
                flag = 0
                for editor in editors:
                    if editor.user == request.user:
                        conference.editors.add(editor.id)
                        flag = 1
                        break 
                if flag==0:    
                    new_editor = Editor.objects.create(
                                        first_name = request.user.first_name,
                                        last_name = request.user.last_name,
                                        email = request.user.email,
                                        user = request.user,
                                    )
                    new_editor.save()
                    conference.editors.add(new_editor.id) 
            else:
                editors = Editor.objects.all()
                for editor in editors:
                    if editor.user == request.user:
                        if editor in conference.editors.all():
                            conference.editors.remove(editor.id)

                            flag = 0
                            conferences = Conference.objects.exclude(id=conference.id)
                            for conference in conferences:
                                if editor in conference.editors.all():
                                       flag = 1 
                            if flag == 0:
                                editor.delete()           
                            break

            conference.creator = request.user
            conference.save()

            action = request.GET.get('action')
            if action == 'edit_editor': # create conference
                return redirect('edit_editor', conference.id, editor_id)
            elif action == 'delete_editor': # create conference
                return redirect('delete_editor', conference.id, editor_id)
            elif action == 'edit_conference_edit_editor':
                return redirect('edit_conference_edit_editor', conference.id, editor_id)
            elif action == 'edit_conference_delete_editor':
                return redirect('edit_conference_delete_editor', conference.id, editor_id)
            
            if 'add_editor' in request.POST: # create conference
                return redirect('add_editor', conference.id)
            elif 'edit_conference_add_editor' in request.POST:
                return redirect('edit_conference_add_editor', conference.id)
            
            if url_name == 'create_conference':        
                send_conference_approval_request_email(request, conference.id)

                messages.success(request, 'Your conference has been registered sucessfully! Please wait for the approval.')
            elif url_name == 'edit_conference':
                messages.success(request, 'Conference edited successfully!')
            return redirect('myAccount')
        else:
            print(form.errors)     
    else:
        form = ConferenceForm(instance=conference)
    context = {
        "form": form,
        "conference": conference,
    }
    if url_name == 'create_conference':
        return render(request, 'conference/create_conference.html', context)
    elif url_name == 'edit_conference':
        return render(request, 'conference/edit_conference.html', context)


def add_editor(request, conference_id):
    url_name = resolve(request.path_info).url_name
    if url_name == 'add_editor':
        x = redirect('create_conference', conference_id)
    elif url_name == 'edit_conference_add_editor':    
        x = redirect('edit_conference', conference_id)
        
    conference = get_object_or_404(Conference, id=conference_id)
    form = ConferenceForm(instance=conference)
    display_add_editor_modal = True 

    if request.method == 'POST':
        eform = EditorForm(request.POST)
        if eform.is_valid(): 
            email = eform.cleaned_data['email'].lower()
            editors = Editor.objects.all()
            for editor in editors:
                if editor.email == email:
                    conference.editors.add(editor.id)
                    editor.first_name = eform.cleaned_data['first_name'] #
                    editor.last_name = eform.cleaned_data['last_name'] #
                    editor.save() #
                    # paper.save()
                    # return redirect('submit_paper', conference_id, paper_id)
                    return x
                
            editor = eform.save(commit=False)

            try:
                user = User.objects.get(email=email, role='Editor')
            except:
                user = None     
            if user: 
                editor.user = user

            editor.email = email
            eform.save()

            conference.editors.add(editor.id)
            
            return x
        else:
            print(eform.errors)
    else:
        eform = EditorForm()
              
    context = {
        "eform": eform,
        "display_add_editor_modal": display_add_editor_modal,
        "form": form,
        "conference": conference,
    }
    if url_name == 'add_editor':
        y = render(request, 'conference/add_editor.html', context)
    elif url_name == 'edit_conference_add_editor': 
        y = render(request, 'conference/edit_conference_add_editor.html', context)
    return y

def delete_editor(request, conference_id, editor_id):
    url_name = resolve(request.path_info).url_name
    if url_name == 'delete_editor':
        x = redirect('create_conference', conference_id)
    elif url_name == 'edit_conference_delete_editor':
        x = redirect('edit_conference', conference_id)

    conference = get_object_or_404(Conference, id=conference_id)
    conference.editors.remove(editor_id)

    editor = get_object_or_404(Editor, id=editor_id)

    if editor.user:
        return x

    conferences = Conference.objects.all()
    for conference in conferences:
        if editor in conference.editors.all():
            return x

    editor.delete()
    return x

def edit_editor(request, conference_id, editor_id):
    url_name = resolve(request.path_info).url_name
    if url_name == 'edit_editor':
        x = redirect('create_conference', conference_id)
    elif url_name == 'edit_conference_edit_editor':
        x = redirect('edit_conference', conference_id)

    conference = get_object_or_404(Conference, id=conference_id)
    form = ConferenceForm(instance=conference)
    display_edit_editor_modal = True

    editor = get_object_or_404(Editor, id=editor_id)
    if request.method == 'POST':
        eform = EditorForm(request.POST, instance=editor)
        if eform.is_valid():
            # code starts here
            entered_email = editor.email.lower()
            orig = Editor.objects.get(id=editor_id)
            if entered_email != orig.email:
                flag = 0
                other_editors = Editor.objects.exclude(id=orig.id)
                for other_editor in other_editors:
                    if other_editor.email == entered_email:
                        conference.editors.add(other_editor.id)
                        other_editor.first_name = editor.first_name #
                        other_editor.last_name = editor.last_name #
                        other_editor.save() #
                        conference.editors.remove(orig.id)
                        flag = 1
                if flag==1:
                    delete_orig = True
                    other_conferences = Conference.objects.exclude(id=conference_id)
                    for other_conference in other_conferences:
                        if orig in other_conference.editors.all():
                            delete_orig = False
                            return x
                    if delete_orig == True:
                        orig.delete()
                        return x     
                elif flag == 0:
                    flag2 = 0
                    other_conferences = Conference.objects.exclude(id=conference_id)
                    for other_conference in other_conferences:
                        if orig in other_conference.editors.all():
                            conference.editors.remove(orig.id)
                            # create a new editor object with a different id and the field values of editor object
                            new_editor = Editor.objects.create(
                                first_name = editor.first_name,
                                last_name = editor.last_name,
                                email = editor.email
                            )

                            try:
                                user = User.objects.get(email=new_editor.email, role='Editor')
                            except:
                                user = None   
                            if user: 
                                new_editor.user = user

                            new_editor.save()
                            conference.editors.add(new_editor.id)
                            flag2 = 1
                    if flag2 == 0:
                        editor.save()
                    return x          
            else:
                orig.first_name = editor.first_name #
                orig.last_name = editor.last_name #
                orig.save() #
                return x
        else:
            print(eform.errors)
    else:
        eform = EditorForm(instance=editor)

    context = {
        "eform": eform,
        "display_edit_editor_modal": display_edit_editor_modal,
        "form": form,
        "conference": conference,
        "editor_id": editor_id,
    }
    if url_name == 'edit_editor':
        y = render(request, 'conference/edit_editor.html', context)
    elif url_name == 'edit_conference_edit_editor': 
        y = render(request, 'conference/edit_conference_edit_editor.html', context)
    return y       

@login_required(login_url='loginAdmin')
@user_passes_test(check_role_admin)
def edit_is_approved_all(request):
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

    # for form in formset:
    #     form.instance.start_date = DateFormat(form.instance.start_date).format('Y-m-d')
    #     form.instance.end_date = DateFormat(form.instance.end_date).format('Y-m-d')
    #     form.instance.submission_deadline = DateFormat(form.instance.submission_deadline).format('Y-m-d')
    context = {
        'formset': formset,
    }
    return render(request, 'conference/edit_is_approved_all.html', context)

@login_required(login_url='loginAdmin')
@user_passes_test(check_role_admin)
def edit_is_approved(request, conference_id):
    conference = Conference.objects.get(id=conference_id)
    if request.method == 'POST':
        form = AlternateConferenceForm(request.POST, instance=conference)

        if form.is_valid():
            form.save()

            return redirect('edit_is_approved_all')
        else:
            print(form.errors)
    else:
        form = AlternateConferenceForm(instance=conference)

    context = {
        'form': form
    }
    return render(request, 'conference/edit_is_approved.html', context)    


def view_papers(request, conference_id):
    papers = Paper.objects.filter(conference=conference_id).order_by('created_at')
    conference = Conference.objects.get(id = conference_id)

    paper_reviewers = Paper_Reviewer.objects.filter(paper__in=papers)

    context = {
        "papers": papers,
        "conference": conference,
        "paper_reviewers": paper_reviewers
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
                        send_review_invitation_email(request, reviewer, target_paper.id)
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
                            send_review_invitation_email(request, reviewer, target_paper.id)
                            
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

                    send_review_invitation_email(request, reviewer, paper.id)

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

            send_review_invitation_email(request, reviewer, paper.id)

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
                        send_review_invitation_email(request, reviewer, paper.id)
                        flag = 1
                if flag == 0:
                    reviewer = Reviewer.objects.create(user=user, first_name=user.first_name, last_name=user.last_name, email=user.email)
                    reviewer.save()
                    paper.reviewers.add(reviewer)  
                    send_review_invitation_email(request, reviewer, paper.id)
                
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
        users = User.objects.filter(role='Author')
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



# def review(request, uidb64, token):
#     try:
#         uid = urlsafe_base64_decode(uidb64).decode()
#         user = User._default_manager.get(pk=uid)
#     except(TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None

#     if user is not None and default_token_generator.check_token(user, token):
#         user.is_active = True
#         user.save()
#         messages.success(request, 'Congratulations! Your account is activated.')
#         return redirect('myAccount')
#     else:
#         messages.error(request, 'Invalid activation link')    
#         return redirect('myAccount')


    