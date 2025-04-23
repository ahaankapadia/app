from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from decimal import Decimal
from django.core.files.base import ContentFile
import base64
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school_name = models.CharField(max_length=255, blank=True)
    is_inspector = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.school_name:
            self.school_name = "Default School"
        super().save(*args, **kwargs)
    def __str__(self):
        return self.school_name 
    

class UserLogData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)

    def duration(self):
        """Calculate time gap between login and logout in hh:mm:ss format."""
        if self.login_time and self.logout_time:  # Ensure both times exist
            total_seconds = int((self.logout_time - self.login_time).total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours}h {minutes}m {seconds}s"
        return "Active"

    def __str__(self):
        return f"{self.user.username} - {self.login_time or 'Unknown'} to {self.logout_time or 'Active'}"

class MonthlySalaryCalculation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    minutes = models.PositiveIntegerField()
    salary_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    final_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        self.final_salary = (Decimal(self.minutes) / Decimal(60)) * self.salary_per_month
        super().save(*args, **kwargs)

class HourlySalaryCalculation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_hours = models.PositiveIntegerField()
    salary_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    final_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        self.final_salary = Decimal(self.total_hours) * self.salary_per_hour
        super().save(*args, **kwargs)

         
from django.db import models

class SchoolInspection(models.Model):
    """
    Combined model replacing GeneralInformation and InspectionChecklist
    """
    # Common identifiers
    school_code = models.CharField(max_length=100, unique=True, verbose_name="School Code (SF Code)")
    
    # Inspection metadata
    INSPECTION_TYPES = [
        ('Recertification', 'Recertification (Annual)'),
        ('Initial', 'Initial Certification (New School)'),
        ('Unannounced', 'Unannounced'),
        ('Remediation', 'Remediation'),
    ]
    INSPECTOR_STATUSES = [
        ('Certified', 'Certified Inspector'),
        ('Trainee', 'Trainee'),
    ]
    inspection_type = models.CharField(blank=True, null=True,max_length=50, choices=INSPECTION_TYPES, verbose_name="Type of Inspection")
    inspector_status = models.CharField(blank=True, null=True,max_length=50, choices=INSPECTOR_STATUSES, verbose_name="Inspector Status")
    
    # School-specific information
    other_schools_attached = models.BooleanField(blank=True, null=True, verbose_name="Are there other schools attached to this building?")
    kitchen_floor = models.CharField(max_length=50, verbose_name="What floor is the Kitchen located on?", blank=True, null=True)
    general_notes = models.TextField(blank=True, null=True, verbose_name="General Notes")

    # Check-in information
    security_asked_id = models.BooleanField(blank=True, null=True, verbose_name="Did Security ask for your I.D?")
    security_asked_vaccination = models.BooleanField(blank=True, null=True, verbose_name="Did Security ask for proof of Vaccination?")
    signed_in_front_desk = models.BooleanField(blank=True, null=True, verbose_name="Did you sign in at the front desk with security?")
    messaged_supervisor = models.BooleanField(blank=True, null=True, verbose_name="Did you message your supervisor the time that you officially signed in at the security desk log-in book?")
    signed_in_kitchen_log = models.BooleanField(blank=True, null=True, verbose_name="Did you sign into the Kitchen's Visitor Log book?")
    check_in_notes = models.TextField(blank=True, null=True, verbose_name="Check-in Notes")
    
    # Documentation and schedule information (from InspectionChecklist)
    staff_list_provided = models.CharField(max_length=2000, blank=True, null=True, choices=[
        ('Staff list of all current employees', 'Staff list of all current employees'),
        ('HACCP inspection provided', 'HACCP inspection provided'),
        ('DOH inspection provided', 'DOH inspection provided'),
        ('Latest Halal approved items list posted', 'Latest Halal approved items list posted'),
        ('Halal menu list posted', 'Halal menu list posted'),
        ('Halal Certification posted', 'Halal Certification posted'),
    ], verbose_name="Documentation provided")
    
    # Meal schedule information
    breakfast_start_time = models.TimeField(verbose_name="Breakfast start time", blank=True, null=True)
    breakfast_end_time = models.TimeField(verbose_name="Breakfast end time", blank=True, null=True)
    lunch_start_time = models.TimeField(verbose_name="Lunch start time", blank=True, null=True)
    lunch_end_time = models.TimeField(verbose_name="Lunch end time", blank=True, null=True)
    breakfast_students_count = models.PositiveIntegerField(null=True, blank=True,verbose_name="Number of students served breakfast")
    lunch_students_count = models.PositiveIntegerField(null=True, blank=True,verbose_name="Number of students served lunch")
    total_students_registered = models.PositiveIntegerField(null=True, blank=True,verbose_name="Total number of students registered in the school")
    halal_consumption_percentage = models.DecimalField(blank=True, null=True,max_digits=5, decimal_places=2, verbose_name="Percentage of students consuming Halal")
    
    def __str__(self):
        return self.school_code

class DeliveryInspectionData(models.Model):
    """
    Combined model replacing DeliveryInspection and DeliveryChecklist
    """
    school = models.ForeignKey(
        SchoolInspection, 
        on_delete=models.CASCADE, 
        related_name='delivery_inspections',
        to_field='school_code',
        verbose_name="School Code (SF Code)"
    )
    
    # From DeliveryInspection
    food_delivery_location = models.CharField(max_length=255, verbose_name="Where is the food delivered into the facility?", blank=True, null=True)
    halal_food_supplier = models.CharField(max_length=255, verbose_name="Which company delivers the Halal food supplies?", blank=True, null=True)
    halal_boxes_labeled = models.CharField(max_length=50, choices=[('Yes', 'Yes'), ('No', 'No'), ('Pending', 'Pending')], 
                                          verbose_name="Are the Halal boxes clearly labeled?", blank=True, null=True)
    delivery_notes = models.TextField(blank=True, null=True, verbose_name="Delivery Inspection Notes")
    
    # From DeliveryChecklist
    incident = models.TextField(blank=True, null=True, verbose_name="Incident")
    remedy = models.TextField(blank=True, null=True, verbose_name="Remedy")
    conclusion = models.TextField(blank=True, null=True, verbose_name="Conclusion")
    
    def __str__(self):
        return f"Delivery inspection for {self.school}"

class FreezerInspectionData(models.Model):
    """
    Combined model replacing RefrigeratorAndFreezer and FreezerChecklist
    """
    school = models.ForeignKey(
        SchoolInspection, 
        on_delete=models.CASCADE, 
        related_name='freezer_inspections',
        to_field='school_code',
        verbose_name="School Code (SF Code)"
    )
    
    # Common fields between both models
    freezer_clean = models.CharField(max_length=50, choices=[('Yes', 'Yes'), ('No', 'No'), ('Pending', 'Pending')], 
                                    verbose_name="Was the Freezer area clean?", blank=True, null=True)
    refrigerator_clean = models.CharField(max_length=50, choices=[('Yes', 'Yes'), ('No', 'No'), ('Pending', 'Pending')], 
                                         verbose_name="Was the Refrigerator area clean?", blank=True, null=True)
    halal_stored_separately = models.CharField(max_length=50, choices=[('Yes', 'Yes'), ('No', 'No'), ('Pending', 'Pending')], 
                                              verbose_name="Were the Halal products stored separately from non-Halal?", blank=True, null=True)
    halal_in_boxes = models.CharField(max_length=50, choices=[('Yes', 'Yes'), ('No', 'No'), ('Pending', 'Pending')], 
                                     verbose_name="Halal products remain in boxes/pallets until fully depleted?", blank=True, null=True)
    
    # From FreezerChecklist
    is_halal_meat_mixed_with_halal_non_meat = models.BooleanField(default=False, verbose_name="Is the staff mixing Halal-meat with Halal non-meat items in the Halal Freezer?")
    is_halal_non_meat_bagged = models.BooleanField(default=False, verbose_name="If they are mixing Halal-meat with Halal non-meat items in the Halal Freezer, are they bagging the non-meat Halal?")
    is_halal_meat_mixed_with_non_halal = models.BooleanField(default=False, verbose_name="Is the staff mixing Halal-meat with non-Halal items in any freezer?")
    halal_boxes_clearly_labeled = models.BooleanField(default=False, verbose_name="Based on your inspection, were the Halal boxes clearly labeled?")
    
    # Inspection details
    incident = models.TextField(blank=True, null=True, verbose_name="Incident")
    remedy = models.TextField(blank=True, null=True, verbose_name="Remedy")
    conclusion = models.TextField(blank=True, null=True, verbose_name="Conclusion")
    storage_notes = models.TextField(blank=True, null=True, verbose_name="Refrigerator and Freezer Inspection Notes")
    
    def __str__(self):
        return f"Freezer inspection for {self.school}"

class PreparationInspectionData(models.Model):
    """
    Combined model replacing PreparationInspection and PreparationChecklist
    """
    school = models.ForeignKey(
        SchoolInspection, 
        on_delete=models.CASCADE, 
        related_name='preparation_inspections',
        to_field='school_code',
        verbose_name="School Code (SF Code)"
    )
    
    # Surfaces and utensils
    countertop = models.CharField(max_length=50, choices=[
        ('Halal', 'Halal'),
        ('Mixed-use', 'Mixed-use'),
        ('N/A', 'N/A')
    ], verbose_name="Countertop", blank=True, null=True)
    
    countertop_no_pathogens = models.CharField(max_length=50, choices=[
        ('Water', 'Water'),
        ('Water & Soap', 'Water & Soap'),
        ('Water & Bleach', 'Water & Bleach'),
        ('Halal Only', 'Halal Only'),
        ('Other', 'Other')
    ], verbose_name="If jointly used with non-halal products, how does the staff ensure no pathogens from non-halal remain?", blank=True, null=True)
    
    sink = models.CharField(max_length=50, choices=[
        ('Halal', 'Halal'),
        ('Mixed-use', 'Mixed-use'),
        ('N/A', 'N/A')
    ], verbose_name="Sink", blank=True, null=True)
    
    sink_no_pathogens = models.CharField(max_length=50, choices=[
        ('Water', 'Water'),
        ('Water & Soap', 'Water & Soap'),
        ('Water & Bleach', 'Water & Bleach'),
        ('Halal Only', 'Halal Only'),
        ('Other', 'Other')
    ], verbose_name="If jointly used with non-halal products, how does the staff ensure no pathogens from non-halal remain?", blank=True, null=True)
    
    # Preparation processes - from both models
    separate_utensils_for_halal = models.CharField(max_length=50, choices=[
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('Pending', 'Pending')
    ], verbose_name="Are there separate utensils used for Halal food preparation?", blank=True, null=True)
    
    cutting_boards_designated = models.CharField(max_length=50, choices=[
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('Pending', 'Pending')
    ], verbose_name="Are there designated cutting boards for Halal food?", blank=True, null=True)
    
    halal_meals_prepared_first = models.CharField(max_length=50, choices=[
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('Pending', 'Pending')
    ], verbose_name="Are Halal meals prepared first before non-Halal items?", blank=True, null=True)
    
    # From PreparationChecklist
    # Oven checks
    halal_items_in_halal_oven = models.BooleanField(default=False, verbose_name="Halal-approved items in Halal-designated ovens?")
    halal_items_in_non_halal_oven = models.BooleanField(default=False, verbose_name="Halal-approved items in non-Halal ovens?")
    non_halal_items_in_halal_oven = models.BooleanField(default=False, verbose_name="Non-Halal items in Halal ovens?")
    
    # Countertop checks
    halal_items_on_unlabeled_countertop = models.BooleanField(default=False, verbose_name="Halal products on non-labeled countertops?")
    halal_items_outside_designated_countertop = models.BooleanField(default=False, verbose_name="Halal products prepared outside designated countertops?")
    cross_contamination_prevention = models.TextField(blank=True, null=True, verbose_name="How does staff prevent cross-contamination on shared countertops?")
    
    # Utensil checks
    utensils_stored_properly = models.BooleanField(default=False, verbose_name="Are utensils stored in a designated Halal area/container?")
    utensils_labeled_exclusively = models.BooleanField(default=False, verbose_name="Are utensils labeled for exclusive Halal use?")
    staff_using_halal_utensils = models.BooleanField(default=False, verbose_name="Is staff using Halal-designated utensils?")
    
    # Signage
    sign_freezer = models.BooleanField(default=False, verbose_name="Clear Halal sign for Freezer?")
    sign_refrigerator = models.BooleanField(default=False, verbose_name="Clear Halal sign for Refrigerator?")
    sign_oven = models.BooleanField(default=False, verbose_name="Clear Halal sign for Oven?")
    sign_warmer = models.BooleanField(default=False, verbose_name="Clear Halal sign for Warmer?")
    sign_countertop = models.BooleanField(default=False, verbose_name="Clear Halal sign for Counter Top?")
    sign_sink = models.BooleanField(default=False, verbose_name="Clear Halal sign for Sink?")
    sign_halal_meal_available = models.BooleanField(default=False, verbose_name="'Halal Meal Available Upon Request' Sign?")
    
    # Inspection details
    incident = models.TextField(blank=True, null=True, verbose_name="Incident")
    remedy = models.TextField(blank=True, null=True, verbose_name="Remedy")
    conclusion = models.TextField(blank=True, null=True, verbose_name="Conclusion")
    preparation_notes = models.TextField(blank=True, null=True, verbose_name="Preparation Inspection Notes")
    additional_notes = models.TextField(blank=True, null=True, verbose_name="Additional Notes")
    
    def __str__(self):
        return f"Preparation inspection for {self.school}"

class UtensilsInspectionData(models.Model):
    """
    Combined model replacing PreparationInspection and PreparationChecklist
    """
    school = models.ForeignKey(
        SchoolInspection, 
        on_delete=models.CASCADE, 
        related_name='utensils_inspections',
        to_field='school_code',
        verbose_name="School Code (SF Code)"
    )

    # Utensils
    utensils_quantity = models.IntegerField(blank=True, null=True, verbose_name="Quantity of Utensils")
    utensils_type = models.CharField(max_length=50, choices=[
        ('Steamer Pans (deep)', 'Steamer Pans (deep)'),
        ('Oven/Warmer Pans (Shallow)', 'Oven/Warmer Pans (Shallow)'),
        ('Serving Tools', 'Serving Tools'),
        ('Round Pots', 'Round Pots'),
    ], verbose_name="Utensils Type", blank=True, null=True)
    
    utensils_designation = models.CharField(max_length=50, choices=[
        ('Halal', 'Halal'),
        ('Mixed-use', 'Mixed-use'),
        ('N/A', 'N/A')
    ], verbose_name="Utensils Designation", blank=True, null=True)
    
    utensils_swab_test = models.CharField(max_length=50, choices=[
        ('Pass', 'Pass'),
        ('Fail', 'Fail'),
        ('N/A', 'N/A')
    ], verbose_name="Utensils Swab Test", blank=True, null=True)
        
    def __str__(self):
        return f"Utensils inspection for {self.school}"

class PreparationMachine(models.Model):
    school = models.ForeignKey(
        SchoolInspection, 
        on_delete=models.CASCADE, 
        related_name='prepare_machine_inspections',
        to_field='school_code',
        verbose_name="School Code (SF Code)"
    )
    machine_serial_number = models.CharField(max_length=100, verbose_name="Machine S/N", blank=True, null=True)
    machine_type = models.CharField(max_length=50, choices=[
        ('Refrigerator', 'Refrigerator'),
        ('Freezer', 'Freezer'),
        ('Oven', 'Oven'),
        ('Warmer', 'Warmer'),
        ('Warmer-Oven Hybrid', 'Warmer-Oven Hybrid'),
        ('Steamer-Oven box', 'Steamer-Oven box'),
        ('Steamer Table', 'Steamer Table'),
        ('Milk Chest', 'Milk Chest'),
        ('Self-Serve merchandiser', 'Self-Serve merchandiser'),
        ('Hot Food merchandiser', 'Hot Food merchandiser')
    ], verbose_name="Machine Type", blank=True, null=True)
    machine_designation = models.CharField(max_length=50, choices=[
        ('Halal', 'Halal'),
        ('Mixed-use', 'Mixed-use'),
        ('N/A', 'N/A')
    ], verbose_name="Designation", blank=True, null=True)
    swab_test_result = models.CharField(max_length=50, choices=[
        ('Pass', 'Pass'),
        ('Fail', 'Fail'),
        ('N/A', 'N/A')
    ], verbose_name="Swab Test", blank=True, null=True)

    def __str__(self):
        return f"{self.machine_type} - {self.machine_serial_number}"

class ServingInspectionData(models.Model):
    """
    Combined model replacing PreparationInspection and PreparationChecklist
    """
    school = models.ForeignKey(
        SchoolInspection, 
        on_delete=models.CASCADE, 
        related_name='serving_inspections',
        to_field='school_code',
        verbose_name="School Code (SF Code)"
    )
    breakfast_start_time = models.TimeField(blank=True, null=True,verbose_name="Breakfast Serving Start Time")
    breakfast_end_time = models.TimeField(blank=True, null=True,verbose_name="Breakfast Serving End Time")

    # Lunch Serving Times
    lunch_start_time = models.TimeField(blank=True, null=True,verbose_name="Lunch Serving Start Time")
    lunch_end_time = models.TimeField(blank=True, null=True,verbose_name="Lunch Serving End Time")

    # Student Counts
    students_served_breakfast = models.PositiveIntegerField(blank=True, null=True,verbose_name="Number of Students Served Breakfast")
    students_served_lunch = models.PositiveIntegerField(blank=True, null=True,verbose_name="Number of Students Served Lunch")
    total_registered_students = models.PositiveIntegerField(blank=True, null=True,verbose_name="Total Registered Students in School")
    halal_consumption_percentage = models.DecimalField(blank=True, null=True,max_digits=5, decimal_places=2, verbose_name="Percentage of Students Consuming Halal Food")

    halal_serving_location = models.CharField(max_length=255,blank=True, null=True, choices=[('In a Halal designated serving location', 'In a Halal designated serving location'), ('In a Halal/non-Halal mixed serving location', 'In a Halal/non-Halal mixed serving location')], verbose_name="Where is the Halal product served?")
    halal_positioning = models.CharField(max_length=255,blank=True, null=True, choices=[('Halal product is clear for consumer to see and choose as an option', 'Halal product is clear for consumer to see and choose as an option'), ('Halal product is not clearly visible for consumers to see or choose', 'Halal product is not clearly visible for consumers to see or choose')], verbose_name="What about the Halal product's positioning in the serving line? Is the Halal food option clearly visible for the students to see and choose as an equal option against the non-Halal options?")
    halal_sign_visible = models.BooleanField(blank=True, null=True,verbose_name="Is there a visible 'Halal' sign in the serving area?")
    halal_sign_type = models.CharField(
        max_length=50,
        choices=[
            ('plastic_stand', 'Plastic stand, 8.5" x 11" paper (recommended)'),
            ('wall_posted', 'Posted on a wall near the serving area'),
            ('large_sign', 'Large sign taped to glass/metal'),
            ('small_label', 'Small label taped to glass/metal'),
            ('none', 'None'),
        ],
        blank=True, null=True,
        verbose_name="What type of 'Halal' sign is at the serving area?"
    )
    HALAL_SERVING_METHODS = [
        ('Pre-Plated', 'Pre-Plated'),
        ('Self-Serve', 'Self-Serve'),
        ('Served by Staff', 'Served by Staff'),
        ('Other', 'Other'),
    ]
    halal_product_serving_method = models.CharField(max_length=50,blank=True, null=True, choices=HALAL_SERVING_METHODS, verbose_name="Halal Product Serving Method")
    
    # Serving Methods
    serving_service_type = models.CharField(
        max_length=255,
        choices=[
            ('cafeteria', 'Cafeteria-style (served by servers)'),
            ('buffet', 'Self-serve buffet style'),
            ('pre_packaged', 'Self-serve pre-packaged stations'),
            ('vending_machine', 'Vending machine style'),
            ('other', 'Other'),
        ],
        blank=True, null=True,
        verbose_name="If 'Other', please specify"
    )
    separate_gloves = models.BooleanField(default=False, verbose_name="Are they using separate gloves when touching Halal food?")
    separate_utensils = models.BooleanField(default=False, verbose_name="Are they using separate Serving Utensils for the Halal product?")
    proper_lighting = models.BooleanField(default=False, verbose_name="Is the serving area properly lit?")

    food_safety_gear_required = models.BooleanField(default=False,verbose_name="Are staff required to wear food safety gear (e.g., gloves) while serving Halal food?")
    separate_serving_utensils = models.BooleanField(default=False,verbose_name="Are separate serving utensils used for Halal food?")
    serving_area_properly_lit = models.BooleanField(default=False,verbose_name="Is the serving area properly lit?")

    # Signs
    serving_line_sign = models.BooleanField(default=False, verbose_name="Clear Halal-sign for Serving Line (Optional)")
    plastic_stand_sign = models.BooleanField(default=False, verbose_name="Clear Halal-sign for Plastic Stand (Strongly Recommended)")
    sign_queue_line = models.BooleanField(default=False,verbose_name="Clear Halal sign for Queue Line (optional)")

    # Additional Notes
    notes = models.TextField(blank=True, null=True, verbose_name="Additional Notes")
    
    # Inspection details
    incident = models.TextField(blank=True, null=True, verbose_name="Incident")
    remedy = models.TextField(blank=True, null=True, verbose_name="Remedy")
    conclusion = models.TextField(blank=True, null=True, verbose_name="Conclusion")
    serving_notes = models.TextField(blank=True, null=True, verbose_name="Additional Serving Inspection Notes")
    
    def __str__(self):
        return f"Serving inspection for {self.school}"
        
        
class StorageInspectionData(models.Model):
    """
    Combined model replacing PreparationInspection and PreparationChecklist
    """
    school = models.ForeignKey(
        SchoolInspection, 
        on_delete=models.CASCADE, 
        related_name='storage_inspections',
        to_field='school_code',
        verbose_name="School Code (SF Code)"
    )
    KITCHEN_CLEANING_FREQUENCY = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('After Each Shift', 'After Each Shift'),
        ('Other', 'Other'),
    ]
    kitchen_cleaning_frequency = models.CharField(blank=True, null=True, 
        max_length=50, choices=KITCHEN_CLEANING_FREQUENCY, verbose_name="How often is the kitchen cleaned?"
    )
    kitchen_cleaning_frequency_other = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="If 'Other', please describe"
    )

    halal_trays_washed_separately = models.BooleanField(null=True, blank=True,verbose_name="Are Halal Trays washed separately from non-Halal?")
    halal_trays_washing_other = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="If 'Other', please describe"
    )

    halal_serving_utensils_washed_separately = models.BooleanField(null=True, blank=True,verbose_name="Are Halal Serving Utensils washed separately?")
    halal_utensils_trays_halal_sink = models.BooleanField(null=True, blank=True,verbose_name="Are Halal Utensils/Trays washed in a Halal-Designated sink?")

    sanitization_chemicals_used = models.CharField(max_length=50,blank=True, null=True,  choices=[
        ('Water only ', 'Water only'),
        ('Water & Soap', 'Water & Soap'),
        ('Water & Bleach', 'Water & Bleach'),
        ('Other', 'Other')
    ],verbose_name="What chemicals are used to sanitize?")

    facility_bad_odors = models.BooleanField(null=True, blank=True,verbose_name="Does the facility have any bad odors due to poor ventilation?")

    # Garbage Management
    GARBAGE_EMPTYING_FREQUENCY = [
        ('Daily', 'Daily'),
        ('Every Shift', 'Every Shift'),
        ('Weekly', 'Weekly'),
        ('Other', 'Other'),
    ]
    garbage_emptying_frequency = models.CharField(blank=True, null=True, 
        max_length=50, choices=GARBAGE_EMPTYING_FREQUENCY, verbose_name="How often are the garbage cans emptied?"
    )
    garbage_emptying_frequency_other = models.CharField(blank=True, null=True, 
        max_length=255, verbose_name="If 'Other', please describe"
    )

    # Additional Notes
    waste_management_notes = models.TextField(blank=True, null=True, verbose_name="Additional Waste Management Notes")
    
    # Inspection details
    incident = models.TextField(blank=True, null=True, verbose_name="Incident")
    remedy = models.TextField(blank=True, null=True, verbose_name="Remedy")
    conclusion = models.TextField(blank=True, null=True, verbose_name="Conclusion")
    halal_pots_separate = models.CharField(blank=True, null=True, 
        max_length=10, choices=[('Yes', 'Yes'), ('No', 'No'), ('Other', 'Other')],
        verbose_name="Are Halal-designated Pots, Pans, Trays washed separately from non-Halal?"
    )
    utensil_sanitization_method = models.CharField(blank=True, null=True, 
        max_length=50, choices=[
            ('Water & Soap', 'Water & Soap'),
            ('Water & Bleach', 'Water & Bleach'),
            ('Other', 'Other'),
        ],
        verbose_name="If Utensils are jointly used with non-halal products, what is used to wash them?"
    )

    storage_notes = models.TextField(blank=True, null=True, verbose_name="Additional Storage Notes")
    
    def __str__(self):
        return f"Storage inspection for {self.school}"
        
class BathroomInspectionData(models.Model):
    """
    Combined model replacing PreparationInspection and PreparationChecklist
    """
    school = models.ForeignKey(
        SchoolInspection, 
        on_delete=models.CASCADE, 
        related_name='bathroom_inspections',
        to_field='school_code',
        verbose_name="School Code (SF Code)"
    )
    bathroom_clean = models.CharField(max_length=50,blank=True, null=True,  choices=[
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('Pending', 'Pending')
    ], verbose_name="Are the bathrooms clean?")

    bad_odor_present = models.BooleanField(default=False,verbose_name="Is there any bad odor in the bathroom?")

    bathroom_notes = models.TextField(blank=True, null=True, verbose_name="Additional Bathroom Inspection Notes")
    
    # Inspection details
    incident = models.TextField(blank=True, null=True, verbose_name="Incident")
    remedy = models.TextField(blank=True, null=True, verbose_name="Remedy")
    conclusion = models.TextField(blank=True, null=True, verbose_name="Conclusion")
    kitchen_staff_bathroom = models.CharField(blank=True, null=True, 
        max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Does Kitchen staff have a separate bathroom?"
    )
    mens_staff_bathroom = models.CharField(blank=True, null=True, 
        max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Men's Staff Bathroom available?"
    )
    womens_staff_bathroom = models.CharField(blank=True, null=True, 
        max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Women's Staff Bathroom available?"
    )
    adequate_soap = models.CharField(blank=True, null=True, 
        max_length=10,
        choices=[("Yes", "Yes"), ("No", "No"), ("Other", "Other")],
        verbose_name="Does the bathroom have adequate soap available?",
    )
    faucets_running = models.CharField(blank=True, null=True,
        max_length=10,
        choices=[("Yes", "Yes"), ("No", "No"), ("Other", "Other")],
        verbose_name="Are the Faucets running properly?"
    )
    restroom_cleaner = models.CharField(blank=True, null=True,
        max_length=10,
        choices=[("Staff", "Staff"), ("Janitor", "Janitor")],
        verbose_name="Who cleans the restrooms?"
    )
    cleaning_frequency = models.CharField(blank=True, null=True,
        max_length=10,
        choices=[("Once a day", "Once a day"), ("Twice", "Twice"), ("Other", "Other")],
        verbose_name="How Often is the bathroom cleaned?"
    )
    wash_hands_signs = models.CharField(blank=True, null=True,
        max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Signs for 'Wash Hands' visible?"
    )
    remove_apron_signs = models.CharField(blank=True, null=True,
        max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Signs for 'Remove Apron' visible?"
    )
    ventilation = models.CharField(blank=True, null=True,
        max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Is the bathroom properly ventilated?"
    )
    
    def __str__(self):
        return f"Bathroom inspection for {self.school}"
        
class RecordsInspectionData(models.Model):
    """
    Combined model replacing PreparationInspection and PreparationChecklist
    """
    school = models.ForeignKey(
        SchoolInspection, 
        on_delete=models.CASCADE, 
        related_name='records_inspections',
        to_field='school_code',
        verbose_name="School Code (SF Code)"
    )
    last_haccp_inspection = models.DateField(blank=True, null=True, verbose_name="Last HACCP Inspection Date")
    last_doh_inspection = models.DateField(blank=True, null=True, verbose_name="Last DOH Inspection Date")
    last_halal_inspection = models.DateField(blank=True, null=True, verbose_name="Last Halal Food Inspection Date")

    failed_food_safety_inspection = models.BooleanField(null=True, blank=True,verbose_name="Has the school ever failed a food safety inspection?")

    halal_certification_visible = models.BooleanField(null=True, blank=True,verbose_name="Is the Halal Certification posted and visible in the kitchen?")
    halal_approved_items_visible = models.BooleanField(null=True, blank=True,verbose_name="Is the latest Halal Approved Items list posted in the kitchen?")
    halal_menu_visible = models.BooleanField(null=True, blank=True,verbose_name="Is the latest Halal Serving Menu list posted in the kitchen?")

    all_halal_documents_posted = models.BooleanField(null=True, blank=True,verbose_name="Are all three documents (Halal Certificate, Approved Items list, and Serving Menu list) posted together and visible?")

    inspection_notes = models.TextField(blank=True, null=True, verbose_name="Additional Notes")
    
    # Inspection details
    incident = models.TextField(blank=True, null=True, verbose_name="Incident")
    remedy = models.TextField(blank=True, null=True, verbose_name="Remedy")
    conclusion = models.TextField(blank=True, null=True, verbose_name="Conclusion")
    
    halal_inspection = models.CharField(blank=True, null=True,
        max_length=10, choices=[('date', 'Date'),
        ('na', 'N/A')], 
    )
    halal_inspection_date = models.DateField(null=True, blank=True)
    
    failed_inspection_date = models.DateField(null=True, blank=True)
    
    record_notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    
    def __str__(self):
        return f"Records inspection for {self.school}"
        
        
class EvaluationInspectionData(models.Model):
    """
    Combined model replacing PreparationInspection and PreparationChecklist
    """
    school = models.ForeignKey(
        SchoolInspection, 
        on_delete=models.CASCADE, 
        related_name='evaluation_inspections',
        to_field='school_code',
        verbose_name="School Code (SF Code)"
    )
    total_kitchen_staff = models.PositiveIntegerField(null=True, blank=True,verbose_name="What is the total number of kitchen staff (including Manager)?")
    staff_present = models.PositiveIntegerField(null=True, blank=True,verbose_name="How many staff were present?")
    staff_on_time = models.BooleanField(default=False,verbose_name="Was the staff on time for the inspection?")
    staff_cooperative = models.BooleanField(default=False,verbose_name="Was the staff cooperative?")
    staff_engaged = models.BooleanField(default=False,verbose_name="Was the staff engaged?")
    staff_allowed_inspection_time = models.BooleanField(default=False,verbose_name="Did the staff allow adequate time for inspection?")
    manager_willingness_halal = models.CharField(max_length=50,null=True, blank=True, choices=[
        ('Not at all', 'Not at all'),
        ('Slightly negative', 'Slightly negative'),
        ('Slightly inclined', 'Slightly inclined'),
        ('Very enthusiastic', 'Very enthusiastic'),
        ('Neutral', 'Neutral'),
        ('N/A', 'N/A')
    ], verbose_name="How willing does the Manager feel about integrating Halal in this Kitchen?")
    cook_willingness_halal = models.CharField(max_length=50,null=True, blank=True, choices=[
        ('Not at all', 'Not at all'),
        ('Slightly negative', 'Slightly negative'),
        ('Slightly inclined', 'Slightly inclined'),
        ('Very enthusiastic', 'Very enthusiastic'),
        ('Neutral', 'Neutral'),
        ('N/A', 'N/A')
    ], verbose_name="How willing does the Cook feel about integrating Halal in this Kitchen?")
    heavy_duty_willingness_halal = models.CharField(max_length=50,null=True, blank=True, choices=[
        ('Not at all', 'Not at all'),
        ('Slightly negative', 'Slightly negative'),
        ('Slightly inclined', 'Slightly inclined'),
        ('Very enthusiastic', 'Very enthusiastic'),
        ('Neutral', 'Neutral'),
        ('N/A', 'N/A')
    ], verbose_name="How willing does the Heavy Duty feel about integrating Halal in this Kitchen?")
    other_staff_willingness_halal = models.CharField(max_length=50,null=True, blank=True, choices=[
        ('Not at all', 'Not at all'),
        ('Slightly negative', 'Slightly negative'),
        ('Slightly inclined', 'Slightly inclined'),
        ('Very enthusiastic', 'Very enthusiastic'),
        ('Neutral', 'Neutral'),
        ('N/A', 'N/A')
    ], verbose_name="How willing does the other Staff feel about integrating Halal in this Kitchen?")
    staff_evaluation_notes = models.TextField(blank=True, null=True, verbose_name="Staff Evaluation Notes")
    
    # Inspection details
    incident = models.TextField(blank=True, null=True, verbose_name="Incident")
    remedy = models.TextField(blank=True, null=True, verbose_name="Remedy")
    conclusion = models.TextField(blank=True, null=True, verbose_name="Conclusion")
    
    def __str__(self):
        return f"Evaluation inspection for {self.school}"
        
        
class TrainingInspectionData(models.Model):
    """
    Combined model replacing PreparationInspection and PreparationChecklist
    """
    school = models.ForeignKey(
        SchoolInspection, 
        on_delete=models.CASCADE, 
        related_name='training_inspections',
        to_field='school_code',
        verbose_name="School Code (SF Code)"
    )
    all_staff_trained = models.BooleanField(default=False,verbose_name="After this visit, have all staff been trained?")
    total_staff_trained = models.PositiveIntegerField(null=True, blank=True,verbose_name="How many total staff are trained?")
    manager_trained = models.BooleanField(default=False,verbose_name="Has the Manager been trained?")
    cook_trained = models.BooleanField(default=False,verbose_name="Has the Cook been trained?")
    halal_training_notes = models.TextField(blank=True, null=True, verbose_name="Halal Training Notes")
    
    # Inspection details
    incident = models.TextField(blank=True, null=True, verbose_name="Incident")
    remedy = models.TextField(blank=True, null=True, verbose_name="Remedy")
    conclusion = models.TextField(blank=True, null=True, verbose_name="Conclusion")
    
    staff_changed = models.TextField(blank=True, null=True, verbose_name="List new employees if staff changed")
    employees_left = models.CharField(max_length=255, blank=True, null=True, verbose_name="List employees who left")
   
    def __str__(self):
        return f"Training inspection for {self.school}"

class StaffRosterInspectionData(models.Model):
    """
    Combined model replacing PreparationInspection and PreparationChecklist
    """
    school = models.ForeignKey(
        SchoolInspection, 
        on_delete=models.CASCADE, 
        related_name='roster_inspections',
        to_field='school_code',
        verbose_name="School Code (SF Code)"
    )
    staff_roster_name = models.CharField(max_length=255,null=True, blank=True, verbose_name="Name")
    staff_roster_position = models.CharField(max_length=50,blank=True, null=True, choices=[
        ('Supervisor', 'Supervisor'),
        ('Manager', 'Manager'),
        ('Cook', 'Cook'),
        ('Assistant Cook', 'Assistant Cook'),
        ('SLH', 'SLH'),
        ('Heavy Duty', 'Heavy Duty'),
        ('Substitute', 'Substitute'),
    ], verbose_name="Position")
    staff_roster_attendance = models.CharField(max_length=50,null=True, blank=True, choices=[
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ],verbose_name="Attendance")
    staff_roster_halal_trained = models.CharField(max_length=50,null=True, blank=True, choices=[
        ('Trained Today', 'Trained Today'),
        ('Already Trained', 'Already Trained'),
        ('No', 'No')
    ],verbose_name="Halal Trained")
    
    staff_roster_notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    
   
    def __str__(self):
        return f"Staff Roster inspection for {self.school}"

class ContaminationRisk(models.Model): 
    # PHASE 10: Contamination Risk
    school = models.ForeignKey(
        SchoolInspection, 
        on_delete=models.CASCADE, 
        related_name='contamination_inspections',
        to_field='school_code',
        verbose_name="School Code (SF Code)"
    )
    contamination_risk_assessment = models.CharField(max_length=50,null=True, blank=True, choices=[
        ('None', 'None'),
        ('Low', 'Low'),
        ('High', 'High')
    ],verbose_name="What is the contamination potential in this facility? Are there any issues in this particular school that raise any concerns for Halal cross-contamination?")

    # Final Comments

    school_name = models.CharField(max_length=100, verbose_name="School Name")
    school_address = models.CharField(max_length=100, verbose_name="School Address", blank=True, null=True)
    street_address = models.CharField(max_length=100, verbose_name="Street Address", blank=True, null=True)
    street_address2 = models.CharField(max_length=100, verbose_name="Street Address Line 2", blank=True, null=True)
    state = models.CharField(max_length=100, verbose_name="State", blank=True, null=True)
    zip_code = models.CharField(max_length=100, verbose_name="Zip Code", blank=True, null=True)
    certification_during_summer = models.BooleanField(default=False,verbose_name="Is this Certification during the Summer School period?")
    school_borough = models.CharField(max_length=50,null=True, blank=True, choices=[
        ('Manhattan', 'Manhattan'),
        ('Bronx', 'Bronx'),
        ('Queens', 'Queens'),
        ('Brooklyn', 'Brooklyn'),
        ('Staten Island', 'Staten Island')
    ], verbose_name="School Borough")
    halal_inspection_evaluation = models.CharField(max_length=50,blank=True, null=True, choices=[
        ('Pass', 'Pass'),
        ('Fail', 'Fail'),
        ('Re-Visit', 'Re-Visit'),
    ],verbose_name="Halal Inspection Evaluation")
    inspector_name = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='inspections')
    inspector_email = models.EmailField(verbose_name="Inspector Email", blank=True, null=True)
    inspection_date = models.DateField(verbose_name="Inspection Date", blank=True, null=True)
    inspector_signature = models.ImageField(upload_to='signatures/', null=True, blank=True, verbose_name="Inspector's Signature")
    time_signed_in = models.TimeField(verbose_name="Time Signed In", blank=True, null=True)
    time_signed_out = models.TimeField(verbose_name="Time Signed Out", blank=True, null=True)
    clock_out_entry_sent = models.BooleanField(default=False,verbose_name="Did you send a picture of your clock out entry in the kitchen log book and send it to your supervisor?")

    # Inspection details
    incident = models.TextField(blank=True, null=True, verbose_name="Incident")
    remedy = models.TextField(blank=True, null=True, verbose_name="Remedy")
    conclusion = models.TextField(blank=True, null=True, verbose_name="Conclusion")

    final_comments = models.TextField(blank=True, null=True)

    def save_signature(self, signature_data):
        """
        Save base64 signature as an image file.
        """
        format, imgstr = signature_data.split(';base64,') 
        ext = format.split('/')[-1]  

        # Create unique filename
        filename = f'signature_{uuid.uuid4()}.{ext}'

        # Convert base64 to image and save it
        self.inspector_signature.save(filename, ContentFile(base64.b64decode(imgstr)), save=True)

    def __str__(self):
        return self.school