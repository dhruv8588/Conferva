# Generated by Django 4.2.1 on 2023-07-09 19:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_researcharea_user_research_areas'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='research_areas',
        ),
        migrations.AddField(
            model_name='researcharea',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
