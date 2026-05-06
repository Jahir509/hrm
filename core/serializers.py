from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Department

Employee = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'department', 'phone', 'date_of_birth', 'profile_photo']
