# FastAPI Backend with Speech Recognition

A comprehensive FastAPI backend application with MongoDB integration and speech recognition capabilities for educational management system.

## Features

- **FastAPI Backend** with async/await support
- **MongoDB Integration** using Motor (async MongoDB driver)
- **Speech Recognition** with microphone input support
- **Text-to-Speech** functionality
- **Educational Management System** with student, faculty, and classroom management
- **Authentication System** for students and faculty
- **CORS Support** for cross-origin requests
- **Real-time Speech Transcription** and storage

## API Endpoints

### General
- `GET /` - Health check
- `GET /ping-db` - Database connection test

### Authentication
- `POST /login/student` - Student login
- `POST /signup/student` - Student registration
- `POST /signup/faculty` - Faculty registration

### User Management
- `GET /student/profile/{usn}` - Get student profile
- `GET /faculty/profile/{teacher_code}` - Get faculty profile
- `GET /dashboard/faculty/{teacher_code}` - Faculty dashboard

### Classroom Management
- `POST /create_class` - Create new classroom
- `GET /my_classes/{teacher_code}` - Get teacher's classes

### Speech Recognition
- `POST /speech/listen` - Listen from microphone and transcribe
- `POST /speech/speak` - Convert text to speech
- `GET /speech/transcripts` - Get all transcripts
- `GET /speech/test-microphone` - Test microphone functionality

## Setup and Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ayush1234566/detect.git
   cd detect
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start MongoDB**
   Make sure MongoDB is running on `localhost:27017`

5. **Run the application**
   ```bash
   python main.py
   ```

The server will start on `http://localhost:5000`

## Technologies Used

- **FastAPI** - Modern, fast web framework for building APIs
- **MongoDB** - NoSQL database for data storage
- **Motor** - Async MongoDB driver for Python
- **SpeechRecognition** - Library for performing speech recognition
- **pyttsx3** - Text-to-speech conversion library
- **PyAudio** - Audio I/O library for microphone access
- **Uvicorn** - ASGI server for running FastAPI applications

## Project Structure

```
├── main.py              # Main FastAPI application
├── model.py             # Speech recognition model
├── requirements.txt     # Python dependencies
├── test_api.py          # API testing script
├── test_login.py        # Login testing script
├── test.html           # HTML test interface
├── .gitignore          # Git ignore file
└── README.md           # Project documentation
```

## Usage Examples

### Test Speech Recognition
```python
# Test microphone
curl http://localhost:5000/speech/test-microphone

# Listen and transcribe
curl -X POST http://localhost:5000/speech/listen

# Convert text to speech
curl -X POST http://localhost:5000/speech/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test message"}'
```

### Student Operations
```python
# Student signup
curl -X POST http://localhost:5000/signup/student \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "usn": "1AB21CS001"}'

# Student login
curl -X POST http://localhost:5000/login/student \
  -H "Content-Type: application/json" \
  -d '{"usn": "1AB21CS001", "classroom_id": "CS101"}'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.