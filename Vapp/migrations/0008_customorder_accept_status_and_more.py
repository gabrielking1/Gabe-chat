# Generated by Django 5.0.7 on 2024-08-01 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Vapp", "0007_customorder_counter_offer"),
    ]

    operations = [
        migrations.AddField(
            model_name="customorder",
            name="accept_status",
            field=models.CharField(
                choices=[("Yes", "Yes"), ("No", "No"), ("Pending", "Pending")],
                default="Pending",
                max_length=15,
            ),
        ),
        migrations.AlterField(
            model_name="customorder",
            name="counter_offer",
            field=models.BooleanField(default=False),
        ),
    ]
