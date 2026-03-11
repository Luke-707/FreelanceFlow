from django.db import models
from django.conf import settings


class Project(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),             # Posted, awaiting freelancer applications
        ('pending', 'Pending'),       # Freelancer assigned, awaiting their acceptance
        ('ongoing', 'Ongoing'),       # Freelancer accepted
        ('completed', 'Completed'),   # All milestones done
        ('rejected', 'Rejected'),     # Freelancer declined
    )

    FREELANCER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Expected budget for this project")

    # Client creates the project; freelancer is assigned later after application
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_projects',
        limit_choices_to={'role': 'client'},
    )
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='freelancer_projects',
        limit_choices_to={'role': 'freelancer'},
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    freelancer_status = models.CharField(
        max_length=20,
        choices=FREELANCER_STATUS_CHOICES,
        default='pending',
        help_text='Whether the assigned freelancer has accepted or rejected this project'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)

    # Deliverable: uploaded by freelancer after completing work
    deliverable = models.FileField(upload_to='deliverables/', null=True, blank=True)
    deliverable_note = models.TextField(blank=True, help_text='Notes from the freelancer about the deliverable')

    # Previews for the client to view before payment
    preview_image = models.ImageField(upload_to='previews/', null=True, blank=True, help_text="A visual preview of the project")
    preview_link = models.URLField(max_length=500, null=True, blank=True, help_text="A live link to preview the product")

    # Payment details set by freelancer
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Amount the freelancer requires for payment")
    payment_link = models.URLField(max_length=500, null=True, blank=True, help_text="Payment link for the client")
    payment_qr = models.ImageField(upload_to='payment_qr/', null=True, blank=True, help_text="QR code for payment")

    # Unlocked by client after payment
    deliverable_unlocked = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def total_earnings(self):
        return sum(m.amount for m in self.milestones.all())

    @property
    def total_paid(self):
        return sum(
            inv.amount for inv in self.invoices.filter(status='paid')
        )

    @property
    def is_fully_paid(self):
        return self.total_paid >= self.total_earnings and self.total_earnings > 0


class Milestone(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.project.title} - {self.title}"


class ProjectApplication(models.Model):
    """A freelancer's application to take up an open project."""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='applications')
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_applications',
        limit_choices_to={'role': 'freelancer'},
    )
    cover_letter = models.TextField(blank=True, help_text="A brief message about why you want this project")
    proposed_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Your proposed rate for this project")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'freelancer')

    def __str__(self):
        return f"{self.freelancer.username} → {self.project.title}"
