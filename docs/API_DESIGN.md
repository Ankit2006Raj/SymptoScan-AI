# API Design: SymptoScan AI

## Base URL
`/api/v1`

## Authentication (`/auth`)
- `POST /auth/register` - Register a new user.
- `POST /auth/login` - Authenticate and return JWT.
- `POST /auth/refresh` - Refresh JWT token.
- `POST /auth/logout` - Invalidate token.

## Users & Profiles (`/users`)
- `GET /users/me` - Get current user profile.
- `PUT /users/me` - Update profile (demographics, medical history).
- `GET /users` - [Admin] List users.
- `DELETE /users/{id}` - [Admin] Delete user.

## Assessments & Symptom Checker (`/assessments`)
- `POST /assessments/analyze` - Submit symptoms for AI analysis.
    - **Payload**: `{"symptoms": [...], "duration": 3, "severity": 7}`
    - **Response**: `{"possible_conditions": [...], "follow_up_questions": [...]}`
- `POST /assessments` - Save a completed assessment.
- `GET /assessments` - Get user's assessment history.
- `GET /assessments/{id}` - Get specific assessment details.

## Disease Risk Prediction (`/predictions`)
- `POST /predictions/diabetes` - Predict diabetes risk.
- `POST /predictions/heart` - Predict heart disease risk.
- `POST /predictions/kidney` - Predict kidney disease risk.
- `POST /predictions/liver` - Predict liver disease risk.
    - **Payload**: Requires specific clinical markers (e.g., BMI, age, blood pressure, etc. depending on model).
    - **Response**: `{"risk_score": 0.85, "severity": "High", "factors": [...]}`

## Medical Reports (OCR) (`/reports`)
- `POST /reports/upload` - Upload PDF/Image for OCR processing.
    - **Payload**: `multipart/form-data`
    - **Response**: `{"task_id": "...", "status": "processing"}`
- `GET /reports/status/{task_id}` - Check OCR task status.
- `GET /reports` - List user's uploaded reports and extracted markers.

## AI Health Assistant (`/chat`)
- `POST /chat/sessions` - Start a new chat session.
- `POST /chat/sessions/{id}/message` - Send a message to AI assistant.
    - **Payload**: `{"message": "I have a headache."}`
    - **Response**: `{"reply": "...", "suggested_actions": [...]}`
- `GET /chat/sessions` - List chat history.

## Recommendations (`/recommendations`)
- `GET /recommendations` - Get personalized health recommendations based on recent assessments and profile.

## Admin Analytics (`/admin`)
- `GET /admin/stats` - Global platform statistics (users, assessments, model performance).
