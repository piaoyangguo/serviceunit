# Generated by Django 2.0.4 on 2018-05-21 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20180518_1604'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='intent',
            name='session',
        ),
        migrations.AddField(
            model_name='intent',
            name='user_id',
            field=models.CharField(default='', max_length=32, verbose_name='用户ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='intent',
            name='current_qu_intent',
            field=models.CharField(max_length=20, verbose_name='当前意图'),
        ),
        migrations.AlterField(
            model_name='intent',
            name='interval',
            field=models.CharField(blank=True, max_length=40, verbose_name='时间段'),
        ),
        migrations.DeleteModel(
            name='Session',
        ),
    ]
