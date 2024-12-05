# Generated by Django 5.1.2 on 2024-12-04 02:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='members',
            field=models.ManyToManyField(related_name='companies_members', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='company',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='companies_owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='CompanyInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('PENDING', 'pending'), ('ACCEPTED', 'accepted'), ('DECLINED', 'declined'), ('REVOKED', 'revoked')], default='PENDING', max_length=20)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations_company', to='companies.company')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Company Invitation',
                'verbose_name_plural': 'Company Invitations',
            },
        ),
        migrations.CreateModel(
            name='CompanyRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('PENDING', 'pending'), ('APPROVED', 'approved'), ('REJECTED', 'rejected'), ('CANCELED', 'canceled')], default='PENDING', max_length=20)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests_company', to='companies.company')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Company Request',
                'verbose_name_plural': 'Company Requests',
            },
        ),
    ]
