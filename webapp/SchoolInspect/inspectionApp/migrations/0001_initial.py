# Generated by Django 5.1.1 on 2025-03-24 15:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolInspection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school_code', models.CharField(max_length=100, unique=True, verbose_name='School Code (SF Code)')),
                ('school_name', models.CharField(max_length=100, verbose_name='School Name')),
                ('school_address', models.CharField(blank=True, max_length=100, null=True, verbose_name='School Address')),
                ('street_address', models.CharField(blank=True, max_length=100, null=True, verbose_name='Street Address')),
                ('street_address2', models.CharField(blank=True, max_length=100, null=True, verbose_name='Street Address Line 2')),
                ('state', models.CharField(blank=True, max_length=100, null=True, verbose_name='State')),
                ('zip_code', models.CharField(blank=True, max_length=100, null=True, verbose_name='Zip Code')),
                ('inspection_type', models.CharField(choices=[('Recertification', 'Recertification (Annual)'), ('Initial', 'Initial Certification (New School)'), ('Unannounced', 'Unannounced'), ('Remediation', 'Remediation')], max_length=50, verbose_name='Type of Inspection')),
                ('inspector_status', models.CharField(choices=[('Certified', 'Certified Inspector'), ('Trainee', 'Trainee')], max_length=50, verbose_name='Inspector Status')),
                ('other_schools_attached', models.BooleanField(default=False, verbose_name='Are there other schools attached to this building?')),
                ('kitchen_floor', models.CharField(blank=True, max_length=50, null=True, verbose_name='What floor is the Kitchen located on?')),
                ('general_notes', models.TextField(blank=True, null=True, verbose_name='General Notes')),
                ('security_asked_id', models.BooleanField(default=False, verbose_name='Did Security ask for your I.D?')),
                ('security_asked_vaccination', models.BooleanField(default=False, verbose_name='Did Security ask for proof of Vaccination?')),
                ('signed_in_front_desk', models.BooleanField(default=False, verbose_name='Did you sign in at the front desk with security?')),
                ('messaged_supervisor', models.BooleanField(default=False, verbose_name='Did you message your supervisor the time that you officially signed in at the security desk log-in book?')),
                ('signed_in_kitchen_log', models.BooleanField(default=False, verbose_name="Did you sign into the Kitchen's Visitor Log book?")),
                ('check_in_notes', models.TextField(blank=True, null=True, verbose_name='Check-in Notes')),
                ('staff_list_provided', models.CharField(blank=True, choices=[('Staff list of all current employees', 'Staff list of all current employees'), ('HACCP inspection provided', 'HACCP inspection provided'), ('DOH inspection provided', 'DOH inspection provided'), ('Latest Halal approved items list posted', 'Latest Halal approved items list posted'), ('Halal menu list posted', 'Halal menu list posted'), ('Halal Certification posted', 'Halal Certification posted')], max_length=2000, null=True, verbose_name='Documentation provided')),
                ('breakfast_start_time', models.TimeField(blank=True, null=True, verbose_name='Breakfast start time')),
                ('breakfast_end_time', models.TimeField(blank=True, null=True, verbose_name='Breakfast end time')),
                ('lunch_start_time', models.TimeField(blank=True, null=True, verbose_name='Lunch start time')),
                ('lunch_end_time', models.TimeField(blank=True, null=True, verbose_name='Lunch end time')),
                ('breakfast_students_count', models.PositiveIntegerField(blank=True, null=True, verbose_name='Number of students served breakfast')),
                ('lunch_students_count', models.PositiveIntegerField(blank=True, null=True, verbose_name='Number of students served lunch')),
                ('total_students_registered', models.PositiveIntegerField(blank=True, null=True, verbose_name='Total number of students registered in the school')),
                ('halal_consumption_percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Percentage of students consuming Halal')),
            ],
        ),
        migrations.CreateModel(
            name='PreparationInspectionData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_serial_number', models.CharField(blank=True, max_length=100, null=True, verbose_name='Halal Machine S/N')),
                ('machine_type', models.CharField(blank=True, choices=[('Refrigerator', 'Refrigerator'), ('Freezer', 'Freezer'), ('Oven', 'Oven'), ('Warmer', 'Warmer'), ('Warmer-Oven Hybrid', 'Warmer-Oven Hybrid'), ('Steamer-Oven box', 'Steamer-Oven box'), ('Steamer Table', 'Steamer Table'), ('Milk Chest', 'Milk Chest'), ('Self-Serve merchandiser', 'Self-Serve merchandiser'), ('Hot Food merchandiser', 'Hot Food merchandiser')], max_length=50, null=True, verbose_name='Machine Type')),
                ('machine_designation', models.CharField(blank=True, choices=[('Halal', 'Halal'), ('Mixed-use', 'Mixed-use'), ('N/A', 'N/A')], max_length=50, null=True, verbose_name='Designation')),
                ('swab_test_result', models.CharField(blank=True, choices=[('Pass', 'Pass'), ('Fail', 'Fail'), ('N/A', 'N/A')], max_length=50, null=True, verbose_name='Swab Test')),
                ('countertop', models.CharField(blank=True, choices=[('Halal', 'Halal'), ('Mixed-use', 'Mixed-use'), ('N/A', 'N/A')], max_length=50, null=True, verbose_name='Countertop')),
                ('countertop_no_pathogens', models.CharField(blank=True, choices=[('Water', 'Water'), ('Water & Soap', 'Water & Soap'), ('Water & Bleach', 'Water & Bleach'), ('Other', 'Other')], max_length=50, null=True, verbose_name='If jointly used with non-halal products, how does the staff ensure no pathogens from non-halal remain?')),
                ('sink', models.CharField(blank=True, choices=[('Halal', 'Halal'), ('Mixed-use', 'Mixed-use'), ('N/A', 'N/A')], max_length=50, null=True, verbose_name='Sink')),
                ('sink_no_pathogens', models.CharField(blank=True, choices=[('Water', 'Water'), ('Water & Soap', 'Water & Soap'), ('Water & Bleach', 'Water & Bleach'), ('Other', 'Other')], max_length=50, null=True, verbose_name='If jointly used with non-halal products, how does the staff ensure no pathogens from non-halal remain?')),
                ('utensils_quantity', models.IntegerField(blank=True, null=True, verbose_name='Quantity of Utensils')),
                ('utensils_type', models.CharField(blank=True, choices=[('Steamer Pans (deep)', 'Steamer Pans (deep)'), ('Oven/Warmer Pans (Shallow)', 'Oven/Warmer Pans (Shallow)'), ('Serving Tools', 'Serving Tools'), ('Round Pots', 'Round Pots')], max_length=50, null=True, verbose_name='Utensils Type')),
                ('utensils_designation', models.CharField(blank=True, choices=[('Halal', 'Halal'), ('Mixed-use', 'Mixed-use'), ('N/A', 'N/A')], max_length=50, null=True, verbose_name='Utensils Designation')),
                ('utensils_swab_test', models.CharField(blank=True, choices=[('Pass', 'Pass'), ('Fail', 'Fail'), ('N/A', 'N/A')], max_length=50, null=True, verbose_name='Utensils Swab Test')),
                ('machine_cleaned_before_use', models.CharField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No'), ('Pending', 'Pending')], max_length=50, null=True, verbose_name='Was the machine cleaned before use?')),
                ('separate_utensils_for_halal', models.CharField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No'), ('Pending', 'Pending')], max_length=50, null=True, verbose_name='Are there separate utensils used for Halal food preparation?')),
                ('cutting_boards_designated', models.CharField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No'), ('Pending', 'Pending')], max_length=50, null=True, verbose_name='Are there designated cutting boards for Halal food?')),
                ('halal_meals_prepared_first', models.CharField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No'), ('Pending', 'Pending')], max_length=50, null=True, verbose_name='Are Halal meals prepared first before non-Halal items?')),
                ('halal_items_in_halal_oven', models.BooleanField(default=False, verbose_name='Halal-approved items in Halal-designated ovens?')),
                ('halal_items_in_non_halal_oven', models.BooleanField(default=False, verbose_name='Halal-approved items in non-Halal ovens?')),
                ('non_halal_items_in_halal_oven', models.BooleanField(default=False, verbose_name='Non-Halal items in Halal ovens?')),
                ('halal_items_on_unlabeled_countertop', models.BooleanField(default=False, verbose_name='Halal products on non-labeled countertops?')),
                ('halal_items_outside_designated_countertop', models.BooleanField(default=False, verbose_name='Halal products prepared outside designated countertops?')),
                ('cross_contamination_prevention', models.TextField(blank=True, null=True, verbose_name='How does staff prevent cross-contamination on shared countertops?')),
                ('utensils_stored_properly', models.BooleanField(default=False, verbose_name='Are utensils stored in a designated Halal area/container?')),
                ('utensils_labeled_exclusively', models.BooleanField(default=False, verbose_name='Are utensils labeled for exclusive Halal use?')),
                ('staff_using_halal_utensils', models.BooleanField(default=False, verbose_name='Is staff using Halal-designated utensils?')),
                ('sign_freezer', models.BooleanField(default=False, verbose_name='Clear Halal sign for Freezer?')),
                ('sign_refrigerator', models.BooleanField(default=False, verbose_name='Clear Halal sign for Refrigerator?')),
                ('sign_oven', models.BooleanField(default=False, verbose_name='Clear Halal sign for Oven?')),
                ('sign_warmer', models.BooleanField(default=False, verbose_name='Clear Halal sign for Warmer?')),
                ('sign_countertop', models.BooleanField(default=False, verbose_name='Clear Halal sign for Counter Top?')),
                ('sign_sink', models.BooleanField(default=False, verbose_name='Clear Halal sign for Sink?')),
                ('sign_halal_meal_available', models.BooleanField(default=False, verbose_name="'Halal Meal Available Upon Request' Sign?")),
                ('incident', models.TextField(blank=True, null=True, verbose_name='Incident')),
                ('remedy', models.TextField(blank=True, null=True, verbose_name='Remedy')),
                ('conclusion', models.TextField(blank=True, null=True, verbose_name='Conclusion')),
                ('preparation_notes', models.TextField(blank=True, null=True, verbose_name='Preparation Inspection Notes')),
                ('additional_notes', models.TextField(blank=True, null=True, verbose_name='Additional Notes')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='preparation_inspections', to='inspectionApp.schoolinspection', to_field='school_code', verbose_name='School Code (SF Code)')),
            ],
        ),
        migrations.CreateModel(
            name='FreezerInspectionData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('freezer_clean', models.CharField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No'), ('Pending', 'Pending')], max_length=50, null=True, verbose_name='Was the Freezer area clean?')),
                ('refrigerator_clean', models.CharField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No'), ('Pending', 'Pending')], max_length=50, null=True, verbose_name='Was the Refrigerator area clean?')),
                ('halal_stored_separately', models.CharField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No'), ('Pending', 'Pending')], max_length=50, null=True, verbose_name='Were the Halal products stored separately from non-Halal?')),
                ('halal_in_boxes', models.CharField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No'), ('Pending', 'Pending')], max_length=50, null=True, verbose_name='Halal products remain in boxes/pallets until fully depleted?')),
                ('is_halal_meat_mixed_with_halal_non_meat', models.BooleanField(default=False, verbose_name='Is the staff mixing Halal-meat with Halal non-meat items in the Halal Freezer?')),
                ('is_halal_non_meat_bagged', models.BooleanField(default=False, verbose_name='If they are mixing Halal-meat with Halal non-meat items in the Halal Freezer, are they bagging the non-meat Halal?')),
                ('is_halal_meat_mixed_with_non_halal', models.BooleanField(default=False, verbose_name='Is the staff mixing Halal-meat with non-Halal items in any freezer?')),
                ('halal_boxes_clearly_labeled', models.BooleanField(default=False, verbose_name='Based on your inspection, were the Halal boxes clearly labeled?')),
                ('incident', models.TextField(blank=True, null=True, verbose_name='Incident')),
                ('remedy', models.TextField(blank=True, null=True, verbose_name='Remedy')),
                ('conclusion', models.TextField(blank=True, null=True, verbose_name='Conclusion')),
                ('storage_notes', models.TextField(blank=True, null=True, verbose_name='Refrigerator and Freezer Inspection Notes')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='freezer_inspections', to='inspectionApp.schoolinspection', to_field='school_code', verbose_name='School Code (SF Code)')),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryInspectionData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food_delivery_location', models.CharField(blank=True, max_length=255, null=True, verbose_name='Where is the food delivered into the facility?')),
                ('halal_food_supplier', models.CharField(blank=True, max_length=255, null=True, verbose_name='Which company delivers the Halal food supplies?')),
                ('halal_boxes_labeled', models.CharField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No'), ('Pending', 'Pending')], max_length=50, null=True, verbose_name='Are the Halal boxes clearly labeled?')),
                ('delivery_notes', models.TextField(blank=True, null=True, verbose_name='Delivery Inspection Notes')),
                ('incident', models.TextField(blank=True, null=True, verbose_name='Incident')),
                ('remedy', models.TextField(blank=True, null=True, verbose_name='Remedy')),
                ('conclusion', models.TextField(blank=True, null=True, verbose_name='Conclusion')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_inspections', to='inspectionApp.schoolinspection', to_field='school_code', verbose_name='School Code (SF Code)')),
            ],
        ),
        migrations.CreateModel(
            name='BathroomInspectionData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bathroom_clean', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No'), ('Pending', 'Pending')], max_length=50, verbose_name='Are the bathrooms clean?')),
                ('paper_towels_available', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No'), ('Partial', 'Partial')], max_length=50, verbose_name='Are paper towels available in all bathrooms?')),
                ('hand_dryers_functioning', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No'), ('Some are not working', 'Some are not working')], max_length=50, verbose_name='Are the hand dryers functioning properly?')),
                ('bad_odor_present', models.BooleanField(verbose_name='Is there any bad odor in the bathroom?')),
                ('clogged_sinks_or_toilets', models.BooleanField(verbose_name='Are there any clogged sinks or toilets?')),
                ('graffiti_present', models.BooleanField(verbose_name='Is there any graffiti or vandalism in the bathrooms?')),
                ('bathroom_notes', models.TextField(blank=True, null=True, verbose_name='Additional Bathroom Inspection Notes')),
                ('incident', models.TextField(blank=True, null=True, verbose_name='Incident')),
                ('remedy', models.TextField(blank=True, null=True, verbose_name='Remedy')),
                ('conclusion', models.TextField(blank=True, null=True, verbose_name='Conclusion')),
                ('kitchen_staff_bathroom', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], max_length=3, verbose_name='Does Kitchen staff have a separate bathroom?')),
                ('mens_staff_bathroom', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], max_length=3, verbose_name="Men's Staff Bathroom available?")),
                ('womens_staff_bathroom', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], max_length=3, verbose_name="Women's Staff Bathroom available?")),
                ('adequate_soap', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No'), ('Other', 'Other')], max_length=10, verbose_name='Does the bathroom have adequate soap available?')),
                ('faucets_running', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No'), ('Other', 'Other')], max_length=10, verbose_name='Are the Faucets running properly?')),
                ('restroom_cleaner', models.CharField(choices=[('Staff', 'Staff'), ('Janitor', 'Janitor')], max_length=10, verbose_name='Who cleans the restrooms?')),
                ('cleaning_frequency', models.CharField(choices=[('Once a day', 'Once a day'), ('Twice', 'Twice'), ('Other', 'Other')], max_length=10, verbose_name='How Often is the bathroom cleaned?')),
                ('wash_hands_signs', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], max_length=3, verbose_name="Signs for 'Wash Hands' visible?")),
                ('remove_apron_signs', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], max_length=3, verbose_name="Signs for 'Remove Apron' visible?")),
                ('ventilation', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], max_length=3, verbose_name='Is the bathroom properly ventilated?')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bathroom_inspections', to='inspectionApp.schoolinspection', to_field='school_code', verbose_name='School Code (SF Code)')),
            ],
        ),
        migrations.CreateModel(
            name='ServingInspectionData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('breakfast_start_time', models.TimeField(blank=True, null=True, verbose_name='Breakfast Serving Start Time')),
                ('breakfast_end_time', models.TimeField(blank=True, null=True, verbose_name='Breakfast Serving End Time')),
                ('lunch_start_time', models.TimeField(blank=True, null=True, verbose_name='Lunch Serving Start Time')),
                ('lunch_end_time', models.TimeField(blank=True, null=True, verbose_name='Lunch Serving End Time')),
                ('students_served_breakfast', models.PositiveIntegerField(blank=True, null=True, verbose_name='Number of Students Served Breakfast')),
                ('students_served_lunch', models.PositiveIntegerField(blank=True, null=True, verbose_name='Number of Students Served Lunch')),
                ('total_registered_students', models.PositiveIntegerField(blank=True, null=True, verbose_name='Total Registered Students in School')),
                ('halal_consumption_percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Percentage of Students Consuming Halal Food')),
                ('halal_serving_location', models.CharField(choices=[('In a Halal designated serving location', 'In a Halal designated serving location'), ('In a Halal/non-Halal mixed serving location', 'In a Halal/non-Halal mixed serving location')], max_length=255, verbose_name='Where is the Halal product served?')),
                ('halal_positioning', models.CharField(choices=[('Halal product is clear for consumer to see and choose as an option', 'Halal product is clear for consumer to see and choose as an option'), ('Halal product is not clearly visible for consumers to see or choose', 'Halal product is not clearly visible for consumers to see or choose')], max_length=255, verbose_name="What about the Halal product's positioning in the serving line? Is the Halal food option clearly visible for the students to see and choose as an equal option against the non-Halal options?")),
                ('halal_sign_visible', models.BooleanField(blank=True, null=True, verbose_name="Is there a visible 'Halal' sign in the serving area?")),
                ('halal_sign_type', models.CharField(choices=[('plastic_stand', 'Plastic stand, 8.5" x 11" paper (recommended)'), ('wall_posted', 'Posted on a wall near the serving area'), ('large_sign', 'Large sign taped to glass/metal'), ('small_label', 'Small label taped to glass/metal'), ('none', 'None')], default='none', max_length=50, verbose_name="What type of 'Halal' sign is at the serving area?")),
                ('halal_product_serving_method', models.CharField(choices=[('Pre-Plated', 'Pre-Plated'), ('Self-Serve', 'Self-Serve'), ('Served by Staff', 'Served by Staff'), ('Other', 'Other')], max_length=50, verbose_name='Halal Product Serving Method')),
                ('serving_service_type', models.CharField(choices=[('cafeteria', 'Cafeteria-style (served by servers)'), ('buffet', 'Self-serve buffet style'), ('pre_packaged', 'Self-serve pre-packaged stations'), ('vending_machine', 'Vending machine style'), ('other', 'Other')], default='none', max_length=255, verbose_name="If 'Other', please specify")),
                ('separate_gloves', models.BooleanField(default=False, verbose_name='Are they using separate gloves when touching Halal food?')),
                ('separate_utensils', models.BooleanField(default=False, verbose_name='Are they using separate Serving Utensils for the Halal product?')),
                ('proper_lighting', models.BooleanField(default=False, verbose_name='Is the serving area properly lit?')),
                ('food_safety_gear_required', models.BooleanField(blank=True, null=True, verbose_name='Are staff required to wear food safety gear (e.g., gloves) while serving Halal food?')),
                ('separate_serving_utensils', models.BooleanField(blank=True, null=True, verbose_name='Are separate serving utensils used for Halal food?')),
                ('serving_area_properly_lit', models.BooleanField(blank=True, null=True, verbose_name='Is the serving area properly lit?')),
                ('serving_line_sign', models.BooleanField(default=False, verbose_name='Clear Halal-sign for Serving Line (Optional)')),
                ('plastic_stand_sign', models.BooleanField(default=False, verbose_name='Clear Halal-sign for Plastic Stand (Strongly Recommended)')),
                ('sign_queue_line', models.BooleanField(blank=True, null=True, verbose_name='Clear Halal sign for Queue Line (optional)')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Additional Notes')),
                ('incident', models.TextField(blank=True, null=True, verbose_name='Incident')),
                ('remedy', models.TextField(blank=True, null=True, verbose_name='Remedy')),
                ('conclusion', models.TextField(blank=True, null=True, verbose_name='Conclusion')),
                ('serving_notes', models.TextField(blank=True, null=True, verbose_name='Additional Serving Inspection Notes')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='serving_inspections', to='inspectionApp.schoolinspection', to_field='school_code', verbose_name='School Code (SF Code)')),
            ],
        ),
        migrations.CreateModel(
            name='StorageInspectionData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kitchen_cleaning_frequency', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('After Each Shift', 'After Each Shift'), ('Other', 'Other')], max_length=50, verbose_name='How often is the kitchen cleaned?')),
                ('kitchen_cleaning_frequency_other', models.CharField(blank=True, max_length=255, null=True, verbose_name="If 'Other', please describe")),
                ('halal_trays_washed_separately', models.BooleanField(verbose_name='Are Halal Trays washed separately from non-Halal?')),
                ('halal_trays_washing_other', models.CharField(blank=True, max_length=255, null=True, verbose_name="If 'Other', please describe")),
                ('halal_serving_utensils_washed_separately', models.BooleanField(verbose_name='Are Halal Serving Utensils washed separately?')),
                ('halal_utensils_trays_halal_sink', models.BooleanField(verbose_name='Are Halal Utensils/Trays washed in a Halal-Designated sink?')),
                ('sanitization_chemicals_used', models.CharField(choices=[('Water only ', 'Water only'), ('Water & Soap', 'Water & Soap'), ('Water & Bleach', 'Water & Bleach'), ('Other', 'Other')], max_length=50, verbose_name='What chemicals are used to sanitize?')),
                ('facility_bad_odors', models.BooleanField(verbose_name='Does the facility have any bad odors due to poor ventilation?')),
                ('garbage_emptying_frequency', models.CharField(choices=[('Daily', 'Daily'), ('Every Shift', 'Every Shift'), ('Weekly', 'Weekly'), ('Other', 'Other')], max_length=50, verbose_name='How often are the garbage cans emptied?')),
                ('garbage_emptying_frequency_other', models.CharField(blank=True, max_length=255, null=True, verbose_name="If 'Other', please describe")),
                ('waste_management_notes', models.TextField(blank=True, null=True, verbose_name='Additional Waste Management Notes')),
                ('incident', models.TextField(blank=True, null=True, verbose_name='Incident')),
                ('remedy', models.TextField(blank=True, null=True, verbose_name='Remedy')),
                ('conclusion', models.TextField(blank=True, null=True, verbose_name='Conclusion')),
                ('halal_pots_separate', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No'), ('Other', 'Other')], max_length=10, verbose_name='Are Halal-designated Pots, Pans, Trays washed separately from non-Halal?')),
                ('utensil_sanitization_method', models.CharField(choices=[('Water & Soap', 'Water & Soap'), ('Water & Bleach', 'Water & Bleach'), ('Other', 'Other')], max_length=50, verbose_name='If Utensils are jointly used with non-halal products, what is used to wash them?')),
                ('storage_notes', models.TextField(blank=True, null=True, verbose_name='Additional Storage Notes')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='storage_inspections', to='inspectionApp.schoolinspection', to_field='school_code', verbose_name='School Code (SF Code)')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school_name', models.CharField(blank=True, max_length=255)),
                ('is_inspector', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
