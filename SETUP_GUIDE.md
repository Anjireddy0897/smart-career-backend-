# Smart Career Backend - Complete Setup Guide

## ✅ Status: All APIs Working

### Backend Endpoints Verified
- ✅ `POST /api/auth/register` - User registration
- ✅ `POST /api/personal-details` - Save personal information
- ✅ `POST /api/education-details` - Save education information
- ✅ `POST /api/career-assessment` - Submit career assessment
- ✅ `GET /api/profile/<email>` - Get user profile
- ✅ `GET /api/career-assessment/<user_id>` - Get assessment results

### React Components Created

#### 1. **App.jsx** - Main Application
The complete application with:
- Home page with registration/login options
- Multi-step form workflow (3 steps)
- Progress indicator
- User authentication flow

```jsx
import App from "./App.jsx";
// Use directly in your React application
```

#### 2. **RegisterForm.jsx** - User Registration (Step 0)
Handles user account creation with fields:
- Full Name 👤
- Email ✉️
- Password 🔒
- Confirm Password 🔒
- Gender ⚧ (optional)
- Phone Number 📞 (optional)

**Features:**
- Two-step submission (register + personal details)
- Password visibility toggle
- Real-time validation
- Success/error messages

```jsx
import RegisterForm from "./RegisterForm.jsx";

<RegisterForm 
  apiBaseUrl="http://127.0.0.1:5000"
  onSuccess={(user) => console.log("User created:", user)}
  onNavigateToLogin={() => goToLogin()}
/>
```

#### 3. **LoginForm.jsx** - User Login
Simple login form with:
- Email ✉️
- Password 🔒

```jsx
import LoginForm from "./LoginForm.jsx";

<LoginForm 
  apiBaseUrl="http://127.0.0.1:5000"
  onSuccess={(user) => console.log("Logged in:", user)}
  onNavigateToRegister={() => goToRegister()}
/>
```

#### 4. **PersonalDetailsForm.jsx** - Step 1 of 4
Complete personal information form:
- Full Name 👤
- Date of Birth 📅 (date picker)
- Gender ⚧ (dropdown)
- Phone Number 📞 (validated 7-15 digits)
- City 📍

```jsx
import PersonalDetailsForm from "./PersonalDetailsForm.jsx";

<PersonalDetailsForm 
  userId={user.id}
  apiBaseUrl="http://127.0.0.1:5000"
/>
```

#### 5. **EducationDetailsForm.jsx** - Step 2 of 4
Education history form with:
- Current Education Level 🎓
- Stream (Science, Commerce, Engineering, etc.)
- School/College Name
- Average Percentage/GPA

```jsx
import EducationDetailsForm from "./EducationDetailsForm.jsx";

<EducationDetailsForm 
  userId={user.id}
  apiBaseUrl="http://127.0.0.1:5000"
/>
```

#### 6. **CareerAssessmentForm.jsx** - Step 3 of 4
10-question career assessment:
- Dynamic skill scoring
- Career category matching
- Personalized career recommendations
- Salary and demand information

```jsx
import CareerAssessmentForm from "./CareerAssessmentForm.jsx";

<CareerAssessmentForm 
  userId={user.id}
  apiBaseUrl="http://127.0.0.1:5000"
/>
```

---

## 🚀 How to Use

### Option 1: Use Complete App (Recommended)
```jsx
import React from 'react';
import App from './App.jsx';

function MyApp() {
  return <App />;
}

export default MyApp;
```

This includes:
1. Home page
2. Registration
3. Login
4. Multi-step dashboard with all forms
5. Progress tracking

### Option 2: Use Individual Forms

```jsx
import React, { useState } from 'react';
import RegisterForm from './RegisterForm.jsx';
import PersonalDetailsForm from './PersonalDetailsForm.jsx';
import EducationDetailsForm from './EducationDetailsForm.jsx';
import CareerAssessmentForm from './CareerAssessmentForm.jsx';

function MyApp() {
  const [user, setUser] = useState(null);
  const [step, setStep] = useState(1);

  return (
    <div>
      {!user ? (
        <RegisterForm 
          apiBaseUrl="http://127.0.0.1:5000"
          onSuccess={setUser}
        />
      ) : step === 1 ? (
        <PersonalDetailsForm userId={user.id} />
      ) : step === 2 ? (
        <EducationDetailsForm userId={user.id} />
      ) : (
        <CareerAssessmentForm userId={user.id} />
      )}
    </div>
  );
}
```

---

## 🔧 API Endpoints Reference

### Registration
```
POST /api/auth/register
Content-Type: application/json

{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "confirm_password": "password123"
}

Response:
{
  "success": true,
  "user": {
    "id": 1,
    "full_name": "John Doe",
    "email": "john@example.com"
  }
}
```

### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}

Response:
{
  "success": true,
  "user": { ... }
}
```

### Save Personal Details
```
POST /api/personal-details
Content-Type: application/json

{
  "user_id": 1,
  "date_of_birth": "1995-05-15",
  "gender": "male",
  "phone_number": "9876543210",
  "city": "New York"
}

Response:
{
  "success": true,
  "message": "Personal details created successfully.",
  "personal_details": { ... }
}
```

### Save Education Details
```
POST /api/education-details
Content-Type: application/json

{
  "user_id": 1,
  "current_education_level": "bachelors",
  "stream": "science",
  "school_college_name": "MIT",
  "average_percentage_gpa": "3.8"
}

Response:
{
  "success": true,
  "message": "Education details created successfully.",
  "education_details": { ... }
}
```

### Submit Career Assessment
```
POST /api/career-assessment
Content-Type: application/json

{
  "user_id": 1,
  "q1": "very interested",
  "q2": "interested",
  "q3": "neutral",
  "q4": "not interested",
  "q5": "very interested",
  "q6": "interested",
  "q7": "neutral",
  "q8": "not interested",
  "q9": "very interested",
  "q10": "interested"
}

Response:
{
  "success": true,
  "assessment": {
    "assessment_id": 1,
    "user_id": 1,
    "primaryCareerPath": "IT & Technology",
    "topScore": 35,
    "recommendedCareers": [
      {
        "career": "Software Engineer",
        "score": 35,
        "skillsRequired": ["Python", "JavaScript", "DSA", "Git"],
        "roadmap": [...],
        "salaryRange": "4-20 LPA",
        "demandLevel": "High"
      }
    ]
  }
}
```

---

## ⚠️ Common "Failed to Fetch" Solutions

If you're still seeing "Failed to fetch":

1. **Backend Not Running**
   - Ensure Flask server is running on `http://127.0.0.1:5000`
   - Check terminal for `Running on http://127.0.0.1:5000`

2. **CORS Issues**
   - ✅ Already configured in backend
   - Check browser console for CORS errors

3. **Invalid User ID**
   - User must be registered first
   - Pass valid `user_id` or `email`

4. **Network Issues**
   - Check if backend URL is correct
   - Verify firewall allows localhost:5000

5. **Invalid Data Format**
   - Phone number must be 7-15 digits
   - Email must be valid format
   - Passwords must match and be 6+ chars

---

## 📦 File Structure

```
smart career backend/
├── app.py                        (Backend Flask)
├── career_backend.db             (SQLite Database)
├── requirements.txt              (Python dependencies)
├── App.jsx                       (Main app component)
├── RegisterForm.jsx              (Registration form)
├── LoginForm.jsx                 (Login form)
├── PersonalDetailsForm.jsx       (Step 1 form)
├── EducationDetailsForm.jsx      (Step 2 form)
├── CareerAssessmentForm.jsx      (Step 3 form)
└── SETUP_GUIDE.md               (This file)
```

---

## ✨ Features

- ✅ Complete user authentication (register/login)
- ✅ Multi-step form workflow
- ✅ Real-time validation
- ✅ Error handling
- ✅ Success feedback
- ✅ Password visibility toggle
- ✅ Responsive design
- ✅ Progress tracking
- ✅ Career recommendations
- ✅ CORS enabled for frontend integration

---

## 🧪 Testing

All endpoints have been tested and verified:
- ✅ Registration: Successfully creates user
- ✅ Personal Details: Successfully saves information
- ✅ Login: Successfully authenticates users
- ✅ Career Assessment: Successfully evaluates and scores

Backend is running on: `http://127.0.0.1:5000`
