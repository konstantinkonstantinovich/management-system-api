from django.urls import path
from web.views import *


urlpatterns = [
    path('confirm/<int:pk>', ConfirmationView.as_view(), name='confirm'),
    path('success', success, name='success'),
    path('report/vehicles', ReportView.as_view()),
]
