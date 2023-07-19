from django.db import models
from django.db.models.fields.related import OneToOneField
from accounts.models import User

from .utils import send_conference_approval_status_email

# Create your models here.

class Editor(models.Model):
    user = OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name + " " + self.last_name

class Conference(models.Model):
    RESEARCH_AREA_CHOICES = (
        ('Accounting and Finance', 'Accounts and Finance'),
        ('Arts and Humanities', 'Arts and Humanities'),
        ('Physics', 'Physics'),
        ('Chemistry', 'Chemistry'),
        ('Mathematics and Statistics', 'Mathematics and Statistics'),
        ('Language and Linguistics', 'Language and Linguistics'),
        ('Engineering', 'Engineering'),
    )
    APPROVAL_CHOICES = (
        (True, 'Approved'),
        (False, 'Not Approved'),
    )
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    editors = models.ManyToManyField(Editor, blank=True)
    name = models.CharField(max_length=200, unique=True)
    acronym = models.CharField(max_length=100, unique=True)
    research_area = models.CharField(max_length=200, choices=RESEARCH_AREA_CHOICES)
    venue = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    web_page = models.URLField(max_length=100, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    submission_deadline = models.DateField()
    is_creator_editor = models.BooleanField(blank=True, null=True)

    is_approved = models.BooleanField(choices=APPROVAL_CHOICES, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.acronym
    
    def organised_by(self):
        return ", ".join([str(i) for i in self.editors.all()])
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = Conference.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:
                if self.is_approved == True:
                    mail_subject = "Congratulations! Your request for conference creation- " + self.name + "(" + self.acronym + ")" + " has been approved."
                    send_conference_approval_status_email(mail_subject, self)
                else:
                    mail_subject = "We're sorry! Your request for conference creation- " + self.name + "(" + self.acronym + ")" + " has been rejected."
                    send_conference_approval_status_email(mail_subject, self)
        return super(Conference, self).save(*args,)     


