from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages, auth
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib.sessions.models import Session

from conference.models import Conference
from paper.models import Paper, Paper_Reviewer

from .utils import detectUser, send_verification_email

from .models import ResearchArea, User, UserProfile
from .forms import ResearchAreaForm, ResearchAreaFormSet, UserForm

def check_role_admin(user):
    if user.is_admin:
        return True
    else:
        raise PermissionDenied

def check_role_guest(user):
    if not user.is_admin:
        return True
    else:
        raise PermissionDenied    

def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method=='POST':
        form = UserForm(request.POST)
        formset = ResearchAreaFormSet(request.POST, prefix='research_areas')
        if form.is_valid() and formset.is_valid():

            user = form.save(commit=False)
            user.username = user.email.split("@")[0]
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()

            for form in formset:
                research_area = form.save(commit=False)
                if research_area.name != '':
                    research_area.user = user
                    research_area.save()
                  
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification.html'
            send_verification_email(request, user, mail_subject, email_template, password)

            messages.success(request, 'Your account has been registered sucessfully!')
            return redirect('login')
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
    return render(request, 'accounts/registerUser.html', context)

def edit_profile(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method=='POST':
        form = UserForm(request.POST, instance=user)
        formset = ResearchAreaFormSet(request.POST, prefix='research_areas', instance=user)
        if form.is_valid() and formset.is_valid():

            user = form.save(commit=False)
            user.save()

            for form in formset:
                research_area = form.save(commit=False)
                if research_area.name != '':
                    research_area.user = user
                    research_area.save()
                elif research_area.name == '' and form.instance.id:
                    form.instance.delete()
                
            messages.success(request, 'Your profile has been edited sucessfully!')
            return redirect('myAccount')
        else:
            print(form.errors)
    else:
        form = UserForm(instance=user)
        formset = ResearchAreaFormSet(prefix='research_areas', instance=user)
    context = {
        'form': form,
        'formset': formset,
        'non_field_errors': form.non_field_errors(),
        'user': user
    }
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
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link')    
        return redirect('myAccount')

def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method=="POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')

            # current_session_key = user.logged_in_user.session_key

            # if current_session_key and current_session_key != request.session.session_key:
            #     Session.objects.get(session_key=current_session_key).delete() 

            # user.logged_in_user.session_key = request.session.session_key
            # user.logged_in_user.save()


            return redirect('myAccount')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')

    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out.')
    return redirect('login')

@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url='login')
@user_passes_test(check_role_guest)
def guestDashboard(request):
    papers = Paper.objects.filter(submitter=request.user)
    conferences = Conference.objects.filter(creator=request.user)
    paper_reviewers = Paper_Reviewer.objects.filter(reviewer__user=request.user)
    
    context = {
        "papers": papers,
        "conferences": conferences,
        "paper_reviewers": paper_reviewers
    }
    return render(request, 'accounts/guestDashboard.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_admin)
def adminDashboard(request):
    return render(request, 'accounts/adminDashboard.html')

def forgot_password(request):
    if request.method=='POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = 'Your new Password'
            email_template = 'accounts/emails/reset_password.html'
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()
            send_verification_email(request, user, mail_subject, email_template, password) 

            messages.success(request, 'A new Password has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')
        
    return render(request, 'accounts/forgot_password.html')

def reset_password(request):
    if request.method=='POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password==confirm_password:
            user = request.user
            user.set_password(password)
            user.save()
            messages.success(request, 'Password changed sucessfully!')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')

