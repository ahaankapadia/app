from django import forms
from .models import *
from django.forms.widgets import TimeInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
        
class LoginForm(AuthenticationForm):
    # You can customize the form here if needed
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


class UserLogDataForm(forms.ModelForm):
    class Meta:
        model = UserLogData
        fields = ['user', 'login_time', 'logout_time']

        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'login_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'logout_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
 
from django import forms
from .models import MonthlySalaryCalculation, HourlySalaryCalculation

class MonthlySalaryForm(forms.ModelForm):
    class Meta:
        model = MonthlySalaryCalculation
        fields = ['user', 'minutes', 'salary_per_month', 'date']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(is_superuser=False)

class HourlySalaryForm(forms.ModelForm):
    class Meta:
        model = HourlySalaryCalculation
        fields = ['user', 'total_hours', 'salary_per_hour', 'date']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(is_superuser=False)

      
class UserRegistrationForm(forms.ModelForm):
    school_name = forms.CharField(max_length=255, required=True)
    is_inspector = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'school_name', 'is_inspector']

    def save(self, commit=True):
        # Save user information (including first_name, last_name)
        user = super().save(commit=False)
        if commit:
            user.save()

        # Create or update the UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.school_name = self.cleaned_data['school_name']
        profile.is_inspector = self.cleaned_data['is_inspector']
        profile.save()

        return user

class InspectorRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2']
        
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import SchoolInspection

class CustomBooleanField(forms.TypedChoiceField):
    """
    Custom boolean field to handle True/False/None choices more robustly
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('choices', [(None, "-----"), (True, "Yes"), (False, "No")])
        kwargs.setdefault('coerce', self.coerce_boolean)
        kwargs.setdefault('empty_value', None)
        kwargs.setdefault('required', False)
        super().__init__(*args, **kwargs)

    def coerce_boolean(self, value):
        """
        Robust boolean coercion method
        """
        if value in [True, 'True', '1', 1]:
            return True
        elif value in [False, 'False', '0', 0]:
            return False
        return None

class SchoolInspectionChecklistForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """
    security_asked_id = CustomBooleanField(
        label="Did Security ask for your I.D?"
    )

    security_asked_vaccination = CustomBooleanField(
        label="Did Security ask for proof of Vaccination?"
    )

    signed_in_front_desk = CustomBooleanField(
        label="Did you sign in at the front desk with security?"
    )

    messaged_supervisor = CustomBooleanField(
        label="Did you message your supervisor the time that you officially signed in at the security desk log-in book?"
    )

    signed_in_kitchen_log = CustomBooleanField(
        label="Did you sign into the Kitchen's Visitor Log book?"
    )



    class Meta:
        model = SchoolInspection
        fields = [
            # Common identifiers
            'school_code',
            
            # Inspection metadata
            'inspection_type',
            'inspector_status',
            
            # Notes
            'general_notes',
            
            # Check-in information
            'signed_in_front_desk',
            'signed_in_kitchen_log',
            'check_in_notes',
            
            # Documentation
            'staff_list_provided',
            
            # Meal schedule
            'breakfast_start_time',
            'breakfast_end_time',
            'lunch_start_time',
            'lunch_end_time',
            'breakfast_students_count',
            'lunch_students_count',
            'total_students_registered',
            'halal_consumption_percentage',
        ]
        widgets = {
            'general_notes': forms.Textarea(attrs={'rows': 4}),
            'check_in_notes': forms.Textarea(attrs={'rows': 4}),
            'breakfast_start_time': forms.TimeInput(attrs={'class': 'timepicker form-control'}),
            'breakfast_end_time': forms.TimeInput(attrs={'class': 'timepicker form-control'}),
            'lunch_start_time': forms.TimeInput(attrs={'class': 'timepicker form-control'}),
            'lunch_end_time': forms.TimeInput(attrs={'class': 'timepicker form-control'}),
        }
class SchoolInspectionForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """
    other_schools_attached = CustomBooleanField(
        label="Are there other schools attached to this building?"
    )
    security_asked_id = CustomBooleanField(
        label="Did Security ask for your I.D?"
    )

    security_asked_vaccination = CustomBooleanField(
        label="Did Security ask for proof of Vaccination?"
    )

    signed_in_front_desk = CustomBooleanField(
        label="Did you sign in at the front desk with security?"
    )

    messaged_supervisor = CustomBooleanField(
        label="Did you message your supervisor the time that you officially signed in at the security desk log-in book?"
    )

    signed_in_kitchen_log = CustomBooleanField(
        label="Did you sign into the Kitchen's Visitor Log book?"
    )



    class Meta:
        model = SchoolInspection
        fields = [
            # Common identifiers
            'school_code',
            
            # Inspection metadata
            'inspection_type',
            'inspector_status',
            'kitchen_floor',
            'other_schools_attached',
            
            # Notes
            'general_notes',
            
            # Check-in information
            'security_asked_id',
            'security_asked_vaccination',
            'signed_in_front_desk',
            'signed_in_kitchen_log',
            'messaged_supervisor',
            'check_in_notes',
        ]
        widgets = {
            'general_notes': forms.Textarea(attrs={'rows': 4}),
            'check_in_notes': forms.Textarea(attrs={'rows': 4}),
            'breakfast_start_time': forms.TimeInput(attrs={'class': 'timepicker form-control'}),
            'breakfast_end_time': forms.TimeInput(attrs={'class': 'timepicker form-control'}),
            'lunch_start_time': forms.TimeInput(attrs={'class': 'timepicker form-control'}),
            'lunch_end_time': forms.TimeInput(attrs={'class': 'timepicker form-control'}),
        }   
        
from django import forms
from .models import DeliveryInspectionData, SchoolInspection

# Standard form for detailed delivery inspection
class DeliveryInspectionDataForm(forms.ModelForm):
    class Meta:
        model = DeliveryInspectionData
        fields = ['school','food_delivery_location','halal_food_supplier','halal_boxes_labeled','delivery_notes']
        widgets = {
            'delivery_notes': forms.Textarea(attrs={'rows': 4}),
            'school': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""

# Simplified checklist form for delivery inspection
class DeliveryInspectionChecklistForm(forms.ModelForm):
    class Meta:
        model = DeliveryInspectionData
        fields = [
            'school',
            'incident',
            'remedy',
            'conclusion',
        ]
        widgets = {
            'incident': forms.Textarea(attrs={'rows': 4}),
            'remedy': forms.Textarea(attrs={'rows': 4}),
            'conclusion': forms.Textarea(attrs={'rows': 4}),
            'school': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""   
        
        
class FreezerInspectionForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """
    BOOLEAN_CHOICES = [(None, "-----"), (True, "Yes"), (False, "No")]

    is_halal_meat_mixed_with_halal_non_meat = forms.TypedChoiceField(
        label="Is the staff mixing Halal-meat with Halal non-meat items in the Halal Freezer?",
        choices=BOOLEAN_CHOICES,
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select
    )

    is_halal_non_meat_bagged = forms.TypedChoiceField(
        label="If they are mixing Halal-meat with Halal non-meat items in the Halal Freezer, are they bagging the non-meat Halal?",
        choices=BOOLEAN_CHOICES,
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select
    )

    is_halal_meat_mixed_with_non_halal = forms.TypedChoiceField(
        label="Is the staff mixing Halal-meat with non-Halal items in any freezer?",
        choices=BOOLEAN_CHOICES,
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select
    )

    halal_boxes_clearly_labeled = forms.TypedChoiceField(
        label="Based on your inspection, were the Halal boxes clearly labeled?",
        choices=BOOLEAN_CHOICES,
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select
    )

    class Meta:
        model = FreezerInspectionData
        fields = [
            'school',
            'freezer_clean', 
            'refrigerator_clean',
            'halal_stored_separately',
            'halal_in_boxes',
            'storage_notes',
        ]
        widgets = {
                            
            'storage_notes': forms.Textarea(attrs={'rows': 4}),
            'school': forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""

class FreezerChecklistForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """
    BOOLEAN_CHOICES = [(None, "-----"), (True, "Yes"), (False, "No")]

    is_halal_meat_mixed_with_halal_non_meat = forms.TypedChoiceField(
        label="Is the staff mixing Halal-meat with Halal non-meat items in the Halal Freezer?",
        choices=BOOLEAN_CHOICES,
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select
    )

    is_halal_non_meat_bagged = forms.TypedChoiceField(
        label="If they are mixing Halal-meat with Halal non-meat items in the Halal Freezer, are they bagging the non-meat Halal?",
        choices=BOOLEAN_CHOICES,
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select
    )

    is_halal_meat_mixed_with_non_halal = forms.TypedChoiceField(
        label="Is the staff mixing Halal-meat with non-Halal items in any freezer?",
        choices=BOOLEAN_CHOICES,
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select
    )

    halal_boxes_clearly_labeled = forms.TypedChoiceField(
        label="Based on your inspection, were the Halal boxes clearly labeled?",
        choices=BOOLEAN_CHOICES,
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select
    )
    class Meta:
        model = FreezerInspectionData
        fields = [
            'school',
            'incident', 
            'remedy',
            'conclusion',
            'storage_notes',
            'freezer_clean', 
            'refrigerator_clean',
            'halal_stored_separately',
            'halal_in_boxes',
        ]
        widgets = {
            'incident': forms.Textarea(attrs={'rows': 4}),
            'remedy': forms.Textarea(attrs={'rows': 4}),
            'conclusion': forms.Textarea(attrs={'rows': 4}),
            
            'storage_notes': forms.Textarea(attrs={'rows': 4}),
            'school': forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""
     
     
class PreparationInspectionForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """
    BOOLEAN_CHOICES = [(None, "-----"), (True, "Yes"), (False, "No")]

    separate_utensils_for_halal = forms.TypedChoiceField(
        label="Are there separate utensils used for Halal food preparation?",
        choices=BOOLEAN_CHOICES,
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select
    )

    cutting_boards_designated = forms.TypedChoiceField(
        label="Are there designated cutting boards for Halal food?",
        choices=BOOLEAN_CHOICES,
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select
    )

    halal_meals_prepared_first = forms.TypedChoiceField(
        label="Are Halal meals prepared first before non-Halal items?",
        choices=BOOLEAN_CHOICES,
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select
    )
    sign_freezer = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Clear Halal sign for Freezer?"
    )
    sign_refrigerator = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Clear Halal sign for Refrigerator?"
    )
    sign_oven = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Clear Halal sign for Oven?"
    )
    sign_warmer = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Clear Halal sign for Warmer?"
    )
    sign_countertop = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Clear Halal sign for Counter Top?"
    )
    sign_sink = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Clear Halal sign for Sink?"
    )
    class Meta:
        model = PreparationInspectionData
        fields = [
            'school',
            'countertop',
            'countertop_no_pathogens',
            'sink',
            'sink_no_pathogens',
            'separate_utensils_for_halal',
            'cutting_boards_designated',
            'halal_meals_prepared_first',
            'preparation_notes',
        ]
        widgets = {
            'preparation_notes': forms.Textarea(attrs={'rows': 4}),
            'school': forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""

class PreparationMachineForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """

    class Meta:
        model = PreparationMachine
        fields = [
            'school',
            'machine_serial_number', 
            'machine_type',
            'machine_designation',
            'swab_test_result',
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""

class UtensilsForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """

    class Meta:
        model = UtensilsInspectionData
        fields = [
            'school',
            'utensils_quantity', 
            'utensils_type',
            'utensils_designation',
            'utensils_swab_test',
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""

class PreparationChecklistForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """
    BOOLEAN_CHOICES = [(None, "-----"), (True, "Yes"), (False, "No")]

    halal_items_in_halal_oven = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Halal-approved items in Halal-designated ovens?"
    )
    halal_items_in_non_halal_oven = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Halal-approved items in non-Halal ovens?"
    )
    non_halal_items_in_halal_oven = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Non-Halal items in Halal ovens?"
    )
    halal_items_on_unlabeled_countertop = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Halal products on non-labeled countertops?"
    )
    halal_items_outside_designated_countertop = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Halal products prepared outside designated countertops?"
    )
    utensils_stored_properly = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Are utensils stored in a designated Halal area/container?"
    )
    utensils_labeled_exclusively = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Are utensils labeled for exclusive Halal use?"
    )
    staff_using_halal_utensils = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Is staff using Halal-designated utensils?"
    )
    sign_freezer = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Clear Halal sign for Freezer?"
    )
    sign_refrigerator = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Clear Halal sign for Refrigerator?"
    )
    sign_oven = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Clear Halal sign for Oven?"
    )
    sign_warmer = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Clear Halal sign for Warmer?"
    )
    sign_countertop = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Clear Halal sign for Counter Top?"
    )
    sign_sink = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES, coerce=lambda x: x == "True" if x is not None else None, 
        required=False, widget=forms.Select, label="Clear Halal sign for Sink?"
    )
    class Meta:
        model = PreparationInspectionData
        fields = [
            'school',
            'incident', 
            'remedy',
            'conclusion',
            'halal_items_in_halal_oven',
            'halal_items_in_non_halal_oven', 
            'non_halal_items_in_halal_oven',
            'halal_items_on_unlabeled_countertop',
            'halal_items_outside_designated_countertop',
            'cross_contamination_prevention',
            'utensils_stored_properly',
            'utensils_labeled_exclusively',
            'staff_using_halal_utensils',
            'sign_freezer',
            'sign_refrigerator',
            'sign_oven',
            'sign_warmer',
            'sign_countertop',
            'sign_sink',
            'additional_notes'
        ]
        widgets = {
            'incident': forms.Textarea(attrs={'rows': 4}),
            'remedy': forms.Textarea(attrs={'rows': 4}),
            'conclusion': forms.Textarea(attrs={'rows': 4}),
            'cross_contamination_prevention': forms.Textarea(attrs={'rows': 4}),
            'additional_notes': forms.Textarea(attrs={'rows': 4}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""

class ServingInspectionForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """
    halal_sign_visible = forms.TypedChoiceField(
        label="Is there a visible 'Halal' sign in the serving area?",
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    food_safety_gear_required = forms.TypedChoiceField(
        label="Are staff required to wear food safety gear (e.g., gloves) while serving Halal food?",
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    separate_utensils = forms.TypedChoiceField(
        label="Are separate serving utensils used for Halal food?",
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    serving_area_properly_lit = forms.TypedChoiceField(
        label="Is the serving area properly lit?",
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    sign_serving_line = forms.TypedChoiceField(
        label="Clear Halal sign for Serving Line (optional)",
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    plastic_stand_sign = forms.TypedChoiceField(
        label="Clear Halal sign on Plastic Stand (strongly recommended)",
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    sign_queue_line = forms.TypedChoiceField(
        label="Clear Halal sign for Queue Line (optional)",
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ServingInspectionData
        fields = [
            'school',
            'breakfast_start_time', 
            'breakfast_end_time',
            'lunch_start_time',
            'lunch_end_time',
            'students_served_breakfast',
            'students_served_lunch',
            'total_registered_students',
            'halal_consumption_percentage',
            'halal_serving_location',
            'halal_positioning',
            'halal_sign_visible',
            'halal_sign_type',
            'halal_product_serving_method',
            'serving_service_type',
            'serving_notes',
        ]
        widgets = {
            'breakfast_start_time': forms.TimeInput(attrs={'class': 'timepicker form-control'}),
            'breakfast_end_time':forms.TimeInput(attrs={'class': 'timepicker form-control'}),
            'lunch_start_time': forms.TimeInput(attrs={'class': 'timepicker form-control'}),
            'lunch_end_time': forms.TimeInput(attrs={'class': 'timepicker form-control'}),
            'halal_positioning_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'serving_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'school': forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""
        
class ServingChecklistForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """
    halal_sign_visible = forms.TypedChoiceField(
        label="Is there a visible 'Halal' sign in the serving area?",
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    separate_utensils = forms.TypedChoiceField(
        label="Are separate serving utensils used for Halal food?",
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    sign_serving_line = forms.TypedChoiceField(
        label="Clear Halal sign for Serving Line (optional)",
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    plastic_stand_sign = forms.TypedChoiceField(
        label="Clear Halal sign on Plastic Stand (strongly recommended)",
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    serving_area_properly_lit = forms.TypedChoiceField(
        label="Is the serving area properly lit?",
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: True if x == "True" else False if x == "False" else None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    sign_serving_line = forms.TypedChoiceField(
        label="Clear Halal sign for Serving Line (optional)",
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    separate_gloves = forms.TypedChoiceField(
        label="Are they using separate gloves when touching Halal food?",
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: True if x == "True" else False if x == "False" else None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})  # Force dropdown
    )
    class Meta:
        model = ServingInspectionData
        fields = [
            'school',
            'incident', 
            'remedy',
            'conclusion',
            'halal_serving_location',
            'halal_positioning',
            'halal_sign_visible',
            'halal_consumption_percentage',
            'serving_service_type',
            'notes',
        ]
        widgets = {
            'incident': forms.Textarea(attrs={'rows': 4,'columns':14}),
            'remedy': forms.Textarea(attrs={'rows': 4}),
            'conclusion': forms.Textarea(attrs={'rows': 4}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""
        
        
class StorageInspectionForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """
    halal_trays_washed_separately = forms.TypedChoiceField(
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select
    )

    halal_serving_utensils_washed_separately = forms.TypedChoiceField(
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select
    )

    halal_utensils_trays_halal_sink = forms.TypedChoiceField(
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select
    )

    facility_bad_odors = forms.TypedChoiceField(
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select
    )

    class Meta:
        model = StorageInspectionData
        fields = [
            'school',
            'kitchen_cleaning_frequency', 
            'kitchen_cleaning_frequency_other',
            'halal_trays_washed_separately',
            'halal_trays_washing_other',
            'halal_serving_utensils_washed_separately',
            'halal_utensils_trays_halal_sink',
            'sanitization_chemicals_used',
            'facility_bad_odors',
            'garbage_emptying_frequency',
            'garbage_emptying_frequency_other',
            'waste_management_notes',
        ]
        widgets = {
            'waste_management_notes': forms.Textarea(attrs={'rows': 4}),
            'school': forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""

class StorageChecklistForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """

    facility_bad_odors = forms.TypedChoiceField(
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select
    )
    class Meta:
        model = StorageInspectionData
        fields = [
            'school',
            'incident', 
            'remedy',
            'conclusion',
            'kitchen_cleaning_frequency',
            'halal_pots_separate',
            'utensil_sanitization_method',
            'facility_bad_odors',
            'garbage_emptying_frequency',
            'sanitization_chemicals_used',
            'storage_notes',
        ]
        widgets = {
            'incident': forms.Textarea(attrs={'rows': 4}),
            'remedy': forms.Textarea(attrs={'rows': 4}),
            'conclusion': forms.Textarea(attrs={'rows': 4}),
            'storage_notes': forms.Textarea(attrs={'rows': 4}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""


class BathroomInspectionForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """
    bad_odor_present = forms.TypedChoiceField(
        label="Is there any bad odor in the bathroom?",
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select
    )


    class Meta:
        model = BathroomInspectionData
        fields = [
            'school',
            'bathroom_clean', 
            'adequate_soap',
            'bathroom_notes',
        ]
        widgets = {
            'bathroom_notes': forms.Textarea(attrs={'rows': 4}),
            'school': forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""

class BathroomChecklistForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """

    facility_bad_odors = forms.TypedChoiceField(
        choices=[(None, "-----"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True" if x is not None else None,
        required=False,
        widget=forms.Select
    )
    class Meta:
        model = BathroomInspectionData
        fields = [
            'school',
            'incident', 
            'remedy',
            'conclusion',
            'kitchen_staff_bathroom',
            'mens_staff_bathroom',
            'womens_staff_bathroom',
            'faucets_running',
            'adequate_soap',
            'restroom_cleaner',
            'cleaning_frequency',
            'wash_hands_signs',
            'remove_apron_signs',
            'ventilation',
            'bathroom_notes',
        ]
        widgets = {
            'incident': forms.Textarea(attrs={'rows': 4}),
            'remedy': forms.Textarea(attrs={'rows': 4}),
            'conclusion': forms.Textarea(attrs={'rows': 4}),
            'bathroom_notes': forms.Textarea(attrs={'rows': 4}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""


class RecordsInspectionForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """
    halal_certification_visible = CustomBooleanField(
        label="Is the Halal Certification posted and visible in the kitchen?"
    )
    halal_approved_items_visible = CustomBooleanField(
        label="Is the latest Halal Approved Items list posted in the kitchen?"
    )
    halal_menu_visible = CustomBooleanField(
        label="Is the latest Halal Serving Menu list posted in the kitchen?"
    )
    all_halal_documents_posted = CustomBooleanField(
        label="Are all three documents (Halal Certificate, Approved Items list, and Serving Menu list) posted together and visible?"
    )
    failed_food_safety_inspection = CustomBooleanField(
        label="Has the school ever failed a food safety inspection?"
    )
    class Meta:
        model = RecordsInspectionData
        fields = [
            'school',
            'last_haccp_inspection', 
            'last_doh_inspection',
            'last_halal_inspection',
            'halal_certification_visible',
            'halal_approved_items_visible',
            'all_halal_documents_posted',
            'inspection_notes',
        ]
        widgets = {
            'inspection_notes': forms.Textarea(attrs={'rows': 4}),
            'school': forms.HiddenInput(),
            'last_haccp_inspection': forms.DateInput(attrs={'type': 'date'}),
            'last_doh_inspection': forms.DateInput(attrs={'type': 'date'}),
            'last_halal_inspection': forms.DateInput(attrs={'type': 'date'}),
            'halal_inspection_date': forms.DateInput(attrs={'type': 'date'}),
            'failed_inspection_date': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""

class RecordsChecklistForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """

    class Meta:
        model = RecordsInspectionData
        fields = [
            'school',
            'incident', 
            'remedy',
            'conclusion',
            'last_haccp_inspection',
            'last_doh_inspection',
            'halal_inspection',
            'halal_inspection_date',
            'failed_inspection_date',
            'halal_menu_visible',
            'record_notes',
        ]
        widgets = {
            'incident': forms.Textarea(attrs={'rows': 4}),
            'school': forms.HiddenInput(),
            'remedy': forms.Textarea(attrs={'rows': 4}),
            'conclusion': forms.Textarea(attrs={'rows': 4}),
            'record_notes': forms.Textarea(attrs={'rows': 4}),
            'last_haccp_inspection': forms.DateInput(attrs={'type': 'date'}),
            'last_doh_inspection': forms.DateInput(attrs={'type': 'date'}),
            'halal_inspection_date': forms.DateInput(attrs={'type': 'date'}),
            'failed_inspection_date': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""

from django.forms.widgets import NullBooleanSelect
from .models import EvaluationInspectionData
class EvaluationInspectionForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """
    staff_on_time = CustomBooleanField(
        label="Was the staff on time for the inspection?"
    )
    staff_cooperative = CustomBooleanField(
        label="Was the staff cooperative?"
    )
    staff_engaged = CustomBooleanField(
        label="Was the staff engaged?"
    )
    staff_allowed_inspection_time = CustomBooleanField(
        label="Did the staff allow adequate time for inspection?"
    )
    class Meta:
        model = EvaluationInspectionData
        fields = [
            'school',
            'total_kitchen_staff', 
            'staff_present',
            'manager_willingness_halal',
            'cook_willingness_halal',
            'heavy_duty_willingness_halal',
            'other_staff_willingness_halal',
            'staff_evaluation_notes'
        ]
        widgets = {
            'staff_evaluation_notes': forms.Textarea(attrs={'rows': 4}),
            'school': forms.HiddenInput(),
            'staff_on_time': NullBooleanSelect(),  # Dropdown Yes/No
            'staff_cooperative': NullBooleanSelect(),
            'staff_engaged': NullBooleanSelect(),
            'staff_allowed_inspection_time': NullBooleanSelect(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""

class EvaluationChecklistForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """
    staff_on_time = CustomBooleanField(
        label="Was the staff on time for the inspection?"
    )
    staff_cooperative = CustomBooleanField(
        label="Was the staff cooperative?"
    )
    staff_engaged = CustomBooleanField(
        label="Was the staff engaged?"
    )
    staff_allowed_inspection_time = CustomBooleanField(
        label="Did the staff allow adequate time for inspection?"
    )
    class Meta:
        model = EvaluationInspectionData
        fields = [
            'school',
            'incident', 
            'remedy',
            'conclusion',
            'total_kitchen_staff', 
            'manager_willingness_halal',
            'cook_willingness_halal',
            'heavy_duty_willingness_halal',
            'other_staff_willingness_halal',
            'staff_evaluation_notes'
        ]
        widgets = {
            'incident': forms.Textarea(attrs={'rows': 4}),
            'school': forms.HiddenInput(),
            'remedy': forms.Textarea(attrs={'rows': 4}),
            'conclusion': forms.Textarea(attrs={'rows': 4}),
            'staff_evaluation_notes': forms.Textarea(attrs={'rows': 4}),
            'school': forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""


class TrainingInspectionForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """

    class Meta:
        model = TrainingInspectionData
        fields = [
            'school',
            'total_staff_trained',
            'staff_changed',
            'halal_training_notes',
        ]
        widgets = {
            'halal_training_notes': forms.Textarea(attrs={'rows': 4}),
            'staff_changed': forms.Textarea(attrs={'rows': 4}),
            'all_staff_trained': NullBooleanSelect(),
            'manager_trained': NullBooleanSelect(),
            'cook_trained': NullBooleanSelect(),
            'school': forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""

class TrainingChecklistForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """

    class Meta:
        model = TrainingInspectionData
        fields = [
            'school',
            'incident', 
            'remedy',
            'conclusion',
            'total_staff_trained',
            'staff_changed',
            'employees_left',
        ]
        widgets = {
            'incident': forms.Textarea(attrs={'rows': 4}),
            'school': forms.HiddenInput(),
            'remedy': forms.Textarea(attrs={'rows': 4}),
            'conclusion': forms.Textarea(attrs={'rows': 4}),
            'school': forms.HiddenInput(),
            'all_staff_trained': NullBooleanSelect(),  # Converts checkbox to dropdown
            'manager_trained': NullBooleanSelect(),
            'cook_trained': NullBooleanSelect(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""


class StaffRosterInspectionForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """

    class Meta:
        model = StaffRosterInspectionData
        fields = [
            'school',
            'staff_roster_name', 
            'staff_roster_position',
            'staff_roster_attendance',
            'staff_roster_halal_trained',
        ]
        widgets = {
            'staff_roster_notes': forms.Textarea(attrs={'rows': 4}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].label = ""

class ContaminationInspectionForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """
    certification_during_summer = CustomBooleanField(
        label="Is this Certification during the Summer School period?"
    )
    clock_out_entry_sent = CustomBooleanField(
        label="Did you send a picture of your clock out entry in the kitchen log book and send it to your supervisor?"
    )
    class Meta:
        model = ContaminationRisk
        fields = [
            'school',
            'contamination_risk_assessment', 
            'school_name',
            'school_address',
            'school_borough',
            'halal_inspection_evaluation',
            'inspector_name',
            'inspector_email',
            'inspection_date',
            'inspector_signature',
            'time_signed_in',
            'time_signed_out',
            'final_comments'

        ]
        widgets = {
            'time_signed_in': forms.TimeInput(attrs={'class': 'timepicker form-control'}),
            'time_signed_out': forms.TimeInput(attrs={'class': 'timepicker form-control'}),
            'school_address': forms.Textarea(attrs={'rows': 4}),
            'inspection_date': forms.DateInput(attrs={'type': 'date'}),
            'final_comments': forms.Textarea(attrs={'rows': 4}),
            'school': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['inspector_name'].queryset = User.objects.filter(is_superuser=False, is_staff=False)
        # Set initial values from the logged-in user
        if user:
            self.fields['inspector_name'].initial = user.pk
            self.fields['inspector_email'].initial = user.email
                        
from django.forms.widgets import TimeInput
class ContaminationChecklistForm(forms.ModelForm):
    """
    Simplified form for the checklist inspection type that only shows a subset of fields
    """
    certification_during_summer = CustomBooleanField(
        label="Is this Certification during the Summer School period?"
    )
    clock_out_entry_sent = CustomBooleanField(
        label="Did you send a picture of your clock out entry in the kitchen log book and send it to your supervisor?"
    )
    class Meta:
        model = ContaminationRisk
        fields = [
            'school',
            'incident', 
            'remedy',
            'conclusion',
            'contamination_risk_assessment', 
            'school_name',
            'school_address',
            'school_borough',
            'halal_inspection_evaluation',
            'inspector_name',
            'inspector_email',
            'inspection_date',
            'inspector_signature',
            'time_signed_in',
            'time_signed_out',
            'final_comments'
        ]
        widgets = {
            'incident': forms.Textarea(attrs={'rows': 4}),
            'school': forms.HiddenInput(),
            'remedy': forms.Textarea(attrs={'rows': 4}),
            'conclusion': forms.Textarea(attrs={'rows': 4}),
            'final_comments': forms.Textarea(attrs={'rows': 4}),
            'school_address': forms.Textarea(attrs={'rows': 4}),
            'inspection_date': forms.DateInput(attrs={'type': 'date'}),
            'time_signed_in': forms.TimeInput(attrs={'class': 'timepicker form-control'}),
            'time_signed_out': forms.TimeInput(attrs={'class': 'timepicker form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
        self.fields['school'].label = ""
        # Fetch all non-superuser staff members for the inspector_name dropdown
        self.fields['inspector_name'].queryset = User.objects.filter(is_superuser=False, is_staff=False)
        self.fields['inspector_name'].initial = user        
    
        # Set initial values from the logged-in user
        if user:
            self.fields['inspector_name'].initial = user.pk
            self.fields['inspector_email'].initial = user.email
    
        # Format time fields to 12-hour format
        if self.instance and self.instance.time_signed_in:
            self.initial['time_signed_in'] = self.instance.time_signed_in.strftime('%I:%M %p')
        if self.instance and self.instance.time_signed_out:
            self.initial['time_signed_out'] = self.instance.time_signed_out.strftime('%I:%M %p')
