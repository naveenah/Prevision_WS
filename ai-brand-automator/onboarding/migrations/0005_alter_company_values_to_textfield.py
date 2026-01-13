# Generated manually to change values field from JSONField to TextField

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("onboarding", "0004_company_demographics_company_desired_outcomes_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="values",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Comma-separated list of core values",
            ),
        ),
    ]
