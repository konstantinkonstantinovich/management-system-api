
from django.urls import path
from api.views import *


urlpatterns = [
    path('v1/users', UserListView.as_view()),
    path('v1/users/<int:pk>', ProfileAPIView.as_view()),
    path('v1/registration', RegistrationView.as_view(), name='sign-up'),
    path('v1/login',  LoginView.as_view(), name='sign-in'),
    path('v1/logout', LogoutView.as_view()),
    path('v1/workers', WorkersAPIView.as_view(), name='worker-list-create'),
    path('v1/workers/<int:pk>', WorkerViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}
    )),
    path('v1/companies/<int:pk>', CompanyAPIView.as_view()),
    path('v1/companies/<int:company_id>/officies', OfficeViewSet.as_view(
        {'get': 'list', 'post': 'create'}
    )),
    path('v1/companies/<int:company_id>/officies/<int:pk>',
        OfficeViewSet.as_view(
            {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}
        )
    ),
    path('v1/companies/<int:company_id>/officies/<int:pk>/assign/<int:user_id>',
         OfficeViewSet.as_view(
             {'post': 'assign'}
         )
    ),
    path('v1/users/<int:pk>/office', OfficeViewSet.as_view({'get': 'office'})),
    path('v1/users/<int:pk>/vehicle', UserVehicleAPIView.as_view()),
    path('v1/companies/<int:pk>/vehicle', VehiclesAPIView.as_view()),
    path('v1/companies/<int:company_id>/vehicle/<int:pk>', VehicleAPIView.as_view()),
]
