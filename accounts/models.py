from django.contrib.auth.models import AbstractUser
from django.db import models


class Permission(models.Model):
    codename = models.CharField(max_length=100, unique=True)  # e.g. 'department.view'
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.codename


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g. 'admin', 'hr_manager'
    permissions = models.ManyToManyField(Permission, blank=True, related_name='roles')

    def __str__(self):
        return self.name

    def has_perm(self, codename):
        return self.permissions.filter(codename=codename).exists()


class Employee(AbstractUser):
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.SET_NULL, related_name='employees')
    department = models.ForeignKey('core.Department', null=True, blank=True, on_delete=models.SET_NULL)
    designation = models.ForeignKey('core.Designation', null=True, blank=True, on_delete=models.SET_NULL)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_joined_company = models.DateField(null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
