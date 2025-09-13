from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI()

# In-memory storage for demonstration
students = {}
faculties = {}
classes = {}
materials = {}
attendance = {}
marks = {}

class StudentSignup(BaseModel):
    usn: str
    name: str
    email: str

class FacultySignup(BaseModel):
    teacher_code: str
    name: str
    email: str

class CreateClass(BaseModel):
    classroom_id: str
    teacher_code: str
    college_name: str
    subject: str

class UploadMaterial(BaseModel):
    classroom_id: str
    type: str
    url: str
    title: str

class Attendance(BaseModel):
    usns: List[str]

class AddMarks(BaseModel):
    classroom_id: str
    usn: str
    marks: Dict[str, int]

@app.post("/signup/student")
def signup_student(data: StudentSignup):
    students[data.usn] = data.dict()
    return {"message": "Student signed up", "student": data}

@app.post("/signup/faculty")
def signup_faculty(data: FacultySignup):
    faculties[data.teacher_code] = data.dict()
    return {"message": "Faculty signed up", "faculty": data}

@app.post("/create_class")
def create_class(data: CreateClass):
    classes[data.classroom_id] = data.dict()
    return {"message": "Class created", "class": data}

@app.get("/class_details/{classroom_id}")
def get_class_details(classroom_id: str):
    class_info = classes.get(classroom_id)
    if not class_info:
        return {"error": "Class not found"}
    return {"class_details": class_info}

@app.post("/faculty/upload-material")
def upload_material(data: UploadMaterial):
    materials.setdefault(data.classroom_id, []).append(data.dict())
    return {"message": "Material uploaded", "material": data}

@app.post("/attendance/{classroom_id}")
def take_attendance(classroom_id: str, data: Attendance):
    attendance.setdefault(classroom_id, []).extend(data.usns)
    return {"message": "Attendance taken", "usns": data.usns}

@app.post("/faculty/add-marks")
def add_marks(data: AddMarks):
    marks.setdefault(data.classroom_id, {})[data.usn] = data.marks
    return {"message": "Marks added", "usn": data.usn, "marks": data.marks}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)