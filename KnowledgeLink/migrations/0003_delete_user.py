# Generated by Django 4.1.6 on 2023-03-19 20:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('KnowledgeLink', '0002_remove_user_user_email_remove_user_username'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]
