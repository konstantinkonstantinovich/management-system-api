from rest_framework.permissions import BasePermission
from rest_framework.authtoken.models import Token
from .models import User

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class IsAuthorized(BasePermission):
    def has_permission(self, request, view):
        try:
            token = request.headers.get('Authorization').split(' ')[-1]
        except AttributeError:
            return False

        token_object = Token.objects.filter(key=token)
        if not token_object.exists():
            return False
        return request.session.get('user_id') == token_object.first().user.id


class IsCompanyAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        try:
            user = User.objects.get(pk=request.session.get('user_id'))
        except User.DoesNotExist:
            return False
        return bool(user.is_admin_role() or request.method in SAFE_METHODS)


class IsCompanyWorker(BasePermission):
    def has_permission(self, request, view):
        company_pk = view.kwargs.get('company_id') or view.kwargs.get('pk')
        try:
            user = User.objects.get(pk=request.session.get('user_id'))
        except User.DoesNotExist:
            return False

        if not user.company_id:
            return False

        return company_pk == user.company_id


class IsProfileOwner(BasePermission):
    def has_permission(self, request, view):
        return view.kwargs.get('pk') == request.session.get('user_id')


class IsCompanyAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            user = User.objects.get(pk=request.session.get('user_id'))
        except User.DoesNotExist:
            return False

        return user.is_admin_role()
