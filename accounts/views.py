from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages, auth
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

from conference.models import Conference, Paper

from .utils import detectUser, send_verification_email

from .models import User, UserProfile
from .forms import UserForm

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
# def registerUser(request):
#     if request.user.is_authenticated:
#         messages.warning(request, 'You are already logged in!')
#         return redirect('myAccount')
#     elif request.method=='POST':
#         form = UserForm(request.POST)
#         if form.is_valid():
#             first_name = form.cleaned_data['first_name']
#             last_name = form.cleaned_data['last_name']
#             username = form.cleaned_data['username']
#             email = form.cleaned_data['email'].lower()
#             password = form.cleaned_data['password']
#             user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
#             user.save()
            
#             mail_subject = 'Please activate your account'
#             email_template = 'accounts/emails/account_verification.html'
#             send_verification_email(request, user, mail_subject, email_template)

#             messages.success(request, 'Your account has been registered sucessfully!')
#             return redirect('registerUser')
#     else:
#         form = UserForm()
#     register_user = True    
#     context = {
#         'form': form,
#         'register_user': register_user,
#         'non_field_errors': form.non_field_errors(),
#     }
#     return render(request, 'home.html', context)

# def activate(request, uidb64, token):
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

# def login(request):
#     if request.user.is_authenticated:
#         messages.warning(request, 'You are already logged in!')
#         return redirect('myAccount')
#     elif request.method=="POST":
#         email = request.POST["email"]
#         password = request.POST["password"]

#         user = auth.authenticate(email=email, password=password)

#         if user is not None:
#             auth.login(request, user)
#             messages.success(request, 'You are now logged in.')
#             return redirect('myAccount')
#         else:
#             messages.error(request, 'Invalid login credentials')
#             return redirect('login')
#     login_user = True   
#     context = {
#         'login_user': login_user,
#     }
#     return render(request, 'home.html', context)
def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method=='POST':
        form = UserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email'].lower()
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.save()
            
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Your account has been registered sucessfully!')
            return redirect('registerUser')
    else:
        form = UserForm()
    context = {
        'form': form,
        'non_field_errors': form.non_field_errors(),
    }
    return render(request, 'home.html', context)

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
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
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
    context = {
        "papers": papers,
        "conferences": conferences,
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
            mail_subject = 'Reset Your Password'
            email_template = 'accounts/emails/reset_password.html'
            send_verification_email(request, user, mail_subject, email_template) 

            messages.success(request, 'Password reset link has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')
        
    return render(request, 'accounts/forgot_password.html')
        

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None    

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('myAccount')    

def reset_password(request):
    if request.method=='POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password==confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset sucessful!')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')
