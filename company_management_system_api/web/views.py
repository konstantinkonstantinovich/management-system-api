from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from .forms import ConfirmationForm
from api.models import VerificationCode
from django.shortcuts import render
from .permissions import IsSupperUserPermissionsMixin


class ConfirmationView(generic.UpdateView):
    model = VerificationCode
    template_name = 'web/confirm.html'
    form_class = ConfirmationForm
    success_url = reverse_lazy('success')


def success(request):
    return render(request, 'web/success.html', {})


def report(request):
    return render(request, 'web/form.html', {})


class ReportView(IsSupperUserPermissionsMixin, generic.View):
    def get(self, request):
        return render(request, 'web/form.html', {})
