# Generated by Django 2.0.4 on 2018-05-18 16:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20180518_1251'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='botmergedslot',
            options={'ordering': ['-confidence'], 'verbose_name': '词槽列表', 'verbose_name_plural': '词槽列表'},
        ),
    ]