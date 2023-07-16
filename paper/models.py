from django.db import models
from django.db.models.fields.related import OneToOneField

from accounts.models import User
from conference.models import Conference

# Create your models here.

class Author(models.Model):
    user = OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Reviewer(models.Model):
    user = OneToOneField(User, on_delete=models.SET_NULL, related_name='reviewer', blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)    

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Paper(models.Model):
    submitter = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    conference = models.ForeignKey(Conference, on_delete=models.SET_NULL, blank=True, null=True)
    reviewers = models.ManyToManyField(Reviewer, through='Paper_Reviewer')
    title = models.CharField(max_length=200)
    abstract = models.TextField(max_length=300)
    authors = models.ManyToManyField(Author, blank=True)
    file = models.FileField(upload_to='conference/papers', blank=True, null=True)
    file_hash = models.CharField(max_length=32, blank=True, null=True)
    is_submitter_author = models.BooleanField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def written_by(self):
        return ", ".join([str(i) for i in self.authors.all()])
    
    def reviewed_by(self):
        return ", ".join([str(i) for i in self.reviewers.all()])
    
    # def calculate_file_hash(self):
    #     import hashlib

    #     # Open the file in binary mode
    #     with self.file.open('rb') as file:
    #         # Read the file's content
    #         content = file.read()

    #     # Calculate the MD5 hash value
    #     hash_value = hashlib.md5(content).hexdigest()

    #     return hash_value
    
    # def save(self, *args, **kwargs):
    #     # Calculate and set the file_hash value before saving the model
    #     self.file_hash = self.calculate_file_hash()
    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    

class Paper_Reviewer(models.Model):
    status_choices = (
        ('pending', 'pending'),
        ('accepted', 'accepted'),
        ('declined', 'declined'),
    )
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=status_choices, default='pending')
    class Meta:
        unique_together = ('paper', 'reviewer')
        verbose_name = 'Paper_Reviewer_pair'
        verbose_name_plural = 'Paper_Reviewer_pairs'
    
    
class Keywords(models.Model):
    name = models.CharField(max_length=50, blank=True)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='keywords', blank=True, null=True)

    class Meta:
        verbose_name = 'Keyword'
        verbose_name_plural = 'Keywords'

    def __str__(self):
        return self.name


class Review(models.Model):
    paper = models.ForeignKey(Paper, related_name="reviews", on_delete=models.CASCADE)
    reviewer = models.ForeignKey(Reviewer, related_name="reviews", on_delete=models.CASCADE)
    body = models.TextField()
    date_reviewed = models.DateTimeField(auto_now_add=True)