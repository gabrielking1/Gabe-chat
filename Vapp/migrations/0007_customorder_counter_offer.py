# Generated by Django 5.0.7 on 2024-07-31 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Vapp", "0006_customorder_proposed_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="customorder",
            name="counter_offer",
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
