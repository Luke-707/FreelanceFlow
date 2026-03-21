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
    
    paid_total = paid_invoices.aggregate(Sum('amount'))['amount__sum'] or 0
    context['total_earnings'] = paid_total   # used for both roles in template
    context['pending_payments'] = pending_invoices.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context['recent_projects'] = projects.order_by('-created_at')[:5]
    context['recent_payments'] = paid_invoices.select_related('project', 'milestone').order_by('-paid_at')[:5]
    context['total_paid_invoices_count'] = paid_invoices.count()
    
    return render(request, 'core/dashboard.html', context)
