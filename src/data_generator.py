import pandas as pd
import random
from faker import Faker

# Initialize Faker for generating names
fake = Faker()

def generate_student_profiles(num_students=10000):  # Changed to 10000 students
    """Generate random student profiles"""
    students = []
    
    for student_id in range(1, num_students + 1):
        student = {
            'student_id': f'STU{str(student_id).zfill(5)}',  # STU00001 format
            'name': fake.name(),
            'age': random.randint(18, 25),
            'batch': random.choice(['2023', '2024', '2025', '2026'])
        }
        students.append(student)
    
    return pd.DataFrame(students)

def generate_marks(students_df):
    """Generate marks for each student in each subject"""
    # List of 6 general subjects as specified
    subjects = ['Electronics', 'Programming', 'Database', 
                'Data_Science', 'Mathematics', 'DSA']
    
    all_marks = []
    
    for _, student in students_df.iterrows():
        for subject in subjects:
            mark = {
                'student_id': student['student_id'],
                'subject': subject,
                'marks': random.randint(0, 100)  # Marks between 0 and 100
            }
            all_marks.append(mark)
    
    marks_df = pd.DataFrame(all_marks)
    
    # Add grades
    marks_df['grade'] = marks_df['marks'].apply(lambda x: 
        'A+' if x >= 90 else
        'A' if x >= 80 else
        'B' if x >= 70 else
        'C' if x >= 60 else
        'D' if x >= 50 else 'F'
    )
    
    return marks_df

def main():
    print("Generating student data...")
    # Generate student profiles
    students_df = generate_student_profiles()
    
    print("Generating marks data...")
    # Generate marks
    marks_df = generate_marks(students_df)
    
    # Save to CSV files
    students_df.to_csv('data/students.csv', index=False)
    marks_df.to_csv('data/marks.csv', index=False)
    
    print(f"Generated data for {len(students_df)} students")
    print(f"Generated {len(marks_df)} mark entries")
    print("Data generation completed!")

def verify_generated_data():
    """Verify the generated data"""
    try:
        students_df = pd.read_csv('data/students.csv')
        marks_df = pd.read_csv('data/marks.csv')
        
        print("\nVerification Results:")
        print(f"Number of students: {len(students_df)}")
        print(f"Number of mark entries: {len(marks_df)}")
        print("\nStudent ID format sample:", students_df['student_id'].iloc[0])
        print("Student columns:", students_df.columns.tolist())
        print("Marks columns:", marks_df.columns.tolist())
        
        # Verify each student has marks
        students_with_marks = marks_df['student_id'].nunique()
        print(f"\nStudents with marks: {students_with_marks}")
        
        if students_with_marks != len(students_df):
            print("Warning: Not all students have marks!")
            
    except Exception as e:
        print(f"Error during verification: {e}")

if __name__ == "__main__":
    main()
    verify_generated_data() 