from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Invoice
from .forms import InvoicePaymentForm


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'payments/invoice_list.html'
    context_object_name = 'invoices'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'freelancer':
            return Invoice.objects.filter(project__freelancer=user).select_related('project', 'milestone')
        return Invoice.objects.filter(project__client=user).select_related('project', 'milestone')

class InvoiceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Invoice
    form_class = InvoicePaymentForm
    template_name = 'payments/invoice_form.html'
    success_url = reverse_lazy('invoice_list')

    def test_func(self):
        # Only the freelancer of the project can edit payment details
        invoice = self.get_object()
        return self.request.user == invoice.project.freelancer

    def form_valid(self, form):
        messages.success(self.request, "Payment details updated successfully.")
        return super().form_valid(form)


@login_required
def mark_paid(request, pk):
    """
    Client pays the invoice.
    When ALL invoices on a project are paid, the deliverable is unlocked.
    """
    invoice = get_object_or_404(Invoice, pk=pk)
    project = invoice.project

    # Only the client of this project can pay
    if request.user != project.client:
        messages.error(request, "Only the project client can pay this invoice.")
        return redirect('invoice_list')

    if invoice.status == 'paid':
        messages.info(request, "This invoice is already paid.")
        return redirect('invoice_list')

    # Mark invoice as paid
    invoice.status = 'paid'
    invoice.milestone.status = 'completed'
    invoice.milestone.save()
    invoice.save()

    # Check if ALL invoices for this project are now paid → unlock deliverable
    if project.is_fully_paid and project.deliverable:
        project.deliverable_unlocked = True
        project.save()
        messages.success(
            request,
            f'Payment confirmed! 🎉 The deliverable for "{project.title}" is now unlocked — you can download it!'
        )
    else:
        messages.success(request, 'Invoice marked as paid.')

    return redirect('invoice_list')
