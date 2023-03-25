from django.http import Http404


class IsSupperUserPermissionsMixin:
    def has_permissions(self):
        return self.request.user.is_superuser

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permissions():
            raise Http404()
        return super().dispatch(request, *args, **kwargs)
