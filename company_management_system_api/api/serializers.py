from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Company, User, Office, Vehicle, VerificationCode
from rest_framework.authtoken.models import Token
from .constants import ROLE_ADMIN, OFFICE_EXISTS_ERROR


class RegistrationForm(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    company_name = serializers.CharField()
    password = serializers.CharField(min_length=6)
    repeat_password = serializers.CharField(min_length=6)

    def validate(self, data):
        password = data.get('password')
        repeat_password = data.get('repeat_password')

        if password and repeat_password and password != repeat_password:
            raise serializers.ValidationError("Invalid password confirmation")
        return data

    def save(self):
        company = Company.objects.create(
            name=self.validated_data.get('company_name')
        )
        user = User.objects.create(
            first_name=self.validated_data.get('first_name'),
            last_name=self.validated_data.get('last_name'),
            email=self.validated_data.get('email'),
            password=self.validated_data.get('password'),
            is_verified=True,
            role=ROLE_ADMIN
        )
        user.company = company
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = User.objects.filter(email=data.get('email'), password=data.get('password')).first()
            if not user:
                raise serializers.ValidationError('Invalid email or password', code='authorization')
        else:
            raise serializers.ValidationError('Email and password fields must be present', code='authorization')

        if not user.is_verified:
            raise serializers.ValidationError('User is not verified', code='authorization')

        data['user'] = user
        return data

    def save(self):
        token, created = Token.objects.get_or_create(user=self.validated_data.get('user'))

        return {'auth_token': token.key, 'auth_user': self.validated_data.get('user').id}


class WorkerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    repeat_password = serializers.CharField(write_only=True, required=False)
    office = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = User
        exclude = ['is_staff', 'is_active', 'groups', 'user_permissions', 'is_superuser']
        extra_kwargs = {'password': {'write_only': True}}
        depth = 1

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Worker with this email already exists!")
        return value

    def validate(self, attrs):
        password = attrs.get('password', None)
        repeat_password = attrs.get('repeat_password', None)

        if password and repeat_password and password != repeat_password:
            raise serializers.ValidationError("Invalid password confirmation!")

        return attrs

    def create(self, validated_data):
        instance = User.objects.create(**validated_data)
        instance.company_id = self.context.get('company')
        instance.save()
        return instance

    def update(self, instance, validated_data):
        validated_data.pop('email', None)
        return super().update(instance, validated_data)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['name', 'address']


class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = '__all__'
        read_only_fields = ['company']

    def create(self, validated_data):
        validated_data['company_id'] = self.context.get('company')
        return Office.objects.create(**validated_data)


class VehicleSerializer(serializers.ModelSerializer):
    office = serializers.PrimaryKeyRelatedField(
        queryset=Office.objects.all(), required=False
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False
    )

    class Meta:
        model = Vehicle
        fields = '__all__'
        read_only_fields = ['company']

    def validate(self, attrs):
        if attrs.get('office') and attrs.get('user'):
            try:
                worker = User.objects.get(id=attrs.get('user').id)
            except User.DoesNotExist:
                raise serializers.ValidationError('Worker with this id does not exists', code='not_found')

            if not worker.is_office_exists():
                raise serializers.ValidationError(OFFICE_EXISTS_ERROR)

            if worker.office.id != attrs.get('office').id:
                raise serializers.ValidationError(
                    'The worker must be from the same office as the vehicle'
                )
        return attrs

    def create(self, validated_data):
        validated_data['company_id'] = self.context.get('company')
        return Vehicle.objects.create(**validated_data)

