from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.signals import post_save, pre_save
from django.db.models.fields.related import OneToOneField
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist

from Conferva_main import settings

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have an username')
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name 
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            email = self.normalize_email(email), 
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    ROLE_CHOICE = (
        ('Author', 'Author'),
        ('Editor', 'Editor'),
    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100)
    role = models.CharField(choices=ROLE_CHOICE, max_length=20, blank=True, null=True)
    # research_areas = models.ManyToManyField(ResearchArea, blank=True, null=True)
    # research_areas = ArrayField(models.CharField(max_length=10, blank=True), size=3, blank=True, null=True)

    # required fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
    
    # def get_role(self):
    #     user_role = ""
    #     if self.is_admin==True:
    #         user_role = 'Admin'
    #     elif self.is_admin==False:
    #         user_role = 'Guest'
    #     return user_role    

    # def has_related_object(self):
    #     is_reviewer = False
    #     try:
    #         is_reviewer = (self.reviewer is not None)
    #     except Reviewer.DoesNotExist:
    #         pass
    #     return is_reviewer

    # def has_related_object(self):
    #     try:
    #         self.reviewer
    #         return True
    #     except ObjectDoesNotExist:
    #         return False

    # def has_related_object(self):
    #     return hasattr(self, 'reviewer')

    # def researched_in(self):
    #     return ", ".join([str(i) for i in self.research_areas.all()]) 

class ResearchArea(models.Model):
    name = models.CharField(max_length=50, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='research_areas', blank=True, null=True)

    def __str__(self):
        return self.name

# class UserProfile(models.Model):
#     user = OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
#     profile_picture = models.ImageField(upload_to='users/profile_pictures', blank=True)
#     country = models.CharField(max_length=15, blank=True)
#     organisation = models.CharField(max_length=15, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     modified_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.user.email    
    
# class LoggedInUser(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='logged_in_user', on_delete=models.CASCADE)
#     session_key = models.CharField(max_length=32, blank=True, null=True)    

#     def __str__(self):
#         return self.user.username