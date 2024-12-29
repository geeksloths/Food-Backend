# Generated by Django 5.0.7 on 2024-12-29 10:35

import Extras.models
import Utils.functions
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Restaurant', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Extra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(default=Utils.functions.get_uuid, editable=False, max_length=15, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('icon', models.FileField(upload_to=Extras.models.get_extra_image, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['svg', 'jpg', 'png'])])),
                ('price', models.IntegerField()),
                ('stack', models.IntegerField(default=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('edited_at', models.DateTimeField(auto_now=True)),
                ('restaurant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Restaurant.restaurant')),
            ],
        ),
    ]
