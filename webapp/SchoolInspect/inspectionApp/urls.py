from django.urls import path
from . import views
from .views import inspection_form

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('inspection/<int:step>/', views.inspection_step, name='inspection_step'),
    path('inspection_complete/', views.inspection_complete, name='inspection_complete'),
    path('inspection_form/', views.inspection_form.as_view(), name='inspection_form'),
    path('update_form_view/', views.update_form_view, name='update_form_view'),
    path('autosave_inspection/', views.autosave_inspection, name='autosave_inspection'),
    path('logs_data/', views.logs_data, name='logs_data'),
    path('salary_calculation/', views.salary_calculation_view, name='salary_calculation'),
    path('set-inspection-type/', views.set_inspection_type, name='set_inspection_type'),
    path('inspection/change-section/', views.change_section, name='change_section'),     
    
]        