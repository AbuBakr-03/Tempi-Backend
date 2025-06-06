# Generated by Django 5.2.1 on 2025-06-02 17:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TempiApp', '0004_status_application'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='JobAssignmentStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='JobAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='TempiApp.application')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TempiApp.job')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TempiApp.jobassignmentstatus')),
            ],
            options={
                'indexes': [models.Index(fields=['user'], name='TempiApp_jo_user_id_f5f824_idx'), models.Index(fields=['job'], name='TempiApp_jo_job_id_469115_idx')],
                'unique_together': {('user', 'job')},
            },
        ),
    ]
