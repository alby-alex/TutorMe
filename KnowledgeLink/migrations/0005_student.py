# Generated by Django 4.1.6 on 2023-03-20 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KnowledgeLink', '0004_rename_availability_tutor_friday_availability_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=200)),
                ('user_email', models.CharField(max_length=200)),
            ],
        ),
    ]
