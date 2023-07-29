from django import forms
from django.http import HttpResponseRedirect
from django.urls import resolve
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages, auth
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib.sessions.models import Session
from itertools import chain, groupby

from conference.models import Conference, Editor
from paper.models import Author, Paper, Paper_Reviewer

from .utils import detectUser, send_verification_email

from .models import ResearchArea, User
from .forms import ResearchAreaFormSet, UserForm

def check_role_admin(user):
    if user.is_admin:
        return True
    else:
        raise PermissionDenied

def check_role_author(user):
    if user.role == 'Author':
        return True
    else:
        raise PermissionDenied  

def check_role_editor(user):
    if user.role == 'Editor':
        return True
    else:
        raise PermissionDenied 

def registerAuthor(request):
    if request.user.is_authenticated and request.user.role == 'Author':
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method=='POST':
        form = UserForm(request.POST)

        email = request.POST['email']
        try:
            user = User.objects.get(email=email, role='Author')
        except:
            user = None
        if user:
            form.add_error(None, "Author with this Email already exists.") 

        formset = ResearchAreaFormSet(request.POST, prefix='research_areas')
        if form.is_valid() and formset.is_valid():

            user = form.save(commit=False)
            user.username = user.email.split("@")[0] + 'A'
            password = User.objects.make_random_password()
            user.set_password(password)
            user.role = 'Author'
            user.save()

            try:
                author = Author.objects.get(email=user.email)
            except:
                author = None
            if author:
                author.user = user  

            for form in formset:
                research_area = form.save(commit=False)
                if research_area.name != '':
                    research_area.user = user
                    research_area.save()
                  
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification.html'
            send_verification_email(request, user, mail_subject, email_template, password)

            messages.success(request, 'Your account has been registered sucessfully!')
            return redirect('loginAuthor')
        else:
            print(form.errors)
    else:
        form = UserForm()
        formset = ResearchAreaFormSet(prefix='research_areas')
    context = {
        'form': form,
        'formset': formset,
        'non_field_errors': form.non_field_errors(),
    }
    return render(request, 'accounts/registerAuthor.html', context)

def registerEditor(request):
    if request.user.is_authenticated and request.user.role == 'Editor':
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method=='POST':
        form = UserForm(request.POST)

        email = request.POST['email']
        try:
            user = User.objects.get(email=email, role='Editor')
        except:
            user = None
        if user:
            form.add_error(None, "Editor with this Email already exists.") 

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email.split("@")[0] + 'E'
            password = User.objects.make_random_password()
            user.set_password(password)
            user.role = 'Editor'
            user.save()

            try:
                editor = Editor.objects.get(email=user.email)
            except:
                editor = None
            if editor:
                editor.user = user        

            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification.html'
            send_verification_email(request, user, mail_subject, email_template, password)

            messages.success(request, 'Your account has been registered sucessfully!')
            return redirect('loginEditor')
        else:
            print(form.errors)
    else:
        form = UserForm()
    context = {
        'form': form,
        'non_field_errors': form.non_field_errors(),
    }
    return render(request, 'accounts/registerEditor.html', context)

def edit_profile(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method=='POST':
        form = UserForm(request.POST, instance=user)
        
        if user.role == 'Author':
            formset = ResearchAreaFormSet(request.POST, prefix='research_areas', instance=user)
            if formset.is_valid():
                for rform in formset:
                    research_area = rform.save(commit=False)
                    if research_area.name != '':
                        print(1)
                        research_area.user = user
                        research_area.save()
                    elif research_area.name == '' and rform.instance.id:
                        rform.instance.delete()
            else:
                print(formset.errors)

        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            messages.success(request, 'Your profile has been edited sucessfully!')
            return redirect('myAccount')
        else:
            print(form.errors)
    else:
        form = UserForm(instance=user)
        if user.role == 'Author':
            formset = ResearchAreaFormSet(prefix='research_areas', instance=user)
    
    context = {
        'form': form,
        'non_field_errors': form.non_field_errors(),
        'user': user
    } 

    if user.role == 'Author':
        context['formset'] = formset

    return render(request, 'accounts/edit_profile.html', context)


def delete_research_area(request, pk):
    try:
        research_area = ResearchArea.objects.get(id=pk)
    except ResearchArea.DoesNotExist:
        messages.success(
            request, 'Research Area does not exist'
            )
        return redirect('edit_profile', research_area.user.id)

    research_area.delete()
    messages.success(
            request, 'Research Area deleted successfully'
            )
    return redirect('edit_profile', research_area.user.id)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
    else:
        messages.error(request, 'Invalid activation link')    
        
    if user.role == 'Editor':
        return redirect('loginEditor')
    else:
        return  redirect('loginAuthor')    

def loginAuthor(request):
    try:
        next = request.GET['next']  
    except:
        next = "" 

    if request.user.is_authenticated and request.user.role == 'Author':
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method=="POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)

        if user is not None and user.role == 'Author':
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')

            if next == "":
                return HttpResponseRedirect('/loginAuthor/')
            else:
                return HttpResponseRedirect(next)
        else:
            messages.error(request, 'Invalid login credentials')
            
    context = {
        'next': next
    }  
    return render(request, 'accounts/loginAuthor.html', context)

def loginEditor(request):
    try:
        next = request.GET['next']  
    except:
        next = "" 

    if request.user.is_authenticated and request.user.role == 'Editor':
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method=="POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password) 

        if user is not None and user.role == 'Editor':
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')

            if next == "":
                return HttpResponseRedirect('/loginEditor/')
            else:
                return HttpResponseRedirect(next)
        else:
            messages.error(request, 'Invalid login credentials')
        
    context = {
        'next': next
    }  
    return render(request, 'accounts/loginEditor.html', context)

def loginAdmin(request):  
    try:
        next = request.GET['next']  
    except:
        next = ""  

    if request.user.is_authenticated and request.user.is_admin:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method=="POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password) 

        if user is not None and user.is_admin:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')

            if next == "":
                return HttpResponseRedirect('/loginAdmin/')
            else:
                return HttpResponseRedirect(next)
        else:
            messages.error(request, 'Invalid login credentials')

    context = {
        'next': next
    }       
    return render(request, 'accounts/loginAdmin.html', context)


def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out.')
    return redirect('home')

def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url='loginAuthor')
@user_passes_test(check_role_author)
def authorDashboard(request):
    paper_reviewers = Paper_Reviewer.objects.filter(reviewer__user=request.user)
    
    try:
        author = Author.objects.get(user=request.user)
    except:
        author = None

    papers_qs1 = Paper.objects.filter(submitter=request.user)
    papers_qs2 = Paper.objects.filter(authors__in=[author])
    papers = papers_qs1 | papers_qs2
    papers = papers.distinct()

    context = {
        "papers": papers,
        "paper_reviewers": paper_reviewers
    }
    return render(request, 'accounts/authorDashboard.html', context)

@login_required(login_url='loginEditor')
@user_passes_test(check_role_editor)
def editorDashboard(request):

    try:
        editor = Editor.objects.get(user=request.user)
    except:
        editor = None

    conferences_qs1 = Conference.objects.filter(creator=request.user)
    conferences_qs2 = Conference.objects.filter(editors__in=[editor])

    conferences = conferences_qs1 | conferences_qs2 # qs1.union(qs2, qs3)
    conferences = conferences.distinct()

    context = {
        "conferences": conferences,
    }
    return render(request, 'accounts/editorDashboard.html', context)

@login_required(login_url='loginAdmin')
@user_passes_test(check_role_admin)
def adminDashboard(request):
    return render(request, 'accounts/adminDashboard.html')

def forgot_password(request): 
    role = request.GET['role'] # role = request.GET.get('role')
    if request.method=='POST':
        email = request.POST['email']              

        try:
            if role=='Admin':
                user = User.objects.get(email=email, is_admin=True)
            else:    
                user = User.objects.get(email=email, role=role)
        except User.DoesNotExist:
            user = None

        # In this version, we use the filter() method instead of get(), and then we use the first() method to retrieve
        # the first matching object. If no matching object is found, first() returns None, which is exactly what we want as the default value for user.    
        #     user = User.objects.filter(email=email, role=role).first()    
        if user:
            # send reset password email
            mail_subject = 'Your new Password'
            email_template = 'accounts/emails/reset_password.html'
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()
            send_verification_email(request, user, mail_subject, email_template, password) 

            messages.success(request, 'A new Password has been sent to your email address.')
            if user.role == 'Editor':
                return redirect('loginEditor')
            elif user.role == 'Author':
                return redirect('loginAuthor')  
            else:
                return redirect('loginAdmin')
        else:
            messages.error(request, 'Account does not exist')
    context = {
        'role': role
    }    
    return render(request, 'accounts/forgot_password.html', context)

def reset_password(request):
    if request.method=='POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password==confirm_password:
            user = request.user
            user.set_password(password)
            user.save()
            messages.success(request, 'Password changed sucessfully!')
            if user.role == 'Editor':
                return redirect('loginEditor')
            elif user.role == 'Author':
                return  redirect('loginAuthor')  
            else:
                return  redirect('loginAdmin')  
        else:
            messages.error(request, 'Password do not match!')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')

