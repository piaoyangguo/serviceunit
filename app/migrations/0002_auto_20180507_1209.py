# Generated by Django 2.0.4 on 2018-05-07 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesstoken',
            name='client_id',
            field=models.CharField(default='', max_length=64, verbose_name='Client ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='accesstoken',
            name='client_secret',
            field=models.CharField(default='', max_length=64, verbose_name='Client Secret'),
            preserve_default=False,
        ),
    ]
