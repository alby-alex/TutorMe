# Generated by Django 4.1.6 on 2023-03-19 20:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('KnowledgeLink', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='user_email',
        ),
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
    ]
