from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from projects.models import Project, Milestone
from payments.models import Invoice
from django.db.models import Sum

@login_required
def dashboard(request):
    user = request.user
    context = {}
    
    if user.role == 'freelancer':
        projects = Project.objects.filter(freelancer=user)
        invoices = Invoice.objects.filter(project__freelancer=user)
    else:
        projects = Project.objects.filter(client=user)
        invoices = Invoice.objects.filter(project__client=user)
    
    context['total_projects'] = projects.count()
    context['ongoing_projects'] = projects.filter(status='ongoing').count()
    context['completed_projects'] = projects.filter(status='completed').count()
    
    paid_invoices = invoices.filter(status='paid')
    pending_invoices = invoices.filter(status='unpaid')
    
    context['total_earnings'] = paid_invoices.aggregate(Sum('amount'))['amount__sum'] or 0
    context['pending_payments'] = pending_invoices.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context['recent_projects'] = projects.order_by('-created_at')[:5]
    
    return render(request, 'core/dashboard.html', context)
