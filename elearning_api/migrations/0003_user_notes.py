# Generated by Django 4.2.8 on 2023-12-08 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elearning_api', '0002_alter_enrollment_enrollment_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='notes',
            field=models.CharField(default='{}', max_length=20000),
        ),
    ]
