from django.db.models.signals import post_save
from django.dispatch import receiver
from projects.models import Milestone
from .models import Invoice

@receiver(post_save, sender=Milestone)
def create_invoice(sender, instance, created, **kwargs):
    if created:
        Invoice.objects.create(
            project=instance.project,
            milestone=instance,
            amount=instance.amount,
            due_date=instance.due_date,
            status='unpaid'
        )
    else:
        # Update invoice amount if milestone amount changes
        if hasattr(instance, 'invoice'):
            instance.invoice.amount = instance.amount
            instance.invoice.due_date = instance.due_date
            instance.invoice.save()
