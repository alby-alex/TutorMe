# Generated by Django 4.1.6 on 2023-03-22 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KnowledgeLink', '0005_student'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutor',
            name='hourly_rate',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]
