from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import login, logout,authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden,HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from reportlab.pdfgen import canvas
from django.shortcuts import get_object_or_404
import os,json
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from reportlab.pdfgen import canvas
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views import View
from django.utils.decorators import method_decorator
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
import logging,csv
from django.utils.timezone import now, timedelta
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test

def admin_required(user):
    return user.is_authenticated and user.is_superuser

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to the login page after registration
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                log_entry = UserLogData.objects.create(user=user, login_time=now())
                
                print(f"User {username} logged in successfully.")  # Debugging line
                
                if user.is_superuser:
                    return redirect('logs_data')  # Redirect superusers to logs_data
                
                try:
                    if not user.userprofile.is_inspector:
                        print("User is not an inspector.")  # Debugging line
                except UserProfile.DoesNotExist:
                    print("User profile does not exist.")  # Debugging line
                
                return redirect('inspection_form')  # Redirect normal users to inspection_form
            else:
                print("Authentication failed.")  # Debugging line
                return redirect('login')  # Redirect back to login if authentication fails
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@user_passes_test(admin_required, login_url='/login/')
def logs_data(request):
    logs = UserLogData.objects.all().order_by('-login_time')

    username = request.GET.get('username')
    date_range = request.GET.get('date_range')
    status = request.GET.get('status')

    if username:
        logs = logs.filter(user__username__icontains=username)
        
    if date_range:
        today = timezone.now().date()
        if date_range == 'today':
            logs = logs.filter(login_time__date=today)
        elif date_range == 'yesterday':
            logs = logs.filter(login_time__date=today-timezone.timedelta(days=1))
        elif date_range == 'week':
            logs = logs.filter(login_time__date__gte=today-timezone.timedelta(days=7))
        elif date_range == 'month':
            logs = logs.filter(login_time__date__gte=today-timezone.timedelta(days=30))

    if status:
        if status == 'active':
            logs = logs.filter(logout_time__isnull=True)
        elif status == 'completed':
            logs = logs.filter(logout_time__isnull=False)

    # Automatically logout users inactive for more than 1 hour
    one_hour_ago = timezone.now() - timedelta(hours=2)
    inactive_users = UserLogData.objects.filter(logout_time__isnull=True, login_time__lte=one_hour_ago)
    
    for log in inactive_users:
        log.logout_time = timezone.now()
        log.save()
        logout(request)  # Ensure the user is logged out from the session

    form = UserLogDataForm()

    if request.method == "POST":
        form = UserLogDataForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('logs_data')  

    return render(request, 'logs_data.html', {'form': form, 'logs': logs})

@user_passes_test(admin_required, login_url='/login/')
def salary_calculation_view(request):
    if request.method == "POST":
        monthly_form = MonthlySalaryForm(request.POST, prefix='monthly')
        hourly_form = HourlySalaryForm(request.POST, prefix='hourly')

        if monthly_form.is_valid():
            monthly_form.save()
            return redirect('salary_calculation')

        if hourly_form.is_valid():
            hourly_form.save()
            return redirect('salary_calculation')

    else:
        monthly_form = MonthlySalaryForm(prefix='monthly')
        hourly_form = HourlySalaryForm(prefix='hourly')

    return render(request, 'salary_calculation.html', {
        'monthly_form': monthly_form,
        'hourly_form': hourly_form
    })

def user_logout(request):
    if request.user.is_authenticated:
        # Update the latest login entry with logout time
        last_login_entry = UserLogData.objects.filter(user=request.user, logout_time__isnull=True).last()
        if last_login_entry:
            last_login_entry.logout_time = now()
            last_login_entry.save()
    
    logout(request)
    return redirect('login')

def migrate_data_from_csv(csv_file_path):
    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Map CSV fields to Inspection model fields
            inspection = Inspection(
                sf_code=row['SF Code'],
                school_name=row['School Name'],
                inspector_name=row['Inspector Name'],
                inspection_date=row['Inspection Date'],
                # Add more fields as necessary
            )
            inspection.save()

# Call the function with your CSV file path
#migrate_data_from_csv('/home/webapp/SchoolInspect/templates/jotform_data.csv')

# In your models.py file

from django.db import models
import base64
import os
import uuid
from django.core.files.base import ContentFile

class SignatureField(models.TextField):
    """
    A TextField that stores base64 signature data and can convert to ImageField when needed
    """
    def __init__(self, *args, **kwargs):
        self.upload_to = kwargs.pop('upload_to', 'signatures')
        super(SignatureField, self).__init__(*args, **kwargs)

# Example model implementation
class InspectionBase(models.Model):
    # Other fields...
    inspector_signature = models.TextField(blank=True, null=True, help_text="Inspector's signature")
    
    class Meta:
        abstract = True
    
    def save_signature_as_file(self):
        """Converts base64 signature to an actual file and returns the path"""
        if not self.inspector_signature or not self.inspector_signature.startswith('data:image'):
            return None
            
        try:
            # Extract image data
            image_data = self.inspector_signature.split(',')[1]
            binary_data = base64.b64decode(image_data)
            
            # Generate a unique filename
            unique_id = uuid.uuid4().hex
            filename = f"signature_{unique_id}.png"
            
            # Create the upload directory if it doesn't exist
            upload_dir = os.path.join('/home/webapp/SchoolInspect/media/sign/')
            full_dir = os.path.join('media', upload_dir)
            os.makedirs(full_dir, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(full_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(binary_data)
                
            return file_path
        except Exception as e:
            print(f"Error saving signature as file: {e}")
            return None
def handle_signature_upload(request, model_instance):
    """
    Process signature data from form and attach to model instance
    Returns the updated model instance
    """
    signature_data = request.POST.get('signature-data', '')
    
    if signature_data and signature_data.startswith('data:image'):
        try:
            # Extract image data
            image_data = signature_data.split(',')[1]
            binary_data = base64.b64decode(image_data)
            
            # Generate a simple filename with timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"signature_{model_instance.id}_{timestamp}.png"
            
            # Use the specified directory
            upload_dir = '/home/webapp/SchoolInspect/media/sign/'

            os.makedirs(upload_dir, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(binary_data)
            
            # Store just the relative path in the model
            model_instance.inspector_signature = f"sign/{filename}"
            
            # Log success
            logger = logging.getLogger(__name__)
            logger.info(f"Signature saved successfully at {file_path}")
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing signature upload: {str(e)}")
    
    return model_instance
    
from django.forms import inlineformset_factory

# Create a formset to handle multiple staff entries
StaffRosterFormSet = inlineformset_factory(
    SchoolInspection,
    StaffRosterInspectionData,
    form=StaffRosterInspectionForm,
    extra=30,  # Allow up to 30 staff entries
    can_delete=False
)
PreparationMachineFormSet = inlineformset_factory(
    SchoolInspection,
    PreparationMachine,
    form=PreparationMachineForm,
    extra=30,  # Allow up to 30 staff entries
    can_delete=False
)
UtensilsFormSet = inlineformset_factory(
    SchoolInspection,
    UtensilsInspectionData,
    form=UtensilsForm,
    extra=15,  # Allow up to 30 staff entries
    can_delete=False
)
@login_required
def inspection_step(request, step=1):
    """
    Handles each step of the inspection process.
    Allows moving to next step regardless of form validation.
    """
    max_steps = 14  # Update based on total steps
    
    # Define step names for better navigation
    step_names = {
        1: "School Details",
        2: "Delivery Inspection",
        3: "Freezer Inspection",
        4: "Preparation Inspection",
        5: "Utensils Inspection",
        6: "Preparation Machine",
        7: "Serving Inspection", 
        8: "Storage Inspection",
        9: "Bathroom Inspection",
        10: "Records Inspection",
        11: "Evaluation Inspection",
        12: "Training Inspection",
        13: "Staff Roster",
        14: "Contamination Risk"
    }

    # Ensure step is within valid range
    if step < 1:
        return redirect('inspection_step', step=1)
    if step > max_steps:
        return redirect('inspection_complete')

    # Get or store `inspection_id` only inside the inspection process
    inspection_id = request.GET.get('inspection_id') or request.session.get('inspection_id')

    # Initialize variables
    school = None
    delivery_inspection = None
    freezer_inspections = None
    preparation_inspections = None
    serving_inspections = None
    storage_inspections = None
    bathroom_inspections = None
    records_inspections = None
    evaluation_inspections = None
    training_inspections = None
    contamination_inspections = None
    formset = None  # Initialize formset variable
    machine_formset = None
    utensils_formset = None

    # If we have an `inspection_id`, fetch existing data
    if inspection_id:
        try:
            school = get_object_or_404(SchoolInspection, id=inspection_id)
            delivery_inspection, _ = DeliveryInspectionData.objects.get_or_create(school=school)
            freezer_inspections, _ = FreezerInspectionData.objects.get_or_create(school=school)
            preparation_inspections, _ = PreparationInspectionData.objects.get_or_create(school=school)
            serving_inspections, _ = ServingInspectionData.objects.get_or_create(school=school)
            storage_inspections, _ = StorageInspectionData.objects.get_or_create(school=school)
            bathroom_inspections, _ = BathroomInspectionData.objects.get_or_create(school=school)
            records_inspections, _ = RecordsInspectionData.objects.get_or_create(school=school)
            evaluation_inspections, _ = EvaluationInspectionData.objects.get_or_create(school=school)
            training_inspections, _ = TrainingInspectionData.objects.get_or_create(school=school)
            contamination_inspections, _ = ContaminationRisk.objects.get_or_create(school=school)
            
            staff_roster_instances = StaffRosterInspectionData.objects.filter(school=school)
            preparation_machine_instances = PreparationMachine.objects.filter(school=school)
            utensils_machine_instances = UtensilsInspectionData.objects.filter(school=school)
            
            # Store `inspection_id` in session if found
            request.session['inspection_id'] = school.id
        except:
            # If school is not found, clear the session
            if 'inspection_id' in request.session:
                del request.session['inspection_id']
    
    # For step 1, if no school was found, we don't need to error out - we'll create a new one
    if step == 1 and not school:
        # We'll create a new school inspection when the form is submitted
        pass
    elif step > 1 and not school:
        # For subsequent steps, you must have a school inspection
        #messages.error(request, "Please complete the school inspection first.")
        return redirect('inspection_step', step=1)

    # Determine the correct form classes
    staff_roster_form_class = StaffRosterInspectionForm
    preparation_machine_form_class = PreparationMachineForm
    inspection_type = request.session.get('inspection_type', 'inspection')
    school_form_class = SchoolInspectionChecklistForm if inspection_type == 'checklist' else SchoolInspectionForm
    delivery_form_class = DeliveryInspectionChecklistForm if inspection_type == 'checklist' else DeliveryInspectionDataForm
    freezer_form_class = FreezerChecklistForm if inspection_type == 'checklist' else FreezerInspectionForm
    preparation_form_class = PreparationChecklistForm if inspection_type == 'checklist' else PreparationInspectionForm
    serving_form_class = ServingChecklistForm if inspection_type == 'checklist' else ServingInspectionForm
    storage_form_class = StorageChecklistForm if inspection_type == 'checklist' else StorageInspectionForm
    bathroom_form_class = BathroomChecklistForm if inspection_type == 'checklist' else BathroomInspectionForm
    records_form_class = RecordsChecklistForm if inspection_type == 'checklist' else RecordsInspectionForm
    evaluation_form_class = EvaluationChecklistForm if inspection_type == 'checklist' else EvaluationInspectionForm
    training_form_class = TrainingChecklistForm if inspection_type == 'checklist' else TrainingInspectionForm
    contamination_form_class = ContaminationChecklistForm if inspection_type == 'checklist' else ContaminationInspectionForm

    # Initialize form variable
    form = None

    # Determine the correct form for the current step
    if step == 1:
        current_form_class, current_instance, step_title = school_form_class, school, step_names[1]
    elif step == 2:
        current_form_class, current_instance, step_title = delivery_form_class, delivery_inspection, step_names[2]
    elif step == 3:
        current_form_class, current_instance, step_title = freezer_form_class, freezer_inspections, step_names[3]
    elif step == 4:
        current_form_class, current_instance, step_title = preparation_form_class, preparation_inspections, step_names[4]
    elif step == 5:
        current_form_class, current_instance, step_title = None, None, step_names[5]  # Special handling for formset
    elif step == 6:
        current_form_class, current_instance, step_title = None, None, step_names[6]  # Special handling for formset
    elif step == 7:
        current_form_class, current_instance, step_title = serving_form_class, serving_inspections, step_names[7]
    elif step == 8:
        current_form_class, current_instance, step_title = storage_form_class, storage_inspections, step_names[8]
    elif step == 9:
        current_form_class, current_instance, step_title = bathroom_form_class, bathroom_inspections, step_names[9]
    elif step == 10:
        current_form_class, current_instance, step_title = records_form_class, records_inspections, step_names[10]
    elif step == 11:
        current_form_class, current_instance, step_title = evaluation_form_class, evaluation_inspections, step_names[11]
    elif step == 12:
        current_form_class, current_instance, step_title = training_form_class, training_inspections, step_names[12]
    elif step == 13:
        current_form_class, current_instance, step_title = None, None, step_names[13]  # Special handling for formset
    elif step == 14:
        current_form_class, current_instance, step_title = contamination_form_class, contamination_inspections, step_names[14]

    # Handle the Staff Roster formset separately
    if step == 13:
        if request.method == 'POST':
            formset = StaffRosterFormSet(request.POST, instance=school)
            
            if 'save_and_continue' in request.POST:
                if formset.is_valid():
                    formset.save()
                else:
                    # Save partial data even if not all entries are valid
                    try:
                        instances = formset.save(commit=False)
                        for instance in instances:
                            instance.school = school
                            instance.save()
                    except Exception as e:
                        pass
                        #messages.warning(request, f"Some staff roster data may not have been saved: {str(e)}")
                
                return redirect('inspection_step', step=step+1)
            
            elif 'save_and_exit' in request.POST:
                try:
                    instances = formset.save(commit=False)
                    for instance in instances:
                        instance.school = school
                        instance.save()
                except Exception as e:
                    pass
                    #messages.warning(request, f"Some staff roster data may not have been saved: {str(e)}")
                return redirect('inspection_step', step=1)
            
            elif 'previous' in request.POST:
                return redirect('inspection_step', step=step-1)
        else:
            formset = StaffRosterFormSet(instance=school)
            
    # Handle the Machine Preparation formset separately
    if step == 5:
        if request.method == 'POST':
            utensils_formset = UtensilsFormSet(request.POST, instance=school)
                        
            
            if 'save_and_continue' in request.POST:
                if utensils_formset.is_valid():
                    utensils_formset.save()
                else:
                    # Save partial data even if not all entries are valid
                    try:
                        instances = utensils_formset.save(commit=False)
                        for instance in instances:
                            instance.school = school
                            instance.save()
                    except Exception as e:
                        pass
                        #messages.warning(request, f"Some Utensils preparation data may not have been saved: {str(e)}")
                
                return redirect('inspection_step', step=step+1)
            
            elif 'save_and_exit' in request.POST:
                try:
                    instances = utensils_formset.save(commit=False)
                    for instance in instances:
                        instance.school = school
                        instance.save()
                except Exception as e:
                    pass
                    #messages.warning(request, f"Some UtensilsFormSet data may not have been saved: {str(e)}")
                return redirect('inspection_step', step=1)
            
            elif 'previous' in request.POST:
                return redirect('inspection_step', step=step-1)
        else:
            utensils_formset = UtensilsFormSet(instance=school)

    # Handle the Machine Preparation formset separately
    if step == 6:
        if request.method == 'POST':
            machine_formset = PreparationMachineFormSet(request.POST, instance=school)
                        
            
            if 'save_and_continue' in request.POST:
                if machine_formset.is_valid():
                    machine_formset.save()
                else:
                    # Save partial data even if not all entries are valid
                    try:
                        instances = machine_formset.save(commit=False)
                        for instance in instances:
                            instance.school = school
                            instance.save()
                    except Exception as e:
                        pass
                        #messages.warning(request, f"Some Machine preparation data may not have been saved: {str(e)}")
                
                return redirect('inspection_step', step=step+1)
            
            elif 'save_and_exit' in request.POST:
                try:
                    instances = machine_formset.save(commit=False)
                    for instance in instances:
                        instance.school = school
                        instance.save()
                except Exception as e:
                    pass
                    #messages.warning(request, f"Some staff roster data may not have been saved: {str(e)}")
                return redirect('inspection_step', step=1)
            
            elif 'previous' in request.POST:
                return redirect('inspection_step', step=step-1)
        else:
            machine_formset = PreparationMachineFormSet(instance=school)
    
    # Handle form submission for other steps
    elif current_form_class is not None:  # Added check to ensure form_class exists
        if request.method == 'POST':
            form = current_form_class(request.POST, instance=current_instance)
            saved_instance = None  # Initialize saved_instance variable
            
            # Modified logic to save form even if it's not completely valid
            if 'save_and_continue' in request.POST:
                try:
                    if form.is_valid():
                        saved_instance = form.save(commit=False)
                        # Process signature separately
                        saved_instance = handle_signature_upload(request, saved_instance)
                        saved_instance.save()
                    else:
                        # Save form with partial data even if validation fails
                        try:
                            saved_instance = form.save(commit=False)
                            # Process signature data if present
                            signature_data = request.POST.get('signature-data', '')
                            if signature_data and hasattr(saved_instance, 'inspector_signature'):
                                saved_instance.inspector_signature = signature_data
                            saved_instance.save()
                        except Exception as e:
                            messages.warning(request, f"Some form data may not have been saved: {str(e)}")
                    
                    # Link instances to school if applicable
                    if step == 1 and saved_instance:
                        school = saved_instance
                        request.session['inspection_id'] = school.id
                    
                    # Ensure school is linked across steps
                    if school:
                        if step == 2 and delivery_inspection:
                            delivery_inspection.school = school
                            delivery_inspection.save()
                        elif step == 3 and freezer_inspections:
                            freezer_inspections.school = school
                            freezer_inspections.save()
                        elif step == 4 and preparation_inspections:
                            preparation_inspections.school = school
                            preparation_inspections.save()
                        elif step == 7 and serving_inspections:
                            serving_inspections.school = school
                            serving_inspections.save()
                        elif step == 8 and storage_inspections:
                            storage_inspections.school = school
                            storage_inspections.save()
                        elif step == 9 and bathroom_inspections:
                            bathroom_inspections.school = school
                            bathroom_inspections.save()
                        elif step == 10 and records_inspections:
                            records_inspections.school = school
                            records_inspections.save()
                        elif step == 11 and evaluation_inspections:
                            evaluation_inspections.school = school
                            evaluation_inspections.save()
                        elif step == 12 and training_inspections:
                            training_inspections.school = school
                            training_inspections.save()
                        elif step == 14 and contamination_inspections:
                            contamination_inspections.school = school
                            contamination_inspections.save()
                
                except Exception as e:
                    messages.error(request, f"Error saving form: {str(e)}")
                
                # Always move to next step when 'save_and_continue' is clicked
                return redirect('inspection_step', step=step+1) if step < max_steps else redirect('inspection_complete')
            
            elif 'save_and_exit' in request.POST:
                # Save form if valid, otherwise save partial data
                try:
                    if form.is_valid():
                        saved_instance = form.save()
                    else:
                        saved_instance = form.save(commit=False)
                        saved_instance.save()
                    
                    # Update school reference in session if we're on step 1
                    if step == 1 and saved_instance:
                        request.session['inspection_id'] = saved_instance.id
                        
                except Exception as e:
                    messages.warning(request, f"Some form data may not have been saved: {str(e)}")
                return redirect('inspection_step',step=1)
            
            elif 'previous' in request.POST and step > 1:
                return redirect('inspection_step', step=step-1)
            
            # If form is not valid and not saving/continuing
            if not form.is_valid():
                messages.warning(request, f"Some required fields might be missing in the {step_title.lower()} form.")
        else:
            form = current_form_class(instance=current_instance)

    # Progress Calculation
    progress_percentage = (step / max_steps) * 100
    
    user_email_map = {str(user.id): user.email for user in User.objects.filter(is_superuser=False, is_staff=False)}

    context = {
        'form': form, 
        'formset': formset,
        'machine_formset': machine_formset,
        'utensils_formset':utensils_formset,
        'user_email_map': user_email_map,
        'step': step,
        'max_steps': max_steps,
        'step_title': step_title,
        'step_names': step_names,
        'progress_percentage': progress_percentage,
        'is_first_step': step == 1,
        'is_last_step': step == max_steps,
        'step_numbers': range(1, max_steps + 1),
        'inspection_type': inspection_type,
        'school': school,
    }

    return render(request, 'inspection_step.html', context)

from django.http import JsonResponse
from django.urls import reverse

@login_required
def change_section(request):
    """
    AJAX view to handle changing between inspection sections/tabs
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            section_id = data.get('section_id')
            
            if section_id and section_id.isdigit():
                section_id = int(section_id)
                # Validate section_id is within range
                max_steps = 14
                if 1 <= section_id <= max_steps:
                    # Return success with redirect URL to the appropriate step
                    return JsonResponse({
                        'success': True,
                        'redirect_url': reverse('inspection_step', kwargs={'step': section_id})
                    })
            
            return JsonResponse({'success': False, 'error': 'Invalid section ID'}, status=400)
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

from django.forms import modelformset_factory
import re
class inspection_form(View):
    """
    Unified view for managing all school inspection data
    """
    template_name = 'inspection_form.html'

    def get(self, request):
        school_code = request.GET.get('school_code')
        if school_code:
            try:
                # Fetch the school
                school = SchoolInspection.objects.get(school_code=school_code)
                return self.render_school_forms(request, school)
            except SchoolInspection.DoesNotExist:
                messages.error(request, 'School not found. Please check the SF Code.')
                return render(request, self.template_name, {'show_search': True})
        
        # Initial search page
        return render(request, self.template_name, {'show_search': True})

    def save_form(self, request, form_class, instance):
        """
        Helper method to save form data
        """
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data saved successfully!')
            return True
        return False

    def post_school_inspection(self, request):
        # Determine which school form to use
        form_type = request.POST.get('school_form_type')
        school = get_object_or_404(SchoolInspection, school_code=request.POST.get('school_code'))
        
        form_class = SchoolInspectionForm if form_type == 'detailed' else SchoolInspectionChecklistForm
        
        if self.save_form(request, form_class, school):
            return redirect('inspection_form')
        
        # If form is invalid, re-render the page with form errors
        return self.render_school_forms(request, school)

    def post_delivery_inspection(self, request):
        # Determine which delivery inspection form to use
        form_type = request.POST.get('delivery_form_type')
        school = get_object_or_404(SchoolInspection, school_code=request.POST.get('school_code'))
        
        # Get or create delivery inspection for this school
        delivery_inspection, _ = DeliveryInspectionData.objects.get_or_create(school=school)
        
        form_class = DeliveryInspectionDataForm if form_type == 'detailed' else DeliveryInspectionChecklistForm
        
        if self.save_form(request, form_class, delivery_inspection):
            return redirect('inspection_form')
        
        # If form is invalid, re-render the page with form errors
        return self.render_school_forms(request, school)

    def post_freezer_inspection(self, request):
        # Determine which freezer inspection form to use
        form_type = request.POST.get('freezer_form_type')
        school = get_object_or_404(SchoolInspection, school_code=request.POST.get('school_code'))
        
        # Get or create freezer inspection for this school
        freezer_inspection, _ = FreezerInspectionData.objects.get_or_create(school=school)
        
        form_class = FreezerInspectionForm if form_type == 'detailed' else FreezerChecklistForm
        
        if self.save_form(request, form_class, freezer_inspection):
            return redirect('inspection_form')
        
        # If form is invalid, re-render the page with form errors
        return self.render_school_forms(request, school)

    def post_preparation_inspections(self, request):
        # Determine which freezer inspection form to use
        form_type = request.POST.get('preparation_form_type')
        school = get_object_or_404(SchoolInspection, school_code=request.POST.get('school_code'))
        
        # Get or create freezer inspection for this school
        preparation_inspection, _ = PreparationInspectionData.objects.get_or_create(school=school)
        
        form_class = PreparationInspectionForm if form_type == 'detailed' else PreparationChecklistForm
        
        if self.save_form(request, form_class, preparation_inspection):
            return redirect('inspection_form')
        
        # If form is invalid, re-render the page with form errors
        return self.render_school_forms(request, school)

    def post_utensils_inspections(self, request):
        """
        Handle utensils inspection submissions with a more direct approach
        """
        school = get_object_or_404(SchoolInspection, school_code=request.POST.get('school_code'))
        post_data = request.POST.copy()
        
        # First, handle existing entries 
        existing_entries = UtensilsInspectionData.objects.filter(school=school)
        
        # For each existing entry, update from form data if present
        for entry in existing_entries:
            # Find the corresponding form data
            form_prefix = None
            entry_id = str(entry.id)
            
            # Look for this entry's ID in the POST data
            for key in post_data:
                if key.endswith('-id') and post_data[key] == entry_id:
                    form_prefix = key.replace('-id', '')
                    break
            
            if form_prefix:
                # Update the entry with form data
                entry.utensils_quantity = post_data.get(f'{form_prefix}-utensils_quantity', entry.utensils_quantity)
                entry.utensils_type = post_data.get(f'{form_prefix}-utensils_type', entry.utensils_type)
                entry.utensils_designation = post_data.get(f'{form_prefix}-utensils_designation', entry.utensils_designation)
                entry.utensils_swab_test = post_data.get(f'{form_prefix}-utensils_swab_test', entry.utensils_swab_test)
                entry.save()
        
        # Now handle new entries
        # Find form prefixes for new entries (they won't have an ID or will have an empty ID)
        new_form_prefixes = []
        for key in post_data:
            if key.endswith('-utensils_type'):
                prefix = key.replace('-utensils_type', '')
                id_field = f'{prefix}-id'
                
                # If the ID field doesn't exist or is empty, this is a new entry
                if id_field not in post_data or not post_data[id_field]:
                    new_form_prefixes.append(prefix)
        
        # Create new entries
        for prefix in new_form_prefixes:
            utensils_quantity = post_data.get(f'{prefix}-utensils_quantity', '').strip()
            utensils_type = post_data.get(f'{prefix}-utensils_type', '').strip()
            
            # Only create if we have at least type or quantity
            if utensils_quantity or utensils_type:
                UtensilsInspectionData.objects.create(
                    school=school,
                    utensils_quantity=utensils_quantity,
                    utensils_type=utensils_type,
                    utensils_designation=post_data.get(f'{prefix}-utensils_designation', ''),
                    utensils_swab_test=post_data.get(f'{prefix}-utensils_swab_test', '')
                )
        
        messages.success(request, 'Utensils inspections saved successfully!')
        # Return to the same page with the same school code
        return self.render_school_forms(request, school)
    
    def post_machine_inspections(self, request):
        """
        Handle machine inspection submissions with a more direct approach
        """
        school = get_object_or_404(SchoolInspection, school_code=request.POST.get('school_code'))
        post_data = request.POST.copy()
        
        # First, handle existing entries 
        existing_entries = PreparationMachine.objects.filter(school=school)
        
        # For each existing entry, update from form data if present
        for entry in existing_entries:
            # Find the corresponding form data
            form_prefix = None
            entry_id = str(entry.id)
            
            # Look for this entry's ID in the POST data
            for key in post_data:
                if key.endswith('-id') and post_data[key] == entry_id:
                    form_prefix = key.replace('-id', '')
                    break
            
            if form_prefix:
                # Update the entry with form data
                entry.machine_serial_number = post_data.get(f'{form_prefix}-machine_serial_number', entry.machine_serial_number)
                entry.machine_type = post_data.get(f'{form_prefix}-machine_type', entry.machine_type)
                entry.machine_designation = post_data.get(f'{form_prefix}-machine_designation', entry.machine_designation)
                entry.swab_test_result = post_data.get(f'{form_prefix}-swab_test_result', entry.swab_test_result)
                entry.save()
        
        # Now handle new entries
        # Find form prefixes for new entries (they won't have an ID or will have an empty ID)
        new_form_prefixes = []
        for key in post_data:
            if key.endswith('-machine_type'):
                prefix = key.replace('-machine_type', '')
                id_field = f'{prefix}-id'
                
                # If the ID field doesn't exist or is empty, this is a new entry
                if id_field not in post_data or not post_data[id_field]:
                    new_form_prefixes.append(prefix)
        
        # Create new entries
        for prefix in new_form_prefixes:
            machine_serial_number = post_data.get(f'{prefix}-machine_serial_number', '').strip()
            machine_type = post_data.get(f'{prefix}-machine_type', '').strip()
            
            # Only create if we have at least a serial number or type
            if machine_serial_number or machine_type:
                PreparationMachine.objects.create(
                    school=school,
                    machine_serial_number=machine_serial_number,
                    machine_type=machine_type,
                    machine_designation=post_data.get(f'{prefix}-machine_designation', ''),
                    swab_test_result=post_data.get(f'{prefix}-swab_test_result', '')
                )
        
        messages.success(request, 'Machine inspections saved successfully!')
        # Return to the same page with the same school code
        return self.render_school_forms(request, school)
        
    def post_serving_inspection(self, request):
        # Determine which freezer inspection form to use
        form_type = request.POST.get('serving_form_type')
        school = get_object_or_404(SchoolInspection, school_code=request.POST.get('school_code'))
        
        # Get or create freezer inspection for this school
        serving_inspection, _ = ServingInspectionData.objects.get_or_create(school=school)
        
        form_class = ServingInspectionForm if form_type == 'detailed' else ServingChecklistForm
        
        if self.save_form(request, form_class, serving_inspection):
            return redirect('inspection_form')
        
        # If form is invalid, re-render the page with form errors
        return self.render_school_forms(request, school)

    def post_storage_inspection(self, request):
        # Determine which freezer inspection form to use
        form_type = request.POST.get('storage_form_type')
        school = get_object_or_404(SchoolInspection, school_code=request.POST.get('school_code'))
        
        # Get or create freezer inspection for this school
        storage_inspection, _ = StorageInspectionData.objects.get_or_create(school=school)
        
        form_class = StorageInspectionForm if form_type == 'detailed' else StorageChecklistForm
        
        if self.save_form(request, form_class, storage_inspection):
            return redirect('inspection_form')
        
        # If form is invalid, re-render the page with form errors
        return self.render_school_forms(request, school)

    def post_bathroom_inspection(self, request):
        # Determine which freezer inspection form to use
        form_type = request.POST.get('bathroom_form_type')
        school = get_object_or_404(SchoolInspection, school_code=request.POST.get('school_code'))
        
        # Get or create freezer inspection for this school
        bathroom_inspection, _ = BathroomInspectionData.objects.get_or_create(school=school)
        
        form_class = BathroomInspectionForm if form_type == 'detailed' else BathroomChecklistForm
        
        if self.save_form(request, form_class, bathroom_inspection):
            return redirect('inspection_form')
        
        # If form is invalid, re-render the page with form errors
        return self.render_school_forms(request, school)

    def post_records_inspection(self, request):
        # Determine which freezer inspection form to use
        form_type = request.POST.get('records_form_type')
        school = get_object_or_404(SchoolInspection, school_code=request.POST.get('school_code'))
        
        # Get or create freezer inspection for this school
        records_inspection, _ = RecordsInspectionData.objects.get_or_create(school=school)
        
        form_class = RecordsInspectionForm if form_type == 'detailed' else RecordsChecklistForm
        
        if self.save_form(request, form_class, records_inspection):
            return redirect('inspection_form')
        
        # If form is invalid, re-render the page with form errors
        return self.render_school_forms(request, school)

    def post_evaluation_inspection(self, request):
        # Determine which freezer inspection form to use
        form_type = request.POST.get('evaluation_form_type')
        school = get_object_or_404(SchoolInspection, school_code=request.POST.get('school_code'))
        
        # Get or create freezer inspection for this school
        evaluation_inspection, _ = EvaluationInspectionData.objects.get_or_create(school=school)
        
        form_class = EvaluationInspectionForm if form_type == 'detailed' else EvaluationChecklistForm
        
        if self.save_form(request, form_class, evaluation_inspection):
            return redirect('inspection_form')
        
        # If form is invalid, re-render the page with form errors
        return self.render_school_forms(request, school)

    def post_training_inspection(self, request):
        # Determine which freezer inspection form to use
        form_type = request.POST.get('training_form_type')
        school = get_object_or_404(SchoolInspection, school_code=request.POST.get('school_code'))
        
        # Get or create freezer inspection for this school
        training_inspection, _ = TrainingInspectionData.objects.get_or_create(school=school)
        
        form_class = TrainingInspectionForm if form_type == 'detailed' else TrainingChecklistForm
        
        if self.save_form(request, form_class, training_inspection):
            return redirect('inspection_form')
        
        # If form is invalid, re-render the page with form errors
        return self.render_school_forms(request, school)

    def post_staffroster_inspection(self, request):
        """
        Handle staff roster submissions with a more direct approach
        """
        school = get_object_or_404(SchoolInspection, school_code=request.POST.get('school_code'))
        post_data = request.POST.copy()
        
        # First, handle existing entries 
        existing_entries = StaffRosterInspectionData.objects.filter(school=school)
        existing_ids = [str(entry.id) for entry in existing_entries]
        
        # For each existing entry, update from form data if present
        for entry in existing_entries:
            # Find the corresponding form data
            form_prefix = None
            entry_id = str(entry.id)
            
            # Look for this entry's ID in the POST data
            for key in post_data:
                if key.endswith('-id') and post_data[key] == entry_id:
                    form_prefix = key.replace('-id', '')
                    break
            
            if form_prefix:
                # Update the entry with form data
                entry.staff_roster_name = post_data.get(f'{form_prefix}-staff_roster_name', entry.staff_roster_name)
                entry.staff_roster_position = post_data.get(f'{form_prefix}-staff_roster_position', entry.staff_roster_position)
                entry.staff_roster_attendance = post_data.get(f'{form_prefix}-staff_roster_attendance', entry.staff_roster_attendance)
                entry.staff_roster_halal_trained = post_data.get(f'{form_prefix}-staff_roster_halal_trained', entry.staff_roster_halal_trained)
                entry.save()
        
        # Now handle new entries
        # Find form prefixes for new entries (they won't have an ID or will have an empty ID)
        new_form_prefixes = []
        for key in post_data:
            if key.endswith('-staff_roster_name'):
                prefix = key.replace('-staff_roster_name', '')
                id_field = f'{prefix}-id'
                
                # If the ID field doesn't exist or is empty, this is a new entry
                if id_field not in post_data or not post_data[id_field]:
                    new_form_prefixes.append(prefix)
        
        # Create new entries
        for prefix in new_form_prefixes:
            name = post_data.get(f'{prefix}-staff_roster_name', '').strip()
            position = post_data.get(f'{prefix}-staff_roster_position', '').strip()
            
            # Only create if we have at least a name or position
            if name or position:
                StaffRosterInspectionData.objects.create(
                    school=school,
                    staff_roster_name=name,
                    staff_roster_position=position,
                    staff_roster_attendance=post_data.get(f'{prefix}-staff_roster_attendance', ''),
                    staff_roster_halal_trained=post_data.get(f'{prefix}-staff_roster_halal_trained', '')
                )
        
        messages.success(request, 'Staff inspections saved successfully!')
        return self.render_school_forms(request, school)

    def post_contamination_inspection(self, request):
        # Determine which freezer inspection form to use
        form_type = request.POST.get('contamination_form_type')
        school = get_object_or_404(SchoolInspection, school_code=request.POST.get('school_code'))
        
        # Get or create freezer inspection for this school
        contamination_inspection, _ = ContaminationRisk.objects.get_or_create(school=school)
        
        form_class =  ContaminationInspectionForm if form_type == 'detailed' else ContaminationInspectionForm
        
        if self.save_form(request, form_class, contamination_inspection):
            return redirect('inspection_form')
        
        # If form is invalid, re-render the page with form errors
        return self.render_school_forms(request, school)

    def render_school_forms(self, request, school):
        """
        Helper method to render all forms for a specific school
        """
        # Fetch or create related inspection data
        delivery_inspection, _ = DeliveryInspectionData.objects.get_or_create(school=school)
        freezer_inspection, _ = FreezerInspectionData.objects.get_or_create(school=school)
        preparation_inspection, _ = PreparationInspectionData.objects.get_or_create(school=school)
        
        # Create the formset for utensils inspection
        UtensilsFormSet = modelformset_factory(UtensilsInspectionData, form=UtensilsForm, extra=0)
        utensils_inspection = UtensilsInspectionData.objects.filter(school=school)
        if not utensils_inspection.exists():
            UtensilsInspectionData.objects.create(school=school)
            utensils_inspection = UtensilsInspectionData.objects.filter(school=school)
        utensils_inspection_formset = UtensilsFormSet(queryset=utensils_inspection)
    
        # Create formset for machine inspections
        MachineFormSet = modelformset_factory(PreparationMachine, form=PreparationMachineForm, extra=0)
        machine_inspections = PreparationMachine.objects.filter(school=school)
        if not machine_inspections.exists():
            PreparationMachine.objects.create(school=school)
            machine_inspections = PreparationMachine.objects.filter(school=school)
        machine_inspection_formset = MachineFormSet(queryset=machine_inspections)
        
        # Create formset for staff roster - make sure to have at least 5 visible entries
        RosterFormSet = modelformset_factory(StaffRosterInspectionData, form=StaffRosterInspectionForm, extra=0)
        staffroster_inspection = StaffRosterInspectionData.objects.filter(school=school)
        
        if not staffroster_inspection.exists():
            StaffRosterInspectionData.objects.create(school=school)
            staffroster_inspection = StaffRosterInspectionData.objects.filter(school=school)        
        
        staffroster_inspection_formset = RosterFormSet(queryset=staffroster_inspection)
        
        # Get other inspection data
        serving_inspection, _ = ServingInspectionData.objects.get_or_create(school=school)
        storage_inspection, _ = StorageInspectionData.objects.get_or_create(school=school)
        bathroom_inspection, _ = BathroomInspectionData.objects.get_or_create(school=school)
        records_inspection, _ = RecordsInspectionData.objects.get_or_create(school=school)
        evaluation_inspection, _ = EvaluationInspectionData.objects.get_or_create(school=school)
        training_inspection, _ = TrainingInspectionData.objects.get_or_create(school=school)
        contamination_inspection, _ = ContaminationRisk.objects.get_or_create(school=school)
        
        # Prepare context with forms
        context = {
            'school': school,
            'show_search': False,
            # School Inspection Forms
            'school_inspection_form': SchoolInspectionForm(instance=school),
            'school_checklist_form': SchoolInspectionChecklistForm(instance=school),
            
            # Delivery Inspection Forms
            'delivery_inspection_form': DeliveryInspectionDataForm(instance=delivery_inspection),
            'delivery_checklist_form': DeliveryInspectionChecklistForm(instance=delivery_inspection),
            
            # Freezer Inspection Forms
            'freezer_inspection_form': FreezerInspectionForm(instance=freezer_inspection),
            'freezer_checklist_form': FreezerChecklistForm(instance=freezer_inspection),
    
            # Preparation Forms
            'preparation_inspection_form': PreparationInspectionForm(instance=preparation_inspection),
            'preparation_checklist_form': PreparationChecklistForm(instance=preparation_inspection),
            
            # Formsets
            'utensils_inspection_formset': utensils_inspection_formset,
            'machine_inspection_formset': machine_inspection_formset,
            'staffroster_inspection_formset': staffroster_inspection_formset,
            
            # Other inspection forms
            'serving_inspection_form': ServingInspectionForm(instance=serving_inspection),
            'serving_checklist_form': ServingChecklistForm(instance=serving_inspection),
            'storage_inspection_form': StorageInspectionForm(instance=storage_inspection),
            'storage_checklist_form': StorageChecklistForm(instance=storage_inspection),
            'bathroom_inspection_form': BathroomInspectionForm(instance=bathroom_inspection),
            'bathroom_checklist_form': BathroomChecklistForm(instance=bathroom_inspection),
            'records_inspection_form': RecordsInspectionForm(instance=records_inspection),
            'records_checklist_form': RecordsChecklistForm(instance=records_inspection),
            'evaluation_inspection_form': EvaluationInspectionForm(instance=evaluation_inspection),
            'evaluation_checklist_form': EvaluationChecklistForm(instance=evaluation_inspection),
            'training_inspection_form': TrainingInspectionForm(instance=training_inspection),
            'training_checklist_form': TrainingChecklistForm(instance=training_inspection),
            'contamination_inspection_form': ContaminationInspectionForm(instance=contamination_inspection),
            'contamination_checklist_form': ContaminationChecklistForm(instance=contamination_inspection),
        }
    
        return render(request, self.template_name, context)
        
        
    def post(self, request):
        school_code = request.POST.get('school_code')
        if not school_code:
            messages.error(request, 'School code is required to save inspection data.')
            return render(request, self.template_name, {'show_search': True})
    
        try:
            school = SchoolInspection.objects.get(school_code=school_code)
        except SchoolInspection.DoesNotExist:
            messages.error(request, 'School not found. Please check the SF Code.')
            return render(request, self.template_name, {'show_search': True})
            
        # Determine which form is being submitted
        if 'school_inspection_submit' in request.POST:
            return self.post_school_inspection(request)
        elif 'delivery_inspection_submit' in request.POST:
            return self.post_delivery_inspection(request)
        elif 'freezer_inspection_submit' in request.POST:
            return self.post_freezer_inspection(request)
        elif 'preparation_inspection_submit' in request.POST:
            return self.post_preparation_inspections(request)
        elif 'utensils_inspection_submit' in request.POST:
            return self.post_utensils_inspections(request) 
        elif 'machine_inspection_submit' in request.POST:
            return self.post_machine_inspections(request)                    
        elif 'serving_inspection_submit' in request.POST:
            return self.post_serving_inspection(request)
        elif 'storage_inspection_submit' in request.POST:
            return self.post_storage_inspection(request)
        elif 'bathroom_inspection_submit' in request.POST:
            return self.post_bathroom_inspection(request)
        elif 'records_inspection_submit' in request.POST:
            return self.post_records_inspection(request)
        elif 'evaluation_inspection_submit' in request.POST:
            return self.post_evaluation_inspection(request)
        elif 'training_inspection_submit' in request.POST:
            return self.post_training_inspection(request)
        elif 'staffroster_inspection_submit' in request.POST:
            return self.post_staffroster_inspection(request)
        elif 'contamination_inspection_submit' in request.POST:
            return self.post_contamination_inspection(request)

        # Default: maybe someone clicked submit without proper context
        messages.warning(request, 'No action could be performed. Please reload a valid school first.')
        return render(request, self.template_name, {'show_search': True})
        
@require_POST
def update_form_view(request):
    """
    AJAX endpoint to update form view in session
    """
    import json
    try:
        data = json.loads(request.body)
        form_type = data.get('form_type')
        view = data.get('view')

        # Update session with new form view
        request.session[f'{form_type}_form_view'] = view
        request.session.modified = True

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
@csrf_protect
def set_inspection_type(request):
    data = json.loads(request.body)
    inspection_type = data.get('inspection_type')
    
    if inspection_type in ['checklist', 'inspection']:
        request.session['inspection_type'] = inspection_type
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid inspection type'})
    

def generate_inspection_report_pdf(inspection):
    """
    Generate a comprehensive PDF report for the entire school inspection,
    including only forms that have been filled out by the user.
    
    Args:
        inspection (SchoolInspection): The school inspection instance
    
    Returns:
        str: Path to the generated PDF file
    """
    import logging
    import base64
    import os
    import tempfile
    from django.core.mail import EmailMessage
    from django.utils import timezone
    from reportlab.lib.utils import ImageReader
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    
    # Ensure reports directory exists
    reports_dir = os.path.join(settings.MEDIA_ROOT, 'inspection_reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate unique filename
    pdf_filename = f"inspection_report_{inspection.school_code}_{inspection.id}.pdf"
    pdf_path = os.path.join(reports_dir, pdf_filename)
    
    # Create PDF with custom page size and margins
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    margin = 50
    
    # Color palette
    header_color = (0.2, 0.4, 0.6)  # Dark Blue
    section_color = (0.3, 0.5, 0.7)  # Lighter Blue
    
    # Logo and Header
    def draw_header():
        # Company Logo Placeholder
        c.setFillColorRGB(*header_color)
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width/2, height - 40, "School Inspection Report")
        today = inspection.inspection_date if hasattr(inspection, 'inspection_date') else timezone.now().date()
        # Subheader
        c.setFont("Helvetica", 12)
        c.drawCentredString(width/2, height - 65, f"Inspection Date: {today}")
    
    # Section Header
    def draw_section_header(title, y_pos):
        c.setFillColorRGB(*section_color)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y_pos, title)
        
        # Horizontal line
        c.setStrokeColorRGB(*section_color)
        c.line(margin, y_pos - 5, width - margin, y_pos - 5)
    
    # Handle signature rendering
    def render_signature(signature_field, y_position):
        """Renders a signature image on the PDF"""
        try:
            # Check if signature_field is None
            if signature_field is None or not signature_field:
                return y_position
            
            # Check if it's a base64 string (for signature pad data)
            if isinstance(signature_field, str) and signature_field.startswith('data:image'):
                # Extract the base64 part of the data URL
                image_data = signature_field.split(',')[1]
                binary_data = base64.b64decode(image_data)
                
                # Create a temporary image file with a proper name
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_file.write(binary_data)
                    image_path = temp_file.name
            else:
                # It's an ImageField
                if hasattr(signature_field, 'path') and os.path.exists(signature_field.path):
                    image_path = signature_field.path
                else:
                    return y_position
            
            # Calculate appropriate dimensions
            try:
                max_width = width - (2 * margin)
                img_width = 300  # Default width
                img_height = 150  # Default height
                
                # Draw signature image
                c.drawImage(
                    image_path, 
                    margin, 
                    y_position - img_height,
                    width=img_width,
                    height=img_height,
                    preserveAspectRatio=True
                )
                
                # Clean up temporary file if created
                if isinstance(signature_field, str) and os.path.exists(image_path):
                    os.unlink(image_path)
                
                return y_position - img_height - 20  # Return new y position after signature
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Error rendering signature image: {str(e)}")
                
                # Clean up temporary file if created and exception occurred
                if isinstance(signature_field, str) and 'image_path' in locals() and os.path.exists(image_path):
                    os.unlink(image_path)
                
                return y_position
                
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing signature: {str(e)}")
            return y_position  # Return original y position if error occurs
    
    # Field Renderer
    def render_fields(instance, y_position, render=True):
        """
        Render fields from a model instance to the PDF.
        If render=False, just check if there's any data to display.
        """
        if render:
            c.setFont("Helvetica", 10)
            c.setFillColorRGB(0, 0, 0)  # Black text
        
        fields_to_skip = ['id', 'school', 'school_code', 'borough', 'municipality']
        signature_fields = ['inspector_signature', 'signature']
        field_spacing = 15
        
        has_data = False
        signatures_to_process = []
        processed_fields = []
        
        # First identify all fields to process and check if there's any data
        for field in instance._meta.get_fields():
            field_name = field.name
            
            # Skip specified fields
            if field_name in fields_to_skip:
                continue
                
            if field_name in signature_fields:
                # Check if there's a signature
                value = getattr(instance, field_name, None)
                if value:
                    signatures_to_process.append(field_name)
                    has_data = True
                continue
            
            value = getattr(instance, field_name, None)
            
            # Skip empty or default values
            if value is None or value == '' or value is False:
                continue
            
            # For CharField or TextField, check if it's not empty
            if hasattr(field, 'get_internal_type'):
                field_type = field.get_internal_type()
                if field_type in ['CharField', 'TextField'] and isinstance(value, str) and not value.strip():
                    continue
            
            # There's valid data to display
            has_data = True
            
            if render:
                # Value formatting
                if isinstance(value, bool):
                    value = 'Yes' if value else 'No'
                value = str(value) if value is not None else 'N/A'
                
                # Format field name
                formatted_field_name = field_name.replace('_', ' ').title()
                
                # Render field
                field_text = f"{formatted_field_name}: {value}"
                
                # Check if we need to start a new page
                if y_position < 80:
                    c.showPage()
                    draw_header()
                    y_position = height - 100
                
                c.drawString(margin + 20, y_position, field_text)
                y_position -= field_spacing
                processed_fields.append(field_name)
            
        # Process signatures if rendering
        if render and signatures_to_process:
            for sig_field in signatures_to_process:
                signature_value = getattr(instance, sig_field, None)
                if signature_value:
                    # Check if we need to start a new page
                    if y_position < 170:  # Need more space for signature
                        c.showPage()
                        draw_header()
                        y_position = height - 100
                    
                    # Add a label for signature
                    formatted_field_name = sig_field.replace('_', ' ').title()
                    c.drawString(margin + 20, y_position, f"{formatted_field_name}:")
                    y_position -= field_spacing
                    
                    # Render the signature
                    y_position = render_signature(signature_value, y_position)
        
        return y_position, has_data, processed_fields if render else []
    
    # Helper function to start a new page with proper formatting
    def new_page():
        c.showPage()
        draw_header()
        return height - 100
    
    # Main Report Generation
    def generate_report():
        # List of models to include in multi-entry tables
        multi_entry_models = ['Machine Inspection', 'Staff Roster Inspection', 'Utensils Inspection']

        # Initialize the first page
        draw_header()
        y_position = height - 100
        
        # School information section
        draw_section_header("School Information", y_position)
        y_position -= 30
        
        # Render school information directly from the inspection object
        school_fields = [
            'school_code', 'school_name', 'school_address', 'school_borough',
            'certification_during_summer', 'inspector_name', 'inspector_email',
            'inspection_date', 'security_asked_id', 'signed_in_kitchen_log',
            'check_in_notes', 'general_notes', 'final_comments'
        ]

        # First check if we have any data (avoid empty sections)
        has_school_data = False
        for field_name in school_fields:
            if hasattr(inspection, field_name):
                value = getattr(inspection, field_name, None)
                if value not in (None, '', False):
                    has_school_data = True
                    break
        
        if has_school_data:
            for field_name in school_fields:
                if hasattr(inspection, field_name):
                    value = getattr(inspection, field_name, None)
                    
                    # Skip empty values
                    if value is None or value == '' or value is False:
                        continue
                    
                    # Format boolean values
                    if isinstance(value, bool):
                        value = 'Yes' if value else 'No'
                    
                    # Format the field name
                    formatted_name = field_name.replace('_', ' ').title()
                    
                    # Check if new page needed
                    if y_position < 80:
                        y_position = new_page()
                    
                    # Draw the field
                    c.drawString(margin + 20, y_position, f"{formatted_name}: {value}")
                    y_position -= 15
        else:
            # Just show school code if nothing else is available
            c.drawString(margin + 20, y_position, f"School Code: {inspection.school_code}")
            y_position -= 15
        
        # Handle inspector signature if present
        if hasattr(inspection, 'inspector_signature') and inspection.inspector_signature:
            # Check if new page needed for signature
            if y_position < 170:  # Need more space for signature
                y_position = new_page()
                
            c.drawString(margin + 20, y_position, "Inspector Signature:")
            y_position -= 15
            y_position = render_signature(inspection.inspector_signature, y_position)
        
        y_position -= 20
        
        # Inspection section list
        sections = [
            ('School Inspection', SchoolInspection),
            ('Delivery Inspection', DeliveryInspectionData),
            ('Freezer Inspection', FreezerInspectionData),
            ('Preparation Inspection', PreparationInspectionData),
            ('Utensils Inspection', UtensilsInspectionData),
            ('Machine Inspection', PreparationMachine),                        
            ('Serving Inspection', ServingInspectionData),
            ('Storage Inspection', StorageInspectionData),
            ('Bathroom Inspection', BathroomInspectionData),
            ('Records Inspection', RecordsInspectionData),
            ('Evaluation Inspection', EvaluationInspectionData),
            ('Training Inspection', TrainingInspectionData),
            ('Staff Roster Inspection', StaffRosterInspectionData),                        
            ('Contamination Risk', ContaminationRisk)
        ]
        
        # Process each section
        for section_name, model in sections:
            try:
                # Handle multi-entry models (tables)
                if section_name in multi_entry_models:
                    # Skip the SchoolInspection model (already processed)
                    if model == SchoolInspection:
                        continue
                        
                    # Get all instances for this model filtered by school code
                    instances = model.objects.filter(school=inspection.school_code)
                    if not instances.exists():
                        continue
        
                    # Check if we need a new page before starting this section
                    if y_position < 200:  # Need space for header + table headers + at least one row
                        y_position = new_page()
        
                    # Draw the section header
                    draw_section_header(section_name, y_position)
                    y_position -= 30
        
                    # Determine the fields to show (excluding certain fields)
                    sample_instance = instances.first()
                    displayed_fields = [f for f in sample_instance._meta.fields 
                                      if f.name not in ['id', 'school', 'borough', 'municipality']]
                    
                    # Function to draw table headers
                    def draw_table_headers():
                        nonlocal y_position
                        c.setFont("Helvetica-Bold", 10)
                        c.drawString(margin + 20, y_position, "No.")
                        col_x = margin + 60
                        for field in displayed_fields:
                            field_name = field.verbose_name if hasattr(field, 'verbose_name') else field.name
                            c.drawString(col_x, y_position, field_name.replace('_', ' ').title())
                            col_x += 100  # Adjust column spacing
                        y_position -= 20
                        
                    # Draw initial table headers
                    draw_table_headers()
                    
                    # Render all rows
                    c.setFont("Helvetica", 9)
                    for idx, row in enumerate(instances, start=1):
                        # Check if we need a new page for this row
                        if y_position < 80:
                            y_position = new_page()
                            draw_section_header(section_name + " (continued)", y_position)
                            y_position -= 30
                            draw_table_headers()  # Redraw headers on the new page
                            c.setFont("Helvetica", 9)  # Reset font after headers
        
                        # Draw row number
                        c.drawString(margin + 20, y_position, str(idx))
                        
                        # Draw each field in the row
                        col_x = margin + 60
                        for field in displayed_fields:
                            value = getattr(row, field.name, None)
                            
                            # Format the value
                            if isinstance(value, bool):
                                value = 'Yes' if value else 'No'
                            value = str(value) if value else ''
                            
                            # Draw the value (truncated if needed)
                            c.drawString(col_x, y_position, value[:15])
                            col_x += 100
                            
                        y_position -= 15  # Move to next row
                    
                    # Add extra space after the table
                    y_position -= 20
                
                # Handle single-entry models
                else:
                    # Skip if this is the SchoolInspection model (already processed)
                    if model == SchoolInspection:
                        continue
                    
                    # Try to get the single instance for this model
                    try:
                        instance = model.objects.get(school=inspection.school_code)
                    except model.DoesNotExist:
                        continue
                    
                    # Check if there's any data to display
                    _, has_data, _ = render_fields(instance, 0, render=False)
                    if not has_data:
                        continue
                    
                    # Check if we need a new page
                    if y_position < 100:
                        y_position = new_page()
                    
                    # Draw section header and fields
                    draw_section_header(section_name, y_position)
                    y_position -= 30
                    y_position, _, _ = render_fields(instance, y_position)
                    y_position -= 20
            
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Error processing section {section_name}: {str(e)}")
                continue
    
    # Generate the report
    try:
        generate_report()
        c.save()
        return pdf_path
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error generating PDF report: {str(e)}")
        raise
    
from django.core.mail import EmailMessage, send_mail
from django.conf import settings

def send_inspection_email(inspection, pdf_path, username):
    """
    Send inspection report via email with comprehensive error handling.
    Args:
        inspection (SchoolInspection): The school inspection instance
        pdf_path (str): Path to the generated PDF file
        username (str): Username of the current user/inspector
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    import logging
    from django.core.mail import EmailMessage
    from django.utils import timezone
    try:
        # Validate inputs
        if not inspection or not pdf_path:
            raise ValueError("Invalid inspection or PDF path")
            
        # Set inspection date to today
        inspection.inspection_date = timezone.now().date()
        inspection.save()
        
        # Try to get school name from ContaminationRisk if it exists
        try:
            risk_data = ContaminationRisk.objects.get(school=inspection.school_code)
            school_name = getattr(risk_data, 'school_name', inspection.school_code)
        except Exception:
            # Default to using school_code if school_name is not available
            school_name = inspection.school_code
        
        # Email configuration
        subject = f"Inspection Report for {school_name}"
        body = f"""
        Dear {username},
        
        Please find the attached inspection report for {school_name} (SF Code: {inspection.school_code}).
        
        Details:
        - School: {school_name}
        - Inspector: {username}
        - Date: {inspection.inspection_date}
        
        Best regards,
        Inspection Team
        """
        
        # Email sender configuration
        from_email = settings.EMAIL_HOST_USER
        to_emails = ['sushily2302@gmail.com','ibad.wali@shuranewyork.org']
        cc_emails = ['abdulrehmankaps@gmail.com']
        # Create email message with attachment
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email,
            to=to_emails,
            cc=cc_emails
        )
        
        # Attach PDF
        email.attach_file(pdf_path)
        
        # Send email
        email.send(fail_silently=False)
        return True
        
    except Exception as e:
        # Comprehensive error logging
        logger = logging.getLogger(__name__)
        logger.error(
            f"Failed to send inspection email: {str(e)}",
            extra={
                'inspection_id': getattr(inspection, 'id', 'N/A'),
                'school_code': getattr(inspection, 'school_code', 'N/A'),
                'username': username,
            }
        )
        
        # Optional: Additional error handling or notification
        print(f"Email sending failed: {str(e)}")
        return False
         
@login_required
def inspection_complete(request):
    # Clear session data if needed
    for key in list(request.session.keys()):
        if key.startswith('inspection_step_'):
            del request.session[key]
    
    # Retrieve the inspection from session
    inspection_id = request.session.get('inspection_id')
    
    # Print session variables for debugging
    print("Session variables:", dict(request.session))
    
    if not inspection_id:
        messages.error(request, "No active inspection found.")
        return render(request, 'inspection_complete.html')
    
    try:
        # First get the ContaminationRisk object
        contamination_risk = ContaminationRisk.objects.get(id=inspection_id)
        
        school_code = contamination_risk.school
        
        if not school_code:
            messages.error(request, "School code not found in the inspection data.")
            return render(request, 'inspection_complete.html')
        
        # Try to find an existing SchoolInspection
        try:
            inspection = SchoolInspection.objects.get(school_code=school_code)
        except SchoolInspection.DoesNotExist:
            inspection = SchoolInspection(
                school_code=school_code,
            )
            inspection.save()
        
        # Generate PDF report
        pdf_path = generate_inspection_report_pdf(inspection)
        
        # Send email with PDF report
        email_sent = send_inspection_email(inspection, pdf_path, request.user.username)
        
        # Clear inspection-related session data
        if 'inspection_id' in request.session:
            del request.session['inspection_id']
        if 'inspection_type' in request.session:
            del request.session['inspection_type']
        
        # Add success messages
        if email_sent:
            messages.success(request, "Inspection completed. Report has been generated and emailed.")
        else:
            messages.warning(request, "Inspection completed. Report was generated, but email sending failed.")
    
    except ContaminationRisk.DoesNotExist:
        messages.error(request, "Invalid inspection ID: {}".format(inspection_id))
    except Exception as e:
        messages.error(request, f"Error completing inspection: {str(e)}")
        # Print detailed error for debugging
        import traceback
        print(traceback.format_exc())
    
    # Render the completion page
    return render(request, 'inspection_complete.html')
    
@csrf_exempt
@login_required
def autosave_inspection(request):
    if request.method == 'POST':
        form = InspectionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'errors': form.errors})                               