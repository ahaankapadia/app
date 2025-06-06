# Generated by Django 5.1.1 on 2025-04-04 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inspectionApp', '0023_remove_schoolinspection_school_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recordsinspectiondata',
            name='all_halal_documents_posted',
            field=models.BooleanField(default=False, verbose_name='Are all three documents (Halal Certificate, Approved Items list, and Serving Menu list) posted together and visible?'),
        ),
        migrations.AlterField(
            model_name='recordsinspectiondata',
            name='failed_food_safety_inspection',
            field=models.BooleanField(default=False, verbose_name='Has the school ever failed a food safety inspection?'),
        ),
        migrations.AlterField(
            model_name='recordsinspectiondata',
            name='halal_approved_items_visible',
            field=models.BooleanField(default=False, verbose_name='Is the latest Halal Approved Items list posted in the kitchen?'),
        ),
        migrations.AlterField(
            model_name='recordsinspectiondata',
            name='halal_certification_visible',
            field=models.BooleanField(default=False, verbose_name='Is the Halal Certification posted and visible in the kitchen?'),
        ),
        migrations.AlterField(
            model_name='recordsinspectiondata',
            name='halal_menu_visible',
            field=models.BooleanField(default=False, verbose_name='Is the latest Halal Serving Menu list posted in the kitchen?'),
        ),
    ]
