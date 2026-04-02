from django.urls import path
from .views import GenerateCodeView, JoinPartnerView, PartnerStatusView

urlpatterns = [
    path('generate-code/', GenerateCodeView.as_view(), name='generate-code'),
    path('join/', JoinPartnerView.as_view(), name='join-partner'),
    path('status/', PartnerStatusView.as_view(), name='partner-status'),
]
