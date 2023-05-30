from django.utils.http import urlsafe_base64_decode
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator

from .utils import send_verification_email

from .models import User
from .forms import UserForm

# Create your views here.

def registerUser(request):
    if request.method=='POST':
        form = UserForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.set_password(password)
            user.role = User.AUTHOR
            form.save()
            send_verification_email(request, user)
            messages.success(request, 'Your account has been registered sucessfully!')
            return redirect('registerUser')
    else:
        form = UserForm()    
    context = {
        'form': form,
    }
    return render(request, 'accounts/registerUser.html', context)

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

def myAccount(request):
    return redirect('registerUser')