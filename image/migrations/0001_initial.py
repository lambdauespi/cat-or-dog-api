# Generated by Django 3.0.3 on 2020-02-19 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.CharField(default='server/default/default_error.jpg', max_length=400)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
