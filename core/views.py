from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from accounts.rbac import rbac
from .models import Department
from .serializers import DepartmentSerializer, EmployeeSerializer
from django.contrib.auth import get_user_model

Employee = get_user_model()


@rbac(['GET', 'POST'], roles=['admin', 'hr_manager'])
def department_list(request):
    if request.method == 'GET':
        serializer = DepartmentSerializer(Department.objects.all(), many=True)
        return Response(serializer.data)

    serializer = DepartmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PUT', 'PATCH', 'DELETE'], roles=['admin', 'hr_manager'])
def department_detail(request, pk):
    department = get_object_or_404(Department, pk=pk)

    if request.method == 'GET':
        return Response(DepartmentSerializer(department).data)

    if request.method in ('PUT', 'PATCH'):
        serializer = DepartmentSerializer(department, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    department.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@rbac(['GET', 'POST'], roles=['admin', 'hr_manager'])
def employee_list(request):
    if request.method == 'GET':
        serializer = EmployeeSerializer(Employee.objects.all(), many=True)
        return Response(serializer.data)

    serializer = EmployeeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PUT', 'PATCH', 'DELETE'], roles=['admin', 'hr_manager'])
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'GET':
        return Response(EmployeeSerializer(employee).data)

    if request.method in ('PUT', 'PATCH'):
        serializer = EmployeeSerializer(employee, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    employee.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
