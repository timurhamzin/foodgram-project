# Generated by Django 3.1.4 on 2021-01-11 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0016_auto_20210111_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
