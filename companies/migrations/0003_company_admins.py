# Generated by Django 5.1.2 on 2024-12-14 22:25

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0002_company_members_alter_company_owner_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='admins',
            field=models.ManyToManyField(related_name='company_admins', to=settings.AUTH_USER_MODEL),
        ),
    ]
