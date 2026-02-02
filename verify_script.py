import os
import django
import sys
import json


sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_sys.settings')
django.setup()

from api.models import User, Treatment, Appointment, Prescription
from rest_framework.test import APIClient
from django.utils import timezone

client = APIClient()

def run_test():
    print("Creating Users...")
    User.objects.all().delete()
    
    doctor = User.objects.create_user(username='doc', email='doc@test.com', password='password', role='DOCTOR')
    patient = User.objects.create_user(username='pat', email='pat@test.com', password='password', role='PATIENT')
    
    print("Getting Tokens...")
    resp = client.post('/api/token/', {'email': 'doc@test.com', 'password': 'password'}, format='json')
    doc_token = resp.data['access']
    
    resp = client.post('/api/token/', {'email': 'pat@test.com', 'password': 'password'}, format='json')
    pat_token = resp.data['access']
    
    print("Creating Treatment...")
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + doc_token)
    resp = client.post('/api/treatments/', {'name': 'Flu Shot', 'description': 'Anti-flu'}, format='json')
    if resp.status_code != 201:
        print(f"Treatment creation failed: {resp.data}")
        return
    treatment_id = resp.data['id']
    
    print("Booking Appointment (Patient)...")
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + pat_token)
    data = {
        'doctor_id': doctor.id, 
        'appointment_date': timezone.now().isoformat(), 
        'status': 'SCHEDULED'
    }
    resp = client.post('/api/appointments/', data, format='json')
    if resp.status_code != 201:
        print(f"Appointment booking failed: {resp.data}")
        return
    appt_id = resp.data['id']
    
    print("Doctor trying prescription on SCHEDULED appt (Should Fail)...")
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + doc_token)
    resp = client.post('/api/prescriptions/', {
        'appointment': appt_id, 
        'treatment_ids': [treatment_id], 
        'notes': 'Take rest'
    }, format='json')
    
    if resp.status_code == 400:
        print("Failed as expected.")
    else:
        print(f"UNEXPECTED SUCCESSS: {resp.status_code} {resp.data}")
        return
    
    print("Doctor updating status to COMPLETED...")
    resp = client.patch(f'/api/appointments/{appt_id}/', {'status': 'COMPLETED'}, format='json')
    if resp.status_code != 200:
        print(f"Update failed: {resp.data}")
        return
    
    print("Doctor creating prescription (Should Success)...")
    resp = client.post('/api/prescriptions/', {
        'appointment': appt_id, 
        'treatment_ids': [treatment_id], 
        'notes': 'Take rest'
    }, format='json')
    
    if resp.status_code == 201:
        print("Success.")
    else:
        print(f"Prescription failed: {resp.data}")
        return

    print("ALL TESTS PASSED!")

if __name__ == '__main__':
    run_test()
