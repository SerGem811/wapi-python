# Generated by Django 3.0.2 on 2020-01-05 00:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authtoken', '0002_auto_20160226_1747'),
    ]

    operations = [
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('profile_path', models.CharField(blank=True, max_length=255, null=True)),
                ('token', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authtoken.Token')),
            ],
        ),
    ]
