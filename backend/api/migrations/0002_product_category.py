# Generated by Django 5.1.2 on 2024-11-19 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.CharField(default=None, max_length=255),
            preserve_default=False,
        ),
    ]
