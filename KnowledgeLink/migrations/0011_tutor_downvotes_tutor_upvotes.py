# Generated by Django 4.1.6 on 2023-04-18 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KnowledgeLink', '0010_alter_appointment_course_alter_appointment_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutor',
            name='downvotes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tutor',
            name='upvotes',
            field=models.IntegerField(default=0),
        ),
    ]