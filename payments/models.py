from django.db import models
from django.utils import timezone
from projects.models import Project, Milestone

class Invoice(models.Model):
    STATUS_CHOICES = (
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='invoices')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    issued_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True, help_text="When the client confirmed payment")
    payment_link = models.URLField(max_length=500, blank=True, null=True, help_text="Link for the client to pay (Optional)")
    payment_qr = models.ImageField(upload_to='qrcodes/', blank=True, null=True, help_text="QR Code for the client to scan and pay")

    def __str__(self):
        return f"Invoice #{self.pk} - {self.project.title}"
