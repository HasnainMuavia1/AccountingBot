# Generated by Django 4.1 on 2024-11-06 18:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Rag', '0003_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Accounting',
        ),
        migrations.RemoveField(
            model_name='chathistory',
            name='session',
        ),
        migrations.DeleteModel(
            name='Params',
        ),
        migrations.DeleteModel(
            name='Taxes',
        ),
        migrations.DeleteModel(
            name='ChatHistory',
        ),
        migrations.DeleteModel(
            name='ChatSession',
        ),
    ]
