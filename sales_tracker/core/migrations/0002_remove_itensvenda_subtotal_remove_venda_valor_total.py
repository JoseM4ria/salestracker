# Generated by Django 5.1.3 on 2024-11-24 21:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="itensvenda",
            name="subtotal",
        ),
        migrations.RemoveField(
            model_name="venda",
            name="valor_total",
        ),
    ]
