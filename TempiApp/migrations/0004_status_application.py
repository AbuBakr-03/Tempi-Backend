# Generated by Django 5.2.1 on 2025-06-01 11:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TempiApp', '0003_alter_job_pay_alter_userprofile_user_wishlist'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=255)),
                ('phone_number', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=255)),
                ('resume', models.FileField(blank=True, null=True, upload_to='resumes/')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TempiApp.job')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TempiApp.status')),
            ],
            options={
                'indexes': [models.Index(fields=['user'], name='TempiApp_ap_user_id_531f01_idx'), models.Index(fields=['job'], name='TempiApp_ap_job_id_d0349b_idx'), models.Index(fields=['status'], name='TempiApp_ap_status__301964_idx')],
                'unique_together': {('user', 'job')},
            },
        ),
    ]
