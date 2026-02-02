from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Treatment, Appointment, Prescription
from .serializers import (
    UserSerializer, TreatmentSerializer, AppointmentSerializer, PrescriptionSerializer
)

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class TreatmentListView(generics.ListCreateAPIView):
    queryset = Treatment.objects.all()
    serializer_class = TreatmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Optional: Restrict treatment creation to Doctors/Admins
        if self.request.user.role == 'PATIENT':
            raise PermissionDenied("Patients cannot create treatments.")
        serializer.save()

class AppointmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['doctor', 'status', 'appointment_date']

    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.select_related('patient', 'doctor')
        
        if user.role == 'DOCTOR':
            return queryset.filter(doctor=user)
        elif user.role == 'PATIENT':
            return queryset.filter(patient=user)
        elif user.role == 'ADMIN' or user.is_staff:
            return queryset.all()
        return queryset.none()

    def perform_create(self, serializer):
        if self.request.user.role == 'PATIENT':
            serializer.save(patient=self.request.user)
        else:
            # Doctors shouldn't book for themselves usually, or maybe they book for a patient?
            # Existing logic allowed default save.
            serializer.save()

class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Removed IsOwnerOrDoctor permission class
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.select_related('patient', 'doctor')
        
        if user.role == 'DOCTOR':
            return queryset.filter(doctor=user)
        elif user.role == 'PATIENT':
            return queryset.filter(patient=user)
        elif user.role == 'ADMIN' or user.is_staff:
            return queryset.all()
        return queryset.none()

class PrescriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['appointment']

    def get_queryset(self):
        user = self.request.user
        queryset = Prescription.objects.select_related('appointment', 'appointment__patient', 'appointment__doctor').prefetch_related('treatments')

        if user.role == 'DOCTOR':
            return queryset.filter(appointment__doctor=user)
        elif user.role == 'PATIENT':
            return queryset.filter(appointment__patient=user)
        elif user.role == 'ADMIN' or user.is_staff:
            return queryset.all()
        return queryset.all()

    def perform_create(self, serializer):
        if self.request.user.role != 'DOCTOR':
             raise PermissionDenied("Only doctors can create prescriptions.")
        serializer.save()
