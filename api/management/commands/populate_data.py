from django.core.management.base import BaseCommand
from api.models import User, Treatment, Appointment, Prescription
from django.utils import timezone
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populate database with dummy data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting old data...')
        Prescription.objects.all().delete()
        Appointment.objects.all().delete()
        Treatment.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        names = ['Nikhil', 'Pandit', 'Gunn', 'Jatin', 'Mehak', 'Deepak', 'Saransh']
        treatments_list = [
            ('General Checkup', 'Regular health screening'),
            ('Blood Test', 'Complete blood count'),
            ('X-Ray', 'Chest X-Ray'),
            ('Vaccination', 'Annual flu shot'),
            ('Dental Cleaning', 'Routine dental cleaning')
        ]

        print("Creating Treatments...")
        treatments_objs = []
        for name, desc in treatments_list:
            t = Treatment.objects.create(name=name, description=desc)
            treatments_objs.append(t)

        print("Creating Users...")
        doctors = []
        patients = []
        
        
        
        for i, name in enumerate(names):
            email = f"{name.lower()}@hospital.com"
            username = name.lower()
            role = 'PATIENT'
            if i < 2: 
                role = 'DOCTOR'
            else:
                role = random.choice(['DOCTOR', 'PATIENT'])
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                role=role,
                first_name=name
            )
            
            if role == 'DOCTOR':
                doctors.append(user)
            else:
                patients.append(user)
            
            self.stdout.write(f'Created {role}: {name}')

        print("Creating Appointments...")
        if not doctors or not patients:
             self.stdout.write('Need at least one doctor and one patient!')
             return

        for _ in range(15): 
            doctor = random.choice(doctors)
            patient = random.choice(patients)
            status = random.choice(['SCHEDULED', 'COMPLETED', 'CANCELLED'])
            
            days = random.randint(-5, 5)
            appt_date = timezone.now() + timedelta(days=days)
            
            appt = Appointment.objects.create(
                doctor=doctor,
                patient=patient,
                appointment_date=appt_date,
                status=status
            )
            
            if status == 'COMPLETED':
                
                if random.choice([True, False]):
                    pres = Prescription.objects.create(
                        appointment=appt,
                        notes=f"Prescription for {patient.username} by {doctor.username}"
                    )
                    
                    pres.treatments.add(*random.sample(treatments_objs, k=random.randint(1, 2)))

        self.stdout.write(self.style.SUCCESS('Successfully populated database!'))
