from django.contrib import admin
from django.apps import apps

# Get the current app
app = apps.get_app_config('system_admin')

# Register all models from this app dynamically
for model_name, model in app.models.items():
    @admin.register(model)
    class DynamicAdmin(admin.ModelAdmin):
        # Automatically display all fields in the list view
        list_display = [field.name for field in model._meta.fields if field.name != 'id']
