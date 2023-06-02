from django.db import models

from accounts.models import User, UserProfile
from accounts.utils import send_notification

# Create your models here.
class Editor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.first_name
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = Editor.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:
                mail_template = 'accounts/emails/admin_approval.html'
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved,
                }
                if self.is_approved == True:
                    mail_subject = "Congratulations! You request has been approved for organizing a conference."
                    send_notification(mail_subject, mail_template, context)
                else:
                    mail_subject = "We're sorry! You are not eligible for organizing a conference."
                    send_notification(mail_subject, mail_template, context)
        return super(Editor, self).save(*args,)            
