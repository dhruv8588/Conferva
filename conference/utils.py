from base64 import urlsafe_b64encode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from Conferva_main import settings
from accounts.models import User


def send_notification(mail_subject, mail_template, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(mail_template, context)
    to_email = context['user'].email
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.send()

# def send_review_invitation(request, reviewer, email_template):
#     from_email = settings.DEFAULT_FROM_EMAIL
#     current_site = get_current_site(request)
#     print(current_site)
#     message = render_to_string(email_template, {
#         'reviewer': reviewer,
#         'domain': current_site,
#         'uid': urlsafe_base64_encode(force_bytes(reviewer.pk)),
#         'token': default_token_generator.make_token(reviewer),
#     })
#     mail_subject = 'Invite to Review'
#     to_email = reviewer.email
#     mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
#     mail.send()

def send_review_invitation(request, user, email_template):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    print(current_site)
    message = render_to_string(email_template, {
        'reviewer': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    mail_subject = 'Invite to Review'
    to_email = user.email
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.send()

    
# def send_approval_request_email(request, mail_subject, mail_template):
#     from_email = request.user.email
#     print(from_email)
#     # to_email = settings.DEFAULT_FROM_EMAIL
#     to_email = 'dhruv1blue2@gmail.com'

#     print(to_email)

#     user = User.objects.filter(is_admin=True, is_superadmin = False)[0]
#     print(user)
#     current_site = get_current_site(request)
#     message = render_to_string(mail_template, {
#         'user': user,
#         'domain': current_site,
#         'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#         'token': default_token_generator.make_token(user),
#     })

#     mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
#     mail.send()
    
