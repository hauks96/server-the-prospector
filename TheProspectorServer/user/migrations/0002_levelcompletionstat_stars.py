# Generated by Django 3.1.4 on 2020-12-13 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='levelcompletionstat',
            name='stars',
            field=models.IntegerField(default=1),
        ),
    ]
