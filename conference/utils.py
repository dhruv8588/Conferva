from base64 import urlsafe_b64encode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from Conferva_main import settings
from accounts.models import User


# def send_notification(mail_subject, mail_template, context):
#     from_email = settings.DEFAULT_FROM_EMAIL
#     message = render_to_string(mail_template, context)
#     to_email = context['user'].email
#     mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
#     mail.send()

def send_conference_approval_status_email(mail_subject, conference):
    mail_template = 'accounts/emails/conference_approval_status.html'
    from_email = settings.DEFAULT_FROM_EMAIL

    to_email = [conference.creator.email]
    # editors = conference.editors.all()
    # for editor in editors:
    #     to_email.append(editor.email)
    # if conference.creator.email not in to_email:
    #     to_email.append(conference.creator.email)    
    
    message = render_to_string(mail_template, {
        'conference': conference
    })

    mail = EmailMessage(mail_subject, message, from_email, to=to_email)
    mail.send()    

def send_review_invitation_email(request, reviewer, paper_id):
    mail_template = 'accounts/emails/review_invitation.html'
    from_email = settings.DEFAULT_FROM_EMAIL
    mail_subject = 'Invitation to Review'
    to_email = reviewer.email

    current_site = get_current_site(request)
    message = render_to_string(mail_template, {
        'reviewer': reviewer,
        'paper_id': paper_id,
        'domain': current_site,
    })
    
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.send()

    
def send_conference_approval_request_email(request, conference_id):
    mail_subject = 'Request for conference approval'
    mail_template = 'accounts/emails/conference_approval_request.html'

    user = User.objects.get(is_admin=True, is_superadmin = False)

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    current_site = get_current_site(request)
    message = render_to_string(mail_template, {
        'domain': current_site,
        'user': user,
        'conference_id': conference_id
    })

    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.send()
    
