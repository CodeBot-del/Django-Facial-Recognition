# Generated by Django 3.1.2 on 2022-03-29 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scanner', '0002_auto_20220329_0610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upload',
            name='image',
            field=models.ImageField(upload_to='data'),
        ),
    ]
