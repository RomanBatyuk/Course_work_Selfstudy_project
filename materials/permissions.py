from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    """
    Разрешает доступ пользователям из групы Student.
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name="Student").exists()


class IsAdminOrTeacher(BasePermission):
    """
    Разрешает доступ пользователям из групп Admin или Teacher.
    """

    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated
            and user.groups.filter(name__in=["Admin", "Teacher"]).exists()
        )
