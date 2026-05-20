from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Department

Employee = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    joining_date = serializers.DateField(source='date_joined_company', format='%d-%m-%Y', input_formats=['%Y-%m-%d'])
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_id = serializers.IntegerField(source='department.id', read_only=True)
    designation_name = serializers.CharField(source='designation.name', read_only=True)
    role = serializers.CharField(source='role.name', read_only=True)
    class Meta:
        model = Employee
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'department_name', 'department_id', 'designation', 'designation_name',
                  'phone', 'date_of_birth', 'profile_photo', 'joining_date', 'is_active','role']
