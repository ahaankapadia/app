from django.contrib import admin
from .models import *

@admin.register(MonthlySalaryCalculation)
class MonthlySalaryCalculationAdmin(admin.ModelAdmin):
    list_display = ('date','user', 'minutes', 'salary_per_month', 'final_salary')
    search_fields = ('user__username',)
    list_filter = ('user',)
    readonly_fields = ('final_salary',)  # Prevent manual changes to final salary
    ordering = ('-date',)

@admin.register(HourlySalaryCalculation)
class HourlySalaryCalculationAdmin(admin.ModelAdmin):
    list_display = ('date','user', 'total_hours', 'salary_per_hour', 'final_salary')
    search_fields = ('user__username',)
    list_filter = ('user',)
    readonly_fields = ('final_salary',)  # Prevent manual changes to final salary
    ordering = ('-date',)
    
@admin.register(UserLogData)
class UserLogDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'logout_time', 'duration')
    list_filter = ('user', 'login_time', 'logout_time')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'school_name', 'is_inspector']

admin.site.register(UserProfile, UserProfileAdmin)

@admin.register(SchoolInspection)
class SchoolInspectionDataAdmin(admin.ModelAdmin):
    list_display = (
            'school_code',
            'INSPECTION_TYPES', 
            'INSPECTOR_STATUSES',
            'kitchen_floor',
            'halal_consumption_percentage',
            'lunch_end_time',
            'check_in_notes'
    )

    ordering = ('school_code', )

@admin.register(PreparationInspectionData)
class PreparationInspectionDataAdmin(admin.ModelAdmin):
    list_display = (
            'school',
            'countertop', 
            'halal_items_in_halal_oven',
            'sign_warmer',
            'sign_freezer',
            'sign_halal_meal_available',
            'utensils_stored_properly'
    )

    ordering = ('school', )

@admin.register(StaffRosterInspectionData)
class StaffRosterInspectionDataAdmin(admin.ModelAdmin):
    list_display = (
        'school',
        'staff_roster_name',
        'staff_roster_position',
        'staff_roster_attendance',
        'staff_roster_halal_trained',
        'staff_roster_notes',
    )
    list_filter = (
        'staff_roster_position',
        'staff_roster_attendance',
        'staff_roster_halal_trained',
        'school',
    )
    search_fields = (
        'staff_roster_name',
        'school__school_code',
        'school__name',  # Assuming `SchoolInspection` has a `name` field
    )
    ordering = ('school', 'staff_roster_name')
    
    
@admin.register(PreparationMachine)
class PreparationMachineDataAdmin(admin.ModelAdmin):
    list_display = (
            'school',
            'machine_serial_number', 
            'machine_type',
            'machine_designation',
            'swab_test_result',
    )

    ordering = ('school', 'machine_serial_number')
    
    
@admin.register(UtensilsInspectionData)
class UtensilsInspectionDataAdmin(admin.ModelAdmin):
    list_display = (
            'school',
            'utensils_quantity', 
            'utensils_type',
            'utensils_designation',
            'utensils_swab_test',
    )

    ordering = ('school', 'utensils_quantity')