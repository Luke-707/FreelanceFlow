from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.urls import reverse
from django.http import Http404, FileResponse

from .models import Project, Milestone, ProjectApplication
from .forms import ClientProjectForm, DeliverableUploadForm, MilestoneForm, ProjectApplicationForm, PaymentSetupForm


# ─────────────────────────────────────────────
# List (My Projects)
# ─────────────────────────────────────────────
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'freelancer':
            return Project.objects.filter(freelancer=user).order_by('-created_at')
        return Project.objects.filter(client=user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        if user.role == 'freelancer':
            ctx['pending_requests'] = Project.objects.filter(
                freelancer=user, freelancer_status='pending'
            ).count()
        return ctx


# ─────────────────────────────────────────────
# Marketplace (Open Projects for Freelancers to browse)
# ─────────────────────────────────────────────
@login_required
def project_marketplace(request):
    """Freelancers browse open projects and apply. Clients see all open projects."""
    open_projects = Project.objects.filter(status='open').order_by('-created_at')

    # For each project, check if the current freelancer has already applied
    user_applications = {}
    if request.user.role == 'freelancer':
        applied_ids = ProjectApplication.objects.filter(
            freelancer=request.user
        ).values_list('project_id', flat=True)
        user_applications = set(applied_ids)

    return render(request, 'projects/marketplace.html', {
        'open_projects': open_projects,
        'user_applications': user_applications,
    })


# ─────────────────────────────────────────────
# Apply to Project (Freelancer only)
# ─────────────────────────────────────────────
@login_required
def apply_to_project(request, pk):
    if request.user.role != 'freelancer':
        messages.error(request, "Only freelancers can apply to projects.")
        return redirect('project_marketplace')

    project = get_object_or_404(Project, pk=pk, status='open')

    # Check if already applied
    if ProjectApplication.objects.filter(project=project, freelancer=request.user).exists():
        messages.warning(request, "You have already applied to this project.")
        return redirect('project_marketplace')

    if request.method == 'POST':
        form = ProjectApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.project = project
            application.freelancer = request.user
            application.save()
            messages.success(request, f'Application submitted for "{project.title}"! Waiting for the client to review.')
            return redirect('project_marketplace')
    else:
        form = ProjectApplicationForm()

    return render(request, 'projects/apply_project.html', {
        'form': form,
        'project': project,
    })


# ─────────────────────────────────────────────
# Accept or Reject Application (Client only)
# ─────────────────────────────────────────────
@login_required
def respond_to_application(request, pk, action):
    """Client accepts or rejects a freelancer's application."""
    application = get_object_or_404(ProjectApplication, pk=pk, project__client=request.user)
    project = application.project

    if request.user.role != 'client':
        messages.error(request, "Only clients can respond to applications.")
        return redirect('project_detail', pk=project.pk)

    if project.status != 'open':
        messages.warning(request, "This project is no longer open for applications.")
        return redirect('project_detail', pk=project.pk)

    if action == 'accept':
        # Accept this application
        application.status = 'accepted'
        application.save()
        # Assign freelancer to project
        project.freelancer = application.freelancer
        project.status = 'pending'  # Awaiting freelancer's own acceptance
        project.freelancer_status = 'pending'
        project.save()
        # Reject all other applications
        ProjectApplication.objects.filter(project=project).exclude(pk=application.pk).update(status='rejected')
        messages.success(request, f'{application.freelancer.username} has been selected! They will now accept or decline the project.')
    elif action == 'reject':
        application.status = 'rejected'
        application.save()
        messages.info(request, f"{application.freelancer.username}'s application has been declined.")

    return redirect('project_detail', pk=project.pk)


# ─────────────────────────────────────────────
# Detail
# ─────────────────────────────────────────────
class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        # Client of project or assigned freelancer may view
        if user != obj.client and user != obj.freelancer:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['milestone_form'] = MilestoneForm()
        ctx['deliverable_form'] = DeliverableUploadForm(instance=self.object)
        ctx['payment_setup_form'] = PaymentSetupForm(instance=self.object)
        ctx['applications'] = self.object.applications.select_related('freelancer').all()
        return ctx


# ─────────────────────────────────────────────
# Create (Client only)
# ─────────────────────────────────────────────
@login_required
def project_create(request):
    if request.user.role != 'client':
        messages.error(request, "Only clients can post new projects.")
        return redirect('project_list')

    if request.method == 'POST':
        form = ClientProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.client = request.user
            project.status = 'open'
            project.save()
            messages.success(request, f'Project "{project.title}" posted to the marketplace! Freelancers can now apply.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ClientProjectForm()

    return render(request, 'projects/project_form.html', {'form': form, 'action': 'Post New Project'})


# ─────────────────────────────────────────────
# Accept / Reject (Freelancer only)
# ─────────────────────────────────────────────
@login_required
def project_respond(request, pk, response):
    """Freelancer accepts or rejects a project assignment."""
    project = get_object_or_404(Project, pk=pk, freelancer=request.user)

    if request.user.role != 'freelancer':
        messages.error(request, "Only freelancers can respond to project assignments.")
        return redirect('project_list')

    if project.freelancer_status != 'pending':
        messages.warning(request, "You have already responded to this project.")
        return redirect('project_detail', pk=pk)

    if response == 'accept':
        project.freelancer_status = 'accepted'
        project.status = 'ongoing'
        project.save()
        messages.success(request, f'You accepted "{project.title}". Go build something awesome!')
    elif response == 'reject':
        project.freelancer_status = 'rejected'
        project.status = 'open'  # Back to open so client can accept another applicant
        project.freelancer = None
        project.save()
        messages.info(request, f'You declined "{project.title}".')

    return redirect('project_list')


# ─────────────────────────────────────────────
# Set Payment Amount (Freelancer only)
# ─────────────────────────────────────────────
@login_required
def set_payment_details(request, pk):
    """Freelancer sets the payment amount and payment info for the client."""
    project = get_object_or_404(Project, pk=pk, freelancer=request.user)

    if request.user.role != 'freelancer':
        messages.error(request, "Only the assigned freelancer can set payment details.")
        return redirect('project_detail', pk=pk)

    if request.method == 'POST':
        form = PaymentSetupForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment details saved! The client can now pay to unlock the deliverable.')
            return redirect('project_detail', pk=pk)
    else:
        form = PaymentSetupForm(instance=project)

    return render(request, 'projects/payment_setup.html', {'form': form, 'project': project})


# ─────────────────────────────────────────────
# Client Pay to Unlock (Client only)
# ─────────────────────────────────────────────
@login_required
def pay_to_unlock(request, pk):
    """Client confirms payment and unlocks the deliverable."""
    project = get_object_or_404(Project, pk=pk, client=request.user)

    if request.user.role != 'client':
        messages.error(request, "Only the project client can make payments.")
        return redirect('project_detail', pk=pk)

    if project.deliverable_unlocked:
        messages.info(request, "The deliverable is already unlocked.")
        return redirect('project_detail', pk=pk)

    if not project.deliverable:
        messages.error(request, "No deliverable has been uploaded yet.")
        return redirect('project_detail', pk=pk)

    if request.method == 'POST':
        project.deliverable_unlocked = True
        project.save()
        messages.success(request, f'🎉 Payment confirmed! The deliverable for "{project.title}" is now unlocked — you can download it!')
        return redirect('project_detail', pk=pk)

    return render(request, 'projects/pay_confirm.html', {'project': project})


# ─────────────────────────────────────────────
# Upload Deliverable (Freelancer only)
# ─────────────────────────────────────────────
@login_required
def upload_deliverable(request, pk):
    project = get_object_or_404(Project, pk=pk, freelancer=request.user)

    if request.user.role != 'freelancer':
        messages.error(request, "Only freelancers can upload deliverables.")
        return redirect('project_detail', pk=pk)

    if project.freelancer_status != 'accepted':
        messages.error(request, "You must accept the project before uploading a deliverable.")
        return redirect('project_detail', pk=pk)

    if request.method == 'POST':
        form = DeliverableUploadForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            proj = form.save(commit=False)
            proj.status = 'completed'
            proj.deliverable_unlocked = False  # Client must pay to unlock
            proj.save()
            messages.success(
                request,
                'Deliverable uploaded! The client will be able to download it after payment.'
            )
            return redirect('project_detail', pk=pk)
    else:
        form = DeliverableUploadForm(instance=project)

    return render(request, 'projects/upload_deliverable.html', {'form': form, 'project': project})


# ─────────────────────────────────────────────
# Download Deliverable (Client only, after payment)
# ─────────────────────────────────────────────
@login_required
def download_deliverable(request, pk):
    project = get_object_or_404(Project, pk=pk, client=request.user)

    if not project.deliverable:
        messages.error(request, "No deliverable has been uploaded yet.")
        return redirect('project_detail', pk=pk)

    if not project.deliverable_unlocked:
        messages.warning(request, "Please pay to unlock and download the deliverable.")
        return redirect('project_detail', pk=pk)

    # Serve the file
    response = FileResponse(project.deliverable.open('rb'), as_attachment=True)
    return response


# ─────────────────────────────────────────────
# Milestone
# ─────────────────────────────────────────────
@login_required
def add_milestone(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # Only freelancer assigned to this project may add milestones
    if request.user != project.freelancer:
        messages.error(request, "Only the assigned freelancer can add milestones.")
        return redirect('project_detail', pk=project_id)

    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.project = project
            milestone.save()
            messages.success(request, 'Milestone added.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = MilestoneForm()

    return render(request, 'projects/milestone_form.html', {'form': form, 'project': project})


# ─────────────────────────────────────────────
# Delete (Client only, only if still open/pending/rejected)
# ─────────────────────────────────────────────
@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, client=request.user)

    if project.status not in ('open', 'pending', 'rejected'):
        messages.error(request, "You can only delete projects that are open, pending or rejected.")
        return redirect('project_detail', pk=pk)

    if request.method == 'POST':
        title = project.title
        project.delete()
        messages.success(request, f'Project "{title}" deleted.')
        return redirect('project_list')

    return render(request, 'projects/project_confirm_delete.html', {'project': project})
