# Generated by Django 4.1 on 2024-10-30 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Accounting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SystemPromptGerman', models.TextField()),
                ('SystemPromptEnglish', models.TextField()),
                ('temperature', models.FloatField()),
                ('max_tokens', models.IntegerField(default=2000)),
            ],
        ),
        migrations.CreateModel(
            name='ChatHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('response', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('conversation_id', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Params',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SystemPromptGerman', models.TextField()),
                ('SystemPromptEnglish', models.TextField()),
                ('temperature', models.FloatField()),
                ('max_tokens', models.IntegerField(default=2000)),
            ],
        ),
        migrations.CreateModel(
            name='Taxes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SystemPromptGerman', models.TextField()),
                ('SystemPromptEnglish', models.TextField()),
                ('temperature', models.FloatField()),
                ('max_tokens', models.IntegerField(default=2000)),
            ],
        ),
    ]
