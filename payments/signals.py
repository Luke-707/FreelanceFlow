from django.db.models.signals import post_save
from django.dispatch import receiver
from projects.models import Project
from .models import Invoice

# Invoices are now created when a project is accepted by a freelancer,
# handled in projects.views.project_respond
