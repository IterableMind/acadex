from faker import Faker
import random
from datetime import datetime, timedelta 
from ..models import Student, db  # Adjust based on your project structure

def generate_random_students(num_students):
    fake = Faker()
    
    for _ in range(num_students):
        adm_no = f"ADM{random.randint(1000, 9999)}"
        
        # Check if admission number already exists
        if Student.query.filter_by(adm_no=adm_no).first():
            continue  # Skip this student and continue

        fullname = fake.name()
        grade = random.choice(["Grade 1", "Grade 2", "Grade 3", "Grade 4",
          "Grade 5", "Grade 6", "Grade 7"])
        dob = fake.date_of_birth(minimum_age=6, maximum_age=18)
        photo = None  # Placeholder, modify as needed
        adm_date = fake.date_between(start_date="-5y", end_date="today")
        gender = random.choice(["Male", "Female"]) 
        stream = None
        if grade == "Grade 4" or grade == "Grade 5":
            stream = random.choice(["West", "East"])
        previous_school = fake.company() if random.random() > 0.5 else None
        parent_name = fake.name()
        relationship = random.choice(["Father", "Mother", "Guardian"])
        contact_phone = fake.phone_number()
        id_no = random.randint(10000000, 99999999)
        email = fake.email() if random.random() > 0.5 else None
        health_info = fake.sentence() if random.random() > 0.5 else None
        
        student = Student(
            fullname=fullname,
            grade=grade,
            dob=dob,
            photo=photo,
            adm_no=adm_no,
            adm_date=adm_date,
            gender=gender,
            stream=stream,
            previous_school=previous_school,
            parent_name=parent_name,
            relationship=relationship,
            contact_phone=contact_phone,
            id_no=id_no,
            email=email,
            health_info=health_info
        )
        
        db.session.add(student)
    
    db.session.commit()
    db.session.close()  # Ensure session is closed to reflect changes
    print(f"{num_students} students added successfully.")

# Example usage
# generate_random_students(10)
