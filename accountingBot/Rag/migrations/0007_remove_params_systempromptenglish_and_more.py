# Generated by Django 4.1 on 2024-11-15 09:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Rag', '0006_delete_accounting_delete_taxes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='params',
            name='SystemPromptEnglish',
        ),
        migrations.RemoveField(
            model_name='params',
            name='SystemPromptGerman',
        ),
    ]
