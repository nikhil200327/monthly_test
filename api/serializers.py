from rest_framework import serializers
from .models import User, Treatment, Appointment, Prescription

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treatment
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    patient = UserSerializer(read_only=True)
    doctor = UserSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='PATIENT'), source='patient', write_only=True, required=False
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='DOCTOR'), source='doctor', write_only=True
    )

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'patient_id', 'doctor_id', 'appointment_date', 'status']

class PrescriptionSerializer(serializers.ModelSerializer):
    treatments = TreatmentSerializer(many=True, read_only=True)
    treatment_ids = serializers.PrimaryKeyRelatedField(
        queryset=Treatment.objects.all(), source='treatments', many=True, write_only=True
    )

    class Meta:
        model = Prescription
        fields = ['id', 'appointment', 'treatments', 'treatment_ids', 'notes', 'created_at']

    def validate_appointment(self, value):
        if value.status != 'COMPLETED':
            raise serializers.ValidationError("Prescriptions can only be created for completed appointments.")
        return value
