from django.contrib.auth import login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework import generics, viewsets, status
from .models import User, Company, Office, Vehicle
from .permissions import (
    IsAuthorized, IsCompanyAdminOrReadOnly, IsCompanyWorker, IsProfileOwner, IsCompanyAdmin
)
from .serializers import (
    WorkerSerializer, RegistrationForm, LoginSerializer,
    CompanySerializer, OfficeSerializer, VehicleSerializer
)
from rest_framework.decorators import action


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = WorkerSerializer
    permission_classes = (IsAuthorized, )


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationForm(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(WorkerSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        request.session['user_id'] = response.get('auth_user')
        login(request, User.objects.get(pk=response.get('auth_user')))
        return Response(response)


class LogoutView(APIView):
    permission_classes = [IsAuthorized]

    def post(self, request):
        Token.objects.filter(key=request.headers.get('Authorization').split(' ')[-1]).delete()
        try:
            del request.session['user_id']
            request.session.flush()
        except KeyError:
            pass
        return Response({})


class WorkersAPIView(generics.ListCreateAPIView):
    serializer_class = WorkerSerializer
    permission_classes = (IsAuthorized, IsCompanyAdminOrReadOnly)

    def get_queryset(self):
        company = User.objects.get(pk=self.request.session.get('user_id')).company
        return User.objects.filter(company=company)

    def list(self, request, *args, **kwargs):
        data = request.data
        queryset = self.get_queryset()
        if data.get('first_name'):
            queryset = queryset.filter(first_name__contains=data.get('first_name'))

        if data.get('last_name'):
            queryset = queryset.filter(last_name__contains=data.get('last_name'))

        if data.get('email'):
            queryset = queryset.filter(email__contains=data.get('email'))

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        company = User.objects.get(pk=self.request.session.get('user_id')).company.id
        context.update({'company': company})
        return context


class WorkerViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = WorkerSerializer
    permission_classes = (IsAuthorized, IsCompanyAdmin)


class CompanyAPIView(generics.RetrieveUpdateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (IsAuthorized, IsCompanyWorker, IsCompanyAdminOrReadOnly)


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = WorkerSerializer
    permission_classes = (IsAuthorized, IsProfileOwner)


class OfficeViewSet(viewsets.ModelViewSet):
    serializer_class = OfficeSerializer
    permission_classes = (IsAuthorized, IsCompanyWorker, IsCompanyAdminOrReadOnly)

    def get_queryset(self):
        queryset = Office.objects.filter(company_id=self.kwargs.get('company_id'))

        if self.request.method in ['PUT', 'DELETE']:
            return queryset

        if self.request.data.get('country'):
            queryset = queryset.filter(country__contains=self.request.data.get('country'))

        if self.request.data.get('city'):
            queryset = queryset.filter(city__contains=self.request.data.get('city'))

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'company': self.kwargs.get('company_id')})
        return context

    @action(detail=True, methods=['post'])
    def assign(self, request, user_id=None, company_id=None, pk=None):
        try:
            user = User.objects.get(id=user_id, company_id=company_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'You can\'t assign user not from your company'},
                status=status.HTTP_403_FORBIDDEN
            )

        if user.office:
            return Response({'error': 'This user is already assign'}, status=status.HTTP_403_FORBIDDEN)

        user.office = self.get_object()
        user.save()
        return Response(WorkerSerializer(user).data)

    @action(detail=True, methods=['get'])
    def office(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if not user.office:
            return Response()

        return Response(self.get_serializer(user.office).data)


class VehiclesAPIView(generics.ListCreateAPIView):
    serializer_class = VehicleSerializer
    permission_classes = (IsAuthorized, IsCompanyWorker, IsCompanyAdminOrReadOnly)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'company': self.kwargs.get('pk')})
        return context

    def get_queryset(self):
        queryset = Vehicle.objects.filter(company_id=self.kwargs.get('pk'))
        if self.request.data.get('office'):
            queryset = queryset.filter(office_id=self.request.data.get('office'))

        if self.request.data.get('user'):
            queryset = queryset.filter(user_id=self.request.data.get('user'))

        return queryset


class VehicleAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = VehicleSerializer
    permission_classes = (IsAuthorized, IsCompanyWorker, IsCompanyAdmin)

    def get_queryset(self):
        return Vehicle.objects.filter(company_id=self.kwargs.get('company_id'))


class UserVehicleAPIView(generics.ListAPIView):
    serializer_class = VehicleSerializer
    permission_classes = (IsAuthorized, IsProfileOwner)

    def get_queryset(self):
        return Vehicle.objects.filter(user_id=self.kwargs.get('pk'))
