import random
import requests
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import motor.motor_asyncio
from bson import ObjectId
from model import SpeechModel
import uvicorn
from contextlib import asynccontextmanager

# MongoDB Connection
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
db = client["college_app"]
speech_model = SpeechModel()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await client.server_info()
        print("✅ MongoDB connected successfully!")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("💡 Make sure MongoDB is running on localhost:27017")
    yield
    # Shutdown
    client.close()
    print("✅ MongoDB connection closed")

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class UserData(BaseModel):
    name: str
    email: str
    usn: str

class FacultyData(BaseModel):
    name: str
    email: str
    teacher_code: str

class QuizData(BaseModel):
    topic: str

class QuizAttemptData(BaseModel):
    usn: str
    score: int

class MaterialData(BaseModel):
    classroom_id: str
    type: str
    url: str
    title: str
    assigned_to: list = []

class MarksData(BaseModel):
    classroom_id: str
    usn: str
    marks: dict

@app.get("/")
async def index():
    return "FastAPI app is running and connected to MongoDB!"

@app.get("/ping-db")
async def ping_db():
    try:
        # Test MongoDB connection by inserting and retrieving a test document
        result = await db.test_connection.insert_one({"test": "connection_check", "timestamp": "2025-09-14"})
        user = await db.test_connection.find_one({"_id": result.inserted_id})
        # Clean up test document
        await db.test_connection.delete_one({"_id": result.inserted_id})
        return {"connected": True, "message": "MongoDB connection successful!", "test_document": {"_id": str(user["_id"]), "test": user["test"]}}
    except Exception as e:
        return {"connected": False, "error": str(e)}

@app.post("/users", status_code=201)
async def create_user(user_data: dict):
    result = await db.users.insert_one(user_data)
    return {"id": str(result.inserted_id)}

@app.get("/users")
async def get_users():
    users = []
    cursor = db.users.find({})
    async for user in cursor:
        user["_id"] = str(user["_id"])
        users.append(user)
    return users

@app.post("/quizzes", status_code=201)
async def create_quiz(quiz_data: dict):
    result = await db.quizzes.insert_one(quiz_data)
    return {"id": str(result.inserted_id)}

@app.get("/quizzes/{quiz_id}")
async def get_quiz(quiz_id: str):
    quiz = await db.quizzes.find_one({"_id": ObjectId(quiz_id)})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    quiz["_id"] = str(quiz["_id"])
    return quiz

@app.post("/login/student")
async def student_login(data: dict):
    student_usn = data.get('usn')
    classroom_id = data.get('classroom_id')
    if not all([student_usn, classroom_id]):
        raise HTTPException(status_code=400, detail="USN and Classroom ID are required.")
    student = await db.students.find_one({"usn": student_usn})
    if not student:
        raise HTTPException(status_code=401, detail="Invalid student USN.")
    classroom = await db.classrooms.find_one({"_id": classroom_id})
    if not classroom or not classroom.get("is_active"):
        raise HTTPException(status_code=404, detail="Classroom not found or is not active.")
    return {"success": True, "message": "Student logged in successfully!"}

@app.post("/signup/student", status_code=201)
async def student_signup(data: dict):
    usn = data.get('usn')
    name = data.get('name')
    email = data.get('email')
    if not all([usn, name, email]):
        raise HTTPException(status_code=400, detail="USN, name, and email are required for signup.")
    existing = await db.students.find_one({"usn": usn})
    if existing:
        raise HTTPException(status_code=409, detail="Student with this USN already exists.")
    await db.students.insert_one({"usn": usn, "name": name, "email": email})
    return {"success": True, "message": "Student profile created successfully!"}

@app.get("/student/profile/{usn}")
async def get_student_profile(usn: str):
    student = await db.students.find_one({"usn": usn})
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")
    attendance_cursor = db.attendance.find({"usn": usn})
    attendance_data, total_classes, classes_attended = [], 0, 0
    async for att in attendance_cursor:
        attendance_data.append(att)
        total_classes += 1
        if att.get("present", False):
            classes_attended += 1
    attendance_percentage = (classes_attended / total_classes * 100) if total_classes > 0 else 0
    performance_cursor = db.student_performance.find({"usn": usn})
    weekly_performance = [perf async for perf in performance_cursor]
    documents_cursor = db.study_materials.find({"assigned_to": usn})
    assigned_documents = [doc async for doc in documents_cursor]
    return {
        "student_info": student,
        "attendance": {
            "total_classes": total_classes,
            "classes_attended": classes_attended,
            "attendance_percentage": attendance_percentage,
            "attendance_history": attendance_data
        },
        "weekly_performance": weekly_performance,
        "assigned_documents": assigned_documents
    }

@app.post("/student/chat")
async def student_chat(data: dict):
    student_query = data.get('query')
    document_id = data.get('document_id')
    response = {
        "answer": f"This is a placeholder response for: {student_query}",
        "related_documents": []
    }
    return response

@app.post("/signup/faculty", status_code=201)
async def faculty_signup(data: dict):
    teacher_code = data.get('teacher_code')
    name = data.get('name')
    email = data.get('email')
    if not all([teacher_code, name, email]):
        raise HTTPException(status_code=400, detail="Teacher code, name, and email are required for signup.")
    existing = await db.teachers.find_one({"teacher_code": teacher_code})
    if existing:
        raise HTTPException(status_code=409, detail="Faculty with this teacher code already exists.")
    await db.teachers.insert_one({"teacher_code": teacher_code, "name": name, "email": email})
    return {"success": True, "message": "Faculty profile created successfully!"}

@app.get("/faculty/profile/{teacher_code}")
async def get_faculty_profile(teacher_code: str):
    faculty = await db.teachers.find_one({"teacher_code": teacher_code})
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found.")
    return faculty

@app.get("/dashboard/faculty/{teacher_code}")
async def faculty_dashboard(teacher_code: str):
    faculty = await db.teachers.find_one({"teacher_code": teacher_code})
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found.")
    classes_cursor = db.classrooms.find({"teacher_code": teacher_code})
    my_classes = []
    async for doc in classes_cursor:
        performance_cursor = db.student_performance.find({"classroom_id": doc["_id"]})
        class_performance = [perf async for perf in performance_cursor]
        attendance_cursor = db.attendance.find({"classroom_id": doc["_id"]})
        attendance_data = [att async for att in attendance_cursor]
        total_students = len(doc.get("students", []))
        avg_attendance = sum(len(att.get("present_students", [])) for att in attendance_data) / len(attendance_data) if attendance_data else 0
        doc.update({
            "total_students": total_students,
            "average_attendance": avg_attendance,
            "performance_data": class_performance,
            "attendance_history": attendance_data
        })
        my_classes.append(doc)
    return {"success": True, "message": "Faculty dashboard data retrieved.", "profile": faculty, "my_classes": my_classes}

@app.post("/create_class", status_code=201)
async def create_class(data: dict):
    classroom_id = data.get('classroom_id')
    teacher_code = data.get('teacher_code')
    college_name = data.get('college_name')
    subject = data.get('subject', '')
    max_students = data.get('max_students', 60)
    if not all([classroom_id, teacher_code, college_name]):
        raise HTTPException(status_code=400, detail="Classroom ID, teacher code, and college name are required.")
    teacher = await db.teachers.find_one({"teacher_code": teacher_code})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid teacher code.")
    existing_class = await db.classrooms.find_one({"_id": classroom_id})
    if existing_class:
        raise HTTPException(status_code=409, detail="Classroom ID already exists.")
    await db.classrooms.insert_one({
        "_id": classroom_id,
        "teacher_code": teacher_code,
        "college_name": college_name,
        "subject": subject,
        "max_students": max_students,
        "current_students": 0,
        "students": [],
        "is_active": True
    })
    return {"success": True, "message": "Class created successfully!"}

@app.get("/my_classes/{teacher_code}")
async def get_my_classes(teacher_code: str):
    cursor = db.classrooms.find({"teacher_code": teacher_code})
    class_list = []
    async for doc in cursor:
        class_list.append(doc)
    return class_list

@app.post("/speech/listen")
async def start_listening():
    text = speech_model.listen_from_microphone()
    if text:
        transcript_data = {"text": text, "type": "teacher_speech"}
        result = await db.transcripts.insert_one(transcript_data)
        return {"success": True, "text": text, "transcript_id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=400, detail="Could not understand audio")

@app.post("/speech/speak")
async def text_to_speech(data: dict):
    text = data.get('text', '')
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    speech_model.text_to_speech(text)
    return {"success": True, "message": "Text converted to speech successfully"}

@app.get("/speech/transcripts")
async def get_transcripts():
    transcripts = []
    cursor = db.transcripts.find({})
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        transcripts.append(doc)
    return {"success": True, "transcripts": transcripts}

@app.get("/speech/test-microphone")
async def test_microphone():
    return {"success": True, "message": "Speech recognition is ready", "engines": speech_model.get_available_engines()}

if __name__ == '__main__':
    print("🚀 Starting FastAPI Server...")
    print(f"📡 Server will be available at:")
    print(f"   • http://localhost:5000")
    print(f"   • http://127.0.0.1:5000")
    print(f"   • http://0.0.0.0:5000")
    print("🔄 Auto-reload enabled for development")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=5000, 
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Try running: pip install uvicorn fastapi motor")
        input("Press Enter to exit...")
