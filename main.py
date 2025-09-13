import os
import random
from flask import Flask, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def index():
    return "Flask app is running and connected to Firebase!"

@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.json
    users_ref = db.collection('users')
    doc_ref = users_ref.document()
    doc_ref.set(user_data)
    return jsonify({"id": doc_ref.id}), 201

@app.route('/users', methods=['GET'])
def get_users():
    users_ref = db.collection('users')
    docs = users_ref.stream()
    all_users = [doc.to_dict() for doc in docs]
    return jsonify(all_users), 200

@app.route('/quizzes', methods=['POST'])
def create_quiz():
    quiz_data = request.json
    quizzes_ref = db.collection('quizzes')
    doc_ref = quizzes_ref.document()
    doc_ref.set(quiz_data)
    return jsonify({"id": doc_ref.id}), 201

@app.route('/quizzes/<quiz_id>', methods=['GET'])
def get_quiz(quiz_id):
    quiz_ref = db.collection('quizzes').document(quiz_id)
    doc = quiz_ref.get()
    if not doc.exists:
        return jsonify({"error": "Quiz not found"}), 404
    return jsonify(doc.to_dict()), 200
@app.route('/login/student', methods=['POST'])
def student_login():
    try:
        data = request.json
        student_usn = data.get('usn')
        classroom_id = data.get('classroom_id')
        
        if not all([student_usn, classroom_id]):
            return jsonify({"error": "USN and Classroom ID are required."}), 400

       
        student_ref = db.collection('students').document(student_usn).get()
        if not student_ref.exists:
            return jsonify({"error": "Invalid student USN."}), 401
            
        
        classroom_ref = db.collection('classrooms').document(classroom_id).get()
        if not classroom_ref.exists or not classroom_ref.get('is_active'):
            return jsonify({"error": "Classroom not found or is not active."}), 404
        
        return jsonify({"success": True, "message": "Student logged in successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/signup/student', methods=['POST'])
def student_signup():
    try:
        data = request.json
        usn = data.get('usn')
        name = data.get('name')
        email = data.get('email')
        
        if not all([usn, name, email]):
            return jsonify({"error": "USN, name, and email are required for signup."}), 400

        student_ref = db.collection('students').document(usn)
        if student_ref.get().exists:
            return jsonify({"error": "Student with this USN already exists."}), 409

        student_ref.set({
            "name": name,
            "email": email,
            "usn": usn,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({"success": True, "message": "Student profile created successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/student/profile/<usn>', methods=['GET'])
def get_student_profile(usn):
    try:
        student_ref = db.collection('students').document(usn)
        doc = student_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "Student profile not found."}), 404
        
        # Get base student data
        student_data = doc.to_dict()
        
        # Get attendance details
        attendance_ref = db.collection('attendance')
        attendance_docs = attendance_ref.where('usn', '==', usn).stream()
        attendance_data = []
        total_classes = 0
        classes_attended = 0
        
        for attendance in attendance_docs:
            att_data = attendance.to_dict()
            attendance_data.append(att_data)
            total_classes += 1
            if att_data.get('present', False):
                classes_attended += 1
        
        # Calculate attendance percentage
        attendance_percentage = (classes_attended / total_classes * 100) if total_classes > 0 else 0
        
        # Get weekly performance
        performance_ref = db.collection('student_performance').where('usn', '==', usn).stream()
        weekly_performance = [perf.to_dict() for perf in performance_ref]
        
        # Get assigned documents (PPT, PDF)
        documents_ref = db.collection('study_materials').where('assigned_to', 'array_contains', usn).stream()
        assigned_documents = [doc.to_dict() for doc in documents_ref]
        
        return jsonify({
            "student_info": student_data,
            "attendance": {
                "total_classes": total_classes,
                "classes_attended": classes_attended,
                "attendance_percentage": attendance_percentage,
                "attendance_history": attendance_data
            },
            "weekly_performance": weekly_performance,
            "assigned_documents": assigned_documents
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# New endpoint for AI chatbot interactions
@app.route('/student/chat', methods=['POST'])
def student_chat():
    try:
        data = request.json
        student_query = data.get('query')
        document_id = data.get('document_id')  # Optional, if asking about specific document
        
        # Here you would integrate with your AI service
        # For now, returning a placeholder response
        response = {
            "answer": f"This is a placeholder response for: {student_query}",
            "related_documents": []
        }
        
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/signup/faculty', methods=['POST'])
def faculty_signup():
    try:
        data = request.json
        teacher_code = data.get('teacher_code')
        name = data.get('name')
        email = data.get('email')
        
        if not all([teacher_code, name, email]):
            return jsonify({"error": "Teacher code, name, and email are required for signup."}), 400

        faculty_ref = db.collection('teachers').document(teacher_code)
        if faculty_ref.get().exists:
            return jsonify({"error": "Faculty with this teacher code already exists."}), 409

        faculty_ref.set({
            "name": name,
            "email": email,
            "teacher_code": teacher_code,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({"success": True, "message": "Faculty profile created successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/faculty/profile/<teacher_code>', methods=['GET'])
def get_faculty_profile(teacher_code):
    try:
        faculty_ref = db.collection('teachers').document(teacher_code)
        doc = faculty_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "Faculty profile not found."}), 404
        
        return jsonify(doc.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    # Route to display the faculty dashboard
@app.route('/dashboard/faculty/<teacher_code>', methods=['GET'])
def faculty_dashboard(teacher_code):
    try:
        # Retrieve the faculty member's profile
        faculty_ref = db.collection('teachers').document(teacher_code)
        faculty_profile = faculty_ref.get()

        if not faculty_profile.exists:
            return jsonify({"error": "Faculty profile not found."}), 404
        
        # Retrieve classes associated with the faculty member
        classes_ref = db.collection('classrooms').where('teacher_code', '==', teacher_code)
        classes_docs = classes_ref.stream()
        
        my_classes = []
        for doc in classes_docs:
            class_data = doc.to_dict()
            class_data['classroom_id'] = doc.id
            
            # Get student performance for this class
            performance_ref = db.collection('student_performance').where('classroom_id', '==', doc.id).stream()
            class_performance = [perf.to_dict() for perf in performance_ref]
            
            # Get attendance data for this class
            attendance_ref = db.collection('attendance').where('classroom_id', '==', doc.id).stream()
            attendance_data = [att.to_dict() for att in attendance_ref]
            
            # Calculate class statistics
            total_students = len(class_data.get('students', []))
            avg_attendance = sum(len(att.get('present_students', [])) for att in attendance_data) / len(attendance_data) if attendance_data else 0
            
            class_data.update({
                'total_students': total_students,
                'average_attendance': avg_attendance,
                'performance_data': class_performance,
                'attendance_history': attendance_data
            })
            
            my_classes.append(class_data)
        
        return jsonify({
            "success": True,
            "message": "Faculty dashboard data retrieved.",
            "profile": faculty_profile.to_dict(),
            "my_classes": my_classes
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to create a new class
@app.route('/create_class', methods=['POST'])
def create_class():
    try:
        data = request.json
        classroom_id = data.get('classroom_id')
        teacher_code = data.get('teacher_code')
        college_name = data.get('college_name')
        subject = data.get('subject', '')  # Optional subject name
        max_students = data.get('max_students', 60)  # Default max students
        
        if not all([classroom_id, teacher_code, college_name]):
            return jsonify({"error": "Classroom ID, teacher code, and college name are required."}), 400

        # Check if the teacher code exists
        teacher_ref = db.collection('teachers').document(teacher_code).get()
        if not teacher_ref.exists:
            return jsonify({"error": "Invalid teacher code."}), 401

        # Check if classroom already exists
        existing_class = db.collection('classrooms').document(classroom_id).get()
        if existing_class.exists:
            return jsonify({"error": "Classroom ID already exists."}), 409

        # Save the new class to the database
        classroom_ref = db.collection('classrooms').document(classroom_id)
        classroom_ref.set({
            "teacher_code": teacher_code,
            "college_name": college_name,
            "subject": subject,
            "max_students": max_students,
            "current_students": 0,
            "students": [],
            "is_active": True,
            "created_at": firestore.SERVER_TIMESTAMP,
            "last_updated": firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({"success": True, "message": "Class created successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/my_classes/<teacher_code>', methods=['GET'])
def get_my_classes(teacher_code):
    try:
        # Retrieve all classes associated with the given teacher_code
        classes_ref = db.collection('classrooms').where('teacher_code', '==', teacher_code)
        docs = classes_ref.stream()

        class_list = []
        for doc in docs:
            class_data = doc.to_dict()
            class_data['classroom_id'] = doc.id
            class_list.append(class_data)
        
        return jsonify(class_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/class_details/<classroom_id>', methods=['GET'])
def get_class_details(classroom_id):
    try:
        # 1. Retrieve the classroom details
        classroom_ref = db.collection('classrooms').document(classroom_id)
        classroom_doc = classroom_ref.get()

        if not classroom_doc.exists:
            return jsonify({"error": "Classroom not found."}), 404

        class_details = classroom_doc.to_dict()
        class_details['classroom_id'] = classroom_doc.id

        # 2. Get enrolled students details
        enrolled_students = []
        student_usns = class_details.get('students', [])
        for usn in student_usns:
            student_ref = db.collection('students').document(usn).get()
            if student_ref.exists:
                student_data = student_ref.to_dict()
                enrolled_students.append(student_data)

        # 3. Get today's attendance
        today = firestore.SERVER_TIMESTAMP
        attendance_ref = db.collection('attendance')\
            .where('classroom_id', '==', classroom_id)\
            .order_by('date', direction=firestore.Query.DESCENDING)\
            .limit(1)\
            .stream()
        
        today_attendance = next(attendance_ref, None)
        present_students = len(today_attendance.get('present_students', [])) if today_attendance else 0

        # 4. Get recent study materials
        materials_ref = db.collection('study_materials')\
            .where('classroom_id', '==', classroom_id)\
            .order_by('uploaded_at', direction=firestore.Query.DESCENDING)\
            .limit(5)\
            .stream()
        recent_materials = [mat.to_dict() for mat in materials_ref]

        # 5. Calculate class statistics
        total_enrolled = len(enrolled_students)
        attendance_percentage = (present_students / total_enrolled * 100) if total_enrolled > 0 else 0

        return jsonify({
            "success": True,
            "class_details": {
                **class_details,
                "enrolled_students": enrolled_students,
                "total_enrolled": total_enrolled,
                "today_attendance": {
                    "present": present_students,
                    "percentage": attendance_percentage
                }
            },
            "recent_materials": recent_materials
        }), 200

        return jsonify({
            "success": True,
            "message": f"Details for class {classroom_id} retrieved.",
            "class_details": class_details,
            "student_details": student_list,
            "topics_covered": topics_covered,
            "schedule": schedule,
            "notes": notes
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/class_details/<classroom_id>/confirm', methods=['POST'])
def confirm_class_details(classroom_id):
    try:
        # Update the class status to 'confirmed' or 'active'
        classroom_ref = db.collection('classrooms').document(classroom_id)
        classroom_ref.update({"status": "confirmed"})

        return jsonify({
            "success": True,
            "message": f"Class {classroom_id} details confirmed. Redirecting to dashboard."
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/login/faculty', methods=['POST'])
def faculty_login():
    try:
        data = request.json
        teacher_code = data.get('teacher_code')
        college_name = data.get('college_name')

        if not all([teacher_code, college_name]):
            return jsonify({"error": "Teacher code and college name are required."}), 400

        # Verify the teacher code in the database
        teacher_ref = db.collection('teachers').document(teacher_code).get()
        if not teacher_ref.exists:
            return jsonify({"error": "Invalid teacher code."}), 401

        # Generate a unique ID for the classroom
        classroom_id = f"{college_name}_{block_name}_{classroom_name}".replace(" ", "_").lower()

        # Update or create the classroom data in Firestore
        classroom_ref = db.collection('classrooms').document(classroom_id)
        classroom_ref.set({
            "college_name": college_name,
            "block_name": block_name,
            "classroom_name": classroom_name,
            "teacher_code": teacher_code,
            "is_active": True,
            "last_login": firestore.SERVER_TIMESTAMP
        }, merge=True)
        
        # Return the dashboard options for the frontend to render
        dashboard_options = {
            "take_attendance_url": f"/attendance/{classroom_id}",
            "notes_url": f"/notes/{classroom_id}",
            "quiz_url": f"/quiz/{classroom_id}",
            "dashboard_url": f"/dashboard/faculty/{teacher_code}"
        }

        return jsonify({
            "success": True, 
            "message": "Faculty logged in successfully!",
            "classroom_id": classroom_id,
            "dashboard_options": dashboard_options
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/attendance/<classroom_id>', methods=['POST'])
def take_attendance(classroom_id):
    usns = request.json.get('usns')
    attendance_ref = db.collection('attendance').document()

    attendance_data = {
        "classroom_id": classroom_id,
        "date": firestore.SERVER_TIMESTAMP,
        "present_students": usns,
        "status": "pending_teacher_confirmation"
    }

    attendance_ref.set(attendance_data)
    
    return jsonify({
        "success": True,
        "message": "Attendance recorded. Awaiting teacher confirmation.",
        "attendance_id": attendance_ref.id
    }), 201
@app.route('/notes/<classroom_id>', methods=['GET'])
def get_notes(classroom_id):
    notes_ref = db.collection('notes').where('classroom_id', '==', classroom_id)
    docs = notes_ref.stream()

    modules = []
    for doc in docs:
        module_data = doc.to_dict()
        modules.append(module_data)

    return jsonify(modules), 200
@app.route('/student_dashboard/<classroom_id>', methods=['GET'])
def get_student_dashboard(classroom_id):
    quiz_attempts_ref = db.collection('quiz_attempts').where('classroom_id', '==', classroom_id)
    docs = quiz_attempts_ref.stream()

    student_scores = {}
    
    for doc in docs:
        attempt_data = doc.to_dict()
        usn = attempt_data.get('usn')
        score = attempt_data.get('score', 0)
        
        if usn not in student_scores:
            student_scores[usn] = 0
        student_scores[usn] += score

    dashboard_data = []
    
    for usn, score in student_scores.items():
        student_ref = db.collection('students').document(usn).get()
        student_name = student_ref.get('name') if student_ref.exists else 'Unknown'
        dashboard_data.append({
            'usn': usn,
            'name': student_name,
            'score': score
        })

    dashboard_data.sort(key=lambda x: x['score'], reverse=True)

    for i, student in enumerate(dashboard_data):
        student['rank'] = i + 1

    return jsonify(dashboard_data), 200
import requests # Make sure this is installed (pip install requests)

import random  # Add this at the top of your file if not already present

@app.route('/quiz/<classroom_id>/generate', methods=['POST'])
def generate_quiz(classroom_id):
    try:
        quiz_data = request.json
        topic = quiz_data.get('topic')
        
        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        # Generate a simple quiz (sample questions)
        sample_questions = [
            {
                "question": f"What is {topic}?",
                "options": [
                    f"A basic {topic}",
                    f"An advanced {topic}",
                    f"A complex {topic}",
                    f"None of the above"
                ],
                "correct_answer": 0
            },
            {
                "question": f"Which of the following is related to {topic}?",
                "options": [
                    "Option 1",
                    "Option 2",
                    "Option 3",
                    "All of the above"
                ],
                "correct_answer": 3
            }
        ]
        
        # Save the generated quiz to the 'quizzes' collection
        quiz_ref = db.collection('quizzes').document()
        quiz_ref.set({
            "classroom_id": classroom_id,
            "topic": topic,
            "questions": sample_questions,
            "generated_at": firestore.SERVER_TIMESTAMP
        })

        return jsonify({
            "success": True,
            "message": "Quiz generated and saved.",
            "quiz_id": quiz_ref.id,
            "quiz_questions": sample_questions
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to save the student's quiz attempt
@app.route('/quiz/<quiz_id>/attempt', methods=['POST'])
def save_quiz_attempt(quiz_id):
    attempt_data = request.json
    quiz_attempts_ref = db.collection('quiz_attempts').document()
    quiz_attempts_ref.set({
        "quiz_id": quiz_id,
        "usn": attempt_data.get('usn'),
        "score": attempt_data.get('score'),
        "attempted_at": firestore.SERVER_TIMESTAMP
    })
    
    return jsonify({"success": True, "message": "Quiz attempt saved."}), 201
@app.route('/quiz/response', methods=['POST'])
def save_quiz_response():
    data = request.json
    quiz_id = data.get('quiz_id')
    usn = data.get('usn')
    answered = data.get('answered')
    
    response_data = {
        "quiz_id": quiz_id,
        "usn": usn,
        "answered": answered,  # True for yes, False for no/not answered
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    
    db.collection('quiz_responses').add(response_data)
    
    return jsonify({"success": True, "message": "Response saved."}), 201

    

# Faculty endpoints for managing marks and materials
@app.route('/faculty/add-marks', methods=['POST'])
def add_student_marks():
    try:
        data = request.json
        classroom_id = data.get('classroom_id')
        usn = data.get('usn')
        marks_data = data.get('marks')  # { "test1": 85, "assignment1": 90, etc. }
        
        if not all([classroom_id, usn, marks_data]):
            return jsonify({"error": "Missing required fields"}), 400
            
        performance_ref = db.collection('student_performance').document()
        performance_ref.set({
            "classroom_id": classroom_id,
            "usn": usn,
            "marks": marks_data,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({
            "success": True,
            "message": "Marks added successfully"
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/faculty/upload-material', methods=['POST'])
def upload_material():
    try:
        data = request.json
        classroom_id = data.get('classroom_id')
        material_type = data.get('type')  # 'pdf' or 'ppt'
        material_url = data.get('url')
        title = data.get('title')
        assigned_to = data.get('assigned_to', [])  # List of student USNs
        
        if not all([classroom_id, material_type, material_url, title]):
            return jsonify({"error": "Missing required fields"}), 400
            
        material_ref = db.collection('study_materials').document()
        material_ref.set({
            "classroom_id": classroom_id,
            "type": material_type,
            "url": material_url,
            "title": title,
            "assigned_to": assigned_to,
            "uploaded_at": firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({
            "success": True,
            "message": "Material uploaded successfully",
            "material_id": material_ref.id
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/student/attendance/summary/<usn>', methods=['GET'])
def get_student_attendance_summary(usn):
    try:
        # Get all attendance records for the student
        attendance_ref = db.collection('attendance')
        attendance_docs = attendance_ref.where('present_students', 'array_contains', usn).stream()
        
        attendance_history = []
        total_classes = 0
        classes_attended = 0
        
        for doc in attendance_docs:
            data = doc.to_dict()
            attendance_history.append(data)
            total_classes += 1
            if usn in data.get('present_students', []):
                classes_attended += 1
        
        attendance_percentage = (classes_attended / total_classes * 100) if total_classes > 0 else 0
        
        return jsonify({
            "success": True,
            "summary": {
                "total_classes": total_classes,
                "classes_attended": classes_attended,
                "attendance_percentage": attendance_percentage
            },
            "attendance_history": attendance_history
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)