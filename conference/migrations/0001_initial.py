# Generated by Django 4.2.1 on 2023-06-18 20:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Conference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('acronym', models.CharField(max_length=100, unique=True)),
                ('research_area', models.CharField(choices=[('Accounting and Finance', 'Accounts and Finance'), ('Arts and Humanities', 'Arts and Humanities'), ('Physics', 'Physics'), ('Chemistry', 'Chemistry'), ('Mathematics and Statistics', 'Mathematics and Statistics'), ('Language and Linguistics', 'Language and Linguistics'), ('Engineering', 'Engineering')], max_length=200)),
                ('venue', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('country', models.CharField(max_length=100)),
                ('web_page', models.URLField(blank=True, max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('submission_deadline', models.DateField()),
                ('is_approved', models.BooleanField(blank=True, choices=[(True, 'Approved'), (False, 'Not Approved')], null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator', to=settings.AUTH_USER_MODEL)),
                ('submitters', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('abstract', models.TextField(max_length=300)),
                ('file', models.FileField(blank=True, null=True, upload_to='conference/papers')),
                ('file_hash', models.CharField(blank=True, max_length=32, null=True)),
                ('is_submitter_author', models.BooleanField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('authors', models.ManyToManyField(blank=True, to='conference.author')),
                ('conferences', models.ManyToManyField(blank=True, to='conference.conference')),
                ('submitters', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]