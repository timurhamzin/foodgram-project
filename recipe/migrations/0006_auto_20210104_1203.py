# Generated by Django 3.1.4 on 2021-01-04 07:03

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipe', '0005_auto_20210104_0022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='recipe_images'),
        ),
        migrations.AlterUniqueTogether(
            name='followrecipe',
            unique_together={('user', 'recipe')},
        ),
        migrations.AlterUniqueTogether(
            name='followuser',
            unique_together={('user', 'author')},
        ),
    ]
