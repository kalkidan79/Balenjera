# 🌸 Balenjera - Your AI Best Friend

**Balenjera** (አጋር - meaning "Best Friend" in Amharic) is an anonymous AI-powered wellness platform designed specifically for boarding school students who may feel sad, stressed, or overwhelmed without access to immediate counselor support.

## 🎯 Problem We Solve

- **40-60%** of boarding students report moderate to high stress levels
- **1:500+** counselor-to-student ratio in Ethiopian boarding schools
- **70%** of teens prefer anonymous digital tools over face-to-face counseling
- **47%** reduction in crises with early intervention

## ✨ Features

### 🤖 AI Wellness Chatbot
- Gemini API integration for compassionate, intelligent responses
- Mood detection with personalized quotes
- Silent companion mode for when users don't want advice
- Emergency crisis detection with counselor alerts

### 📚 Self-Help Library
- Curated books on emotional wellness, mindfulness, and motivation
- In-browser PDF reader for instant access

### 🎵 Calming Music
- 15+ relaxing tracks for focus, meditation, and stress relief
- YouTube integration with playlist support

### 🖼️ Peaceful Gallery
- Nature, calming, and motivational images
- Lightbox viewer for full-screen experience

### 🧘 Healing Tools
- 4-4-4-4 box breathing exercise
- Daily affirmations with tap-to-refresh
- Wellness tips for grounding and self-care

### 👩‍⚕️ Counselor Dashboard
- View flagged student cases (anonymous identity)
- Mark cases as resolved
- Contact guidance for follow-up

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML5, CSS3, JavaScript (Vanilla) |
| Backend | Python Flask |
| AI | Google Gemini API |
| Database | In-memory (easily upgradeable to PostgreSQL) |
| Deployment | Any cloud platform (Render, Heroku, PythonAnywhere) |

## 📁 Project Structure
balenjera/
├── backend/
│ ├── app.py # Flask server with Gemini integration
│ ├── requirements.txt # Python dependencies
│ └── .env # API keys (not committed)
├── frontend/
│ ├── index.html # Landing page with research stats
│ ├── login.html # Authentication (student/counselor)
│ ├── dashboard.html # Student dashboard
│ ├── counselor.html # Counselor flagged cases view
│ ├── chatbot.html # AI wellness chat
│ ├── books.html # Self-help library with PDF viewer
│ ├── music.html # Calming music player
│ ├── pictures.html # Peaceful image gallery
│ ├── healing.html # Breathing exercise & affirmations
│ ├── css/style.css # Global styles
│ └── js/ # JavaScript modules
└── README.md