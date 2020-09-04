# Generated by Django 3.1 on 2020-08-31 11:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import stdimage.models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_follow'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', stdimage.models.StdImageField(upload_to='images/')),
                ('content', models.CharField(blank=True, default=None, max_length=140, null=True)),
                ('share_id', models.IntegerField(default=-1)),
                ('good_count', models.IntegerField(default=0)),
                ('share_count', models.IntegerField(default=0)),
                ('pub_date', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_owner', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-pub_date',),
            },
        ),
    ]