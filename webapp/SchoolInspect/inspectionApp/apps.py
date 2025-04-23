from django.apps import AppConfig

class InspectionAppConfig(AppConfig):
    name = 'inspectionApp'

    def ready(self):
        import inspectionApp.signals