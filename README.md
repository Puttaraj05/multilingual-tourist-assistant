# 🌍 TravelMate — Multilingual Tourist Assistant

> **An AI-powered multilingual tourist assistance platform for smarter travel planning, communication, discovery, navigation, and emergency support.**

---

## 📌 Overview

**TravelMate** is a multilingual AI-powered tourist assistance platform designed to make travel easier, safer, and more accessible.

The platform brings multiple travel-related capabilities together in one application, including:

* 🤖 AI-powered tourist assistance
* 🗺️ Personalized itinerary planning
* 🌐 Multilingual text translation
* 📷 OCR-based image text extraction and translation
* 🎙️ Speech processing and voice assistance
* 📍 Location-based recommendations
* 🧭 Nearby place discovery
* 🚨 Emergency assistance
* 🔐 User authentication
* 💬 Conversation history
* 🌎 Multilingual interface support

TravelMate uses **Generative AI, FastAPI, MongoDB, Geoapify, OpenStreetMap, Overpass API, OCR, speech processing, and browser geolocation** to provide an integrated tourist experience.

---

# ✨ Key Features

## 🤖 AI Travel Assistant

TravelMate provides an AI-powered conversational assistant designed specifically for tourism-related interactions.

Users can ask questions about:

* Destinations
* Travel planning
* Places to visit
* Local activities
* Tourist assistance
* Travel-related information
* General trip guidance

The AI functionality is powered by **Google Gemini**.

The backend separates AI functionality into dedicated services and prompts, making the conversational system easier to maintain and extend.

### AI Request Flow

```text
User
 ↓
Frontend Chat Interface
 ↓
FastAPI Chat Router
 ↓
Chat Service
 ↓
Gemini Service
 ↓
Google Gemini API
 ↓
AI Response
 ↓
Frontend
```

---

# 🗺️ Personalized Travel Planner

The Travel Planner allows users to generate travel plans based on their requirements.

The planner can be used for organizing:

* Destinations
* Trip duration
* Activities
* Places to visit
* Daily travel plans
* Personalized itineraries

The itinerary functionality is implemented through a dedicated backend API and AI service integration.

---

# 🌐 Multilingual Translator

TravelMate provides multilingual translation functionality for tourists.

Users can:

* Enter text
* Select source language
* Select target language
* Translate content
* Detect the input language
* Use supported languages through the translation system

The application also includes a global interface language selector.

### Supported Interface Languages

| Language     | Code |
| ------------ | ---- |
| 🇬🇧 English | `en` |
| 🇮🇳 Hindi   | `hi` |
| 🇮🇳 Telugu  | `te` |

The localization system is implemented using frontend language files:

```text
frontend/js/i18n/
├── en.js
├── hi.js
├── te.js
└── i18n.js
```

---

# 📷 OCR Image Translation

Travelers can upload an image containing text and use TravelMate to extract and translate the content.

### Workflow

```text
Image Upload
     ↓
Image Processing
     ↓
OCR
     ↓
Text Extraction
     ↓
Language Detection
     ↓
Translation
     ↓
Translated Text
```

The backend includes a dedicated OCR service.

The project uses **EasyOCR** and image-processing libraries for extracting text from images.

This feature can be useful for:

* Restaurant menus
* Road signs
* Tourist information
* Tickets
* Notices
* Information boards
* Printed documents

---

# 🎙️ Speech & Voice Support

TravelMate includes speech-related backend functionality.

The project contains dedicated services and API routes for speech processing.

Technologies included in the project dependencies include:

* Faster Whisper
* Edge TTS
* PyAV
* CTranslate2

This provides the foundation for speech recognition and text-to-speech capabilities within the tourist assistant.

---

# 📍 Location-Based Recommendations

TravelMate helps tourists discover useful places around a destination or their current location.

Users can search for:

* 🍽️ Restaurants
* 🏨 Hotels
* ☕ Cafés
* 🏛️ Attractions
* 🛍️ Shopping
* 🌳 Parks
* 🏥 Hospitals
* 💊 Pharmacies
* 🏧 ATMs
* ⛽ Fuel stations
* 🅿️ Parking
* 🛒 Supermarkets
* 🛏️ Hostels
* 🏠 Guest houses
* And other useful nearby services

## Search Methods

Users can:

1. Search for a city or destination
2. Use **Near Me**
3. Select a search radius
4. Select a category
5. Retrieve nearby recommendations

The frontend supports configurable search distances such as:

* 5 km
* 10 km
* 15 km
* 25 km

Recommendations can display:

* Place name
* Category
* Address
* Rating
* Distance
* Opening hours
* Description
* Navigation link
* Source/details link

---

# 🗺️ OpenStreetMap Integration

TravelMate also uses **OpenStreetMap** data for location-based tourist assistance.

The project integrates OpenStreetMap through the **Overpass API** for searching nearby real-world services.

This is used particularly for emergency-related nearby-place discovery.

### OpenStreetMap Workflow

```text
User Location
     ↓
Latitude + Longitude
     ↓
OpenStreetMap / Overpass API
     ↓
Nearby Real-World Services
     ↓
Filter & Format Results
     ↓
TravelMate UI
```

The OpenStreetMap integration allows the application to search for real-world services around a user's location without relying exclusively on a single commercial map provider.

---

# 🌍 Geoapify Integration

TravelMate also contains a dedicated Geoapify service for location-based recommendations.

### Recommendation Flow

```text
User Search / Location
        ↓
Recommendation API
        ↓
Recommendation Service
        ↓
Geoapify Service
        ↓
Nearby Places
        ↓
Formatted Recommendations
        ↓
Frontend
```

This provides location-aware place discovery and recommendation functionality.

---

# 🚨 Emergency Assistance

TravelMate includes a dedicated emergency assistance module designed to help tourists access important safety-related information.

The emergency functionality includes:

* Emergency contacts
* Emergency services
* Nearby service discovery
* Incident information
* Location-based emergency assistance

The emergency API also uses **OpenStreetMap / Overpass API** to search nearby real-world services.

Example backend functionality includes searching for nearby services such as relevant emergency facilities based on geographic coordinates.

### Emergency Location Flow

```text
User Location
     ↓
Latitude / Longitude
     ↓
Emergency API
     ↓
OpenStreetMap / Overpass API
     ↓
Nearby Emergency Services
     ↓
Formatted Results
     ↓
TravelMate Emergency Page
```

---

# 🔐 Authentication

TravelMate includes authentication functionality for user accounts.

The backend provides a dedicated authentication router:

```text
backend/api/auth.py
```

The frontend contains:

```text
frontend/js/auth.js
frontend/js/auth-state.js
frontend/auth.html
```

Authentication-related functionality includes:

* User registration
* User login
* Authentication state management
* Protected/user-oriented functionality

The project also includes security-related dependencies such as:

* bcrypt
* passlib
* python-jose
* email-validator

---

# 💬 Conversation History

TravelMate maintains conversation-related functionality through dedicated backend components.

```text
backend/api/chat.py
backend/api/chat_history.py
backend/services/chat_service.py
backend/services/conversation_service.py
backend/models/chat.py
backend/models/conversation.py
```

This separates:

* Chat API handling
* Conversation processing
* AI service communication
* Conversation data models
* Chat history functionality

---

# 🗄️ MongoDB Database

TravelMate uses **MongoDB** for backend data storage.

Database functionality is organized under:

```text
backend/database/
└── mongodb.py
```

MongoDB is used as part of the backend architecture for application data and user/conversation-related functionality.

**MongoDB Atlas** can be configured using the MongoDB connection string stored in environment variables.

---

# 🧠 Generative AI Architecture

The AI functionality is separated into dedicated backend components.

```text
backend/
├── prompts/
│   └── tourist_chat.py
│
└── services/
    ├── gemini_service.py
    ├── chat_service.py
    └── conversation_service.py
```

### AI Architecture

```text
User
 ↓
Frontend Chat Interface
 ↓
FastAPI Chat Router
 ↓
Chat Service
 ↓
Gemini Service
 ↓
Google Gemini API
 ↓
AI Response
 ↓
Frontend
```

This architecture separates the API layer from AI business logic and makes the application easier to maintain.

---

# 🏗️ Actual Project Architecture

The project follows a modular **FastAPI backend + HTML/CSS/JavaScript frontend** architecture.

```text
multilingual-tourist-assistant/
│
├── backend/
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── chat_history.py
│   │   ├── emergency.py
│   │   ├── itinerary.py
│   │   ├── recommendation.py
│   │   ├── speech_router.py
│   │   └── translator.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   └── mongodb.py
│   │
│   ├── models/
│   │   ├── chat.py
│   │   └── conversation.py
│   │
│   ├── prompts/
│   │   └── tourist_chat.py
│   │
│   ├── schemas/
│   │   └── recommendation.py
│   │
│   ├── services/
│   │   ├── chat_service.py
│   │   ├── conversation_service.py
│   │   ├── gemini_service.py
│   │   ├── geoapify_service.py
│   │   ├── ocr_service.py
│   │   ├── places_service.py
│   │   ├── recommendation_service.py
│   │   ├── speech_service.py
│   │   └── translation_service.py
│   │
│   ├── utils/
│   │   ├── distance.py
│   │   └── navigation.py
│   │
│   ├── config.py
│   ├── list_models.py
│   └── main.py
│
├── frontend/
│   │
│   ├── css/
│   │   ├── chat.css
│   │   └── style.css
│   │
│   ├── images/
│   │   ├── Heroimg.png
│   │   └── logo.webp
│   │
│   ├── js/
│   │   ├── auth.js
│   │   ├── auth-state.js
│   │   ├── chat.js
│   │   ├── dashboard.js
│   │   ├── emergency.js
│   │   ├── global-language.js
│   │   ├── itinerary.js
│   │   ├── planner-language.js
│   │   ├── planner.js
│   │   ├── recommendations.js
│   │   ├── translation.js
│   │   │
│   │   └── i18n/
│   │       ├── en.js
│   │       ├── hi.js
│   │       ├── i18n.js
│   │       └── te.js
│   │
│   ├── about.html
│   ├── auth.html
│   ├── chat.html
│   ├── dashboard.html
│   ├── emergency.html
│   ├── features.html
│   ├── index.html
│   ├── itinerary.html
│   ├── planner.html
│   ├── recommendations.html
│   └── translation.html
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

> `__pycache__` files and backup files are development artifacts and are not part of the functional architecture.

---

# 🔄 Complete System Architecture

```text
                         ┌──────────────────────────┐
                         │        TRAVELMATE        │
                         │ Multilingual Tourist AI  │
                         └────────────┬─────────────┘
                                      │
                         ┌────────────▼────────────┐
                         │        FRONTEND         │
                         │    HTML + CSS + JS       │
                         └────────────┬────────────┘
                                      │
                              HTTP / JSON APIs
                                      │
                         ┌────────────▼────────────┐
                         │        FASTAPI           │
                         │      Backend API         │
                         └────────────┬────────────┘
                                      │
          ┌───────────────┬───────────┼───────────┬───────────────┐
          │               │           │           │               │
          ▼               ▼           ▼           ▼               ▼
       AI Chat        Translator   Planner    Recommendations   Emergency
          │               │           │           │               │
          ▼               ▼           ▼           ▼               ▼
       Gemini         Translation   Gemini     Geoapify      OpenStreetMap
       Service        + Language    Service     Service       / Overpass
          │               │           │           │               │
          └───────────────┴───────────┴───────────┴───────────────┘
                                      │
                         ┌────────────▼────────────┐
                         │        SERVICES          │
                         │ OCR / Speech / AI /     │
                         │ Translation / Places    │
                         └────────────┬────────────┘
                                      │
                         ┌────────────▼────────────┐
                         │        MongoDB            │
                         │       Database            │
                         └──────────────────────────┘
```

---

# 🔌 Backend API Modules

The FastAPI application registers dedicated routers for the major features.

| API Module          | Responsibility                            |
| ------------------- | ----------------------------------------- |
| `auth.py`           | Authentication                            |
| `chat.py`           | AI chat                                   |
| `chat_history.py`   | Conversation history                      |
| `emergency.py`      | Emergency assistance                      |
| `itinerary.py`      | Itinerary/planner functionality           |
| `recommendation.py` | Location recommendations                  |
| `speech_router.py`  | Speech functionality                      |
| `translator.py`     | Translation and OCR-related functionality |

These routers are registered in:

```text
backend/main.py
```

---

# 🧩 Backend Services

The service layer contains the application's main business logic.

| Service                     | Purpose                    |
| --------------------------- | -------------------------- |
| `chat_service.py`           | Chat processing            |
| `conversation_service.py`   | Conversation handling      |
| `gemini_service.py`         | Google Gemini integration  |
| `geoapify_service.py`       | Geoapify location services |
| `ocr_service.py`            | Image OCR                  |
| `places_service.py`         | Place-related operations   |
| `recommendation_service.py` | Recommendation processing  |
| `speech_service.py`         | Speech processing          |
| `translation_service.py`    | Translation functionality  |

---

# 🛠️ Technology Stack

## Frontend

* HTML5
* CSS3
* JavaScript
* Poppins
* Font Awesome
* Browser Geolocation API

## Backend

* Python
* FastAPI
* Uvicorn
* Pydantic

## Generative AI

* Google Gemini API
* `google-genai`

## Database

* MongoDB
* PyMongo
* MongoDB Atlas

## Translation

* Deep Translator
* Language Detection

## OCR / Computer Vision

* EasyOCR
* OpenCV
* Pillow
* NumPy

## Speech

* Faster Whisper
* Edge TTS
* CTranslate2
* PyAV

## Maps & Location

* OpenStreetMap
* Overpass API
* Geoapify
* Browser Geolocation API
* Google Maps navigation links

## Authentication & Security

* bcrypt
* Passlib
* Python-JOSE
* Email Validator

---

# 📦 Requirements

The project dependencies are maintained in:

```text
requirements.txt
```

Major dependencies include:

```text
FastAPI
Uvicorn
Google GenAI
PyMongo
EasyOCR
OpenCV
Pillow
Deep Translator
Language Detection
Faster Whisper
Edge TTS
Geoapify-related HTTP services
Python-JOSE
Passlib
bcrypt
```

Install all dependencies with:

```bash
pip install -r requirements.txt
```

---

# ⚙️ Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/Puttaraj05/multilingual-tourist-assistant.git
cd multilingual-tourist-assistant
```

---

## 2. Create a Python Virtual Environment

### macOS / Linux

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Configuration

Create a `.env` file in the project root.

Use `.env.example` as the configuration template.

### `.env.example`

```env
# Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here

# MongoDB connection URI
MONGODB_URI=your_mongodb_connection_string_here

# MongoDB database name
DATABASE_NAME=multilingual_tourist_assistant

# Geoapify API key
GEOAPIFY_API_KEY=your_geoapify_api_key_here

# JWT authentication secret
JWT_SECRET_KEY=your_jwt_secret_key_here
```

### Environment Variables

| Variable           | Purpose                          |
| ------------------ | -------------------------------- |
| `GEMINI_API_KEY`   | Google Gemini API authentication |
| `MONGODB_URI`      | MongoDB connection URI           |
| `DATABASE_NAME`    | MongoDB database name            |
| `GEOAPIFY_API_KEY` | Geoapify API authentication      |
| `JWT_SECRET_KEY`   | JWT authentication secret        |

### ⚠️ Security

Never commit your real `.env` file to GitHub.

Your `.gitignore` should contain:

```gitignore
.env
venv/
__pycache__/
*.pyc
```

Never expose:

* Gemini API keys
* MongoDB credentials
* Geoapify API keys
* JWT secrets
* Other private credentials

Only commit `.env.example` with placeholder values.

---

# ▶️ Run the Application

Activate the virtual environment.

### macOS / Linux

```bash
source venv/bin/activate
```

Then start the FastAPI server:

```bash
uvicorn backend.main:app --reload --port 8000
```

The application will be available at:

```text
http://127.0.0.1:8000
```

---

# 📄 Application Pages

| Page               | Route                   |
| ------------------ | ----------------------- |
| 🏠 Home            | `/`                     |
| ℹ️ About           | `/about.html`           |
| 🔐 Authentication  | `/auth.html`            |
| 📊 Dashboard       | `/dashboard.html`       |
| 🤖 AI Chat         | `/chat.html`            |
| 🚨 Emergency       | `/emergency.html`       |
| ✨ Features         | `/features.html`        |
| 🧭 Itinerary       | `/itinerary.html`       |
| 🗺️ Planner        | `/planner.html`         |
| 📍 Recommendations | `/recommendations.html` |
| 🌐 Translator      | `/translation.html`     |

---

# 📚 API Documentation

FastAPI automatically provides interactive API documentation.

After starting the server:

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

### Health Check

```http
GET /api/health
```

Expected response:

```json
{
  "success": true,
  "message": "TravelMate API is running"
}
```

---

# 📍 Recommendation Flow

```text
Search City / Destination
          │
          ▼
Select Category
          │
          ▼
Select Radius
          │
          ▼
Recommendation API
          │
          ▼
Recommendation Service
          │
          ▼
Geoapify / Location Services
          │
          ▼
Format Places
          │
          ▼
Recommendation Cards
          │
          ▼
Google Maps Navigation
```

### Near Me Flow

```text
Browser Geolocation
        ↓
Latitude + Longitude
        ↓
Recommendation API
        ↓
Nearby Places
        ↓
TravelMate Results
```

---

# 🚨 Emergency Location Flow

```text
User Location
     ↓
Latitude / Longitude
     ↓
Emergency API
     ↓
OpenStreetMap / Overpass API
     ↓
Nearby Emergency Services
     ↓
Formatted Results
     ↓
TravelMate Emergency Page
```

This allows TravelMate to search OpenStreetMap data for relevant nearby real-world services.

---

# 🌐 Multilingual Interface Flow

```text
User Selects Language
          ↓
Global Language Selector
          ↓
i18n System
          ↓
Language Resource
          ↓
English / Hindi / Telugu
          ↓
Updated Interface
```

Language resources:

```text
frontend/js/i18n/en.js
frontend/js/i18n/hi.js
frontend/js/i18n/te.js
frontend/js/i18n/i18n.js
```

---

# 🧪 Testing

The backend APIs can be tested using:

* FastAPI Swagger UI
* ReDoc
* Postman
* Browser
* Frontend integration testing

Start the server:

```bash
uvicorn backend.main:app --reload --port 8000
```

Then open:

```text
http://127.0.0.1:8000/docs
```

---

# 🔒 Security Notes

Before deploying the project publicly:

* Never commit `.env`
* Never expose API keys
* Never expose MongoDB credentials
* Never expose `JWT_SECRET_KEY`
* Use secure production CORS settings
* Use HTTPS in production
* Use strong authentication secrets
* Restrict database access
* Rotate credentials if they are accidentally exposed

---

# 🚀 Future Scope

TravelMate can be extended with:

* 📱 Mobile application
* 🗣️ More advanced voice conversations
* 🌐 More Indian and international languages
* 🌦️ Real-time weather information
* 🚆 Public transportation information
* ✈️ Flight and hotel integration
* 💰 AI-powered travel budget planning
* 🧭 Advanced route optimization
* 🔔 Real-time travel alerts
* 📴 Offline translation
* 🤖 Multimodal AI travel assistance
* 📍 More advanced personalized recommendations
* 👥 Collaborative itinerary planning

---

# 🎯 Project Objective

The primary objective of **TravelMate** is to create a single intelligent travel companion that helps tourists with:

```text
Planning + Communication + Discovery + Navigation + Safety
```

Instead of depending on multiple applications, tourists can use TravelMate to access several essential travel services through one platform.

---

# 🌟 Why TravelMate?

Travelers often need multiple applications for:

* Translation
* Maps
* Travel planning
* Local recommendations
* Emergency information
* AI assistance
* Communication

TravelMate brings these capabilities together into one platform.

```text
                 TRAVELMATE
                     │
       ┌─────────────┼─────────────┐
       │             │             │
    PLAN          EXPLORE       COMMUNICATE
       │             │             │
   Itinerary     Places        Translation
   AI Planner    Maps          AI Chat
       │             │             │
       └─────────────┼─────────────┘
                     │
                  STAY SAFE
                     │
               Emergency Support
```

---

# 💻 Development

The project is structured to separate:

* Frontend presentation
* API routing
* Business logic
* External services
* Database operations
* Models
* Schemas
* Utilities

This modular architecture makes it easier to:

* Add new features
* Replace external services
* Maintain individual modules
* Test APIs independently
* Extend AI functionality
* Scale the backend

---

# 📁 Important Project Directories

```text
backend/api/          → FastAPI routes
backend/services/     → Application business logic
backend/database/     → MongoDB integration
backend/models/       → Database/application models
backend/schemas/      → Pydantic schemas
backend/prompts/      → AI prompts
backend/utils/        → Shared utilities
frontend/             → User interface
frontend/css/         → Stylesheets
frontend/js/          → Frontend logic
frontend/js/i18n/     → Multilingual resources
frontend/images/      → Project assets
```

---

# 🔗 Repository

**TravelMate — Multilingual Tourist Assistant**

GitHub Repository:

https://github.com/Puttaraj05/multilingual-tourist-assistant

---

# 👨‍💻 Project

**TravelMate — Multilingual Tourist Assistant**

Built using:

* Python
* FastAPI
* JavaScript
* Google Gemini
* MongoDB
* OpenStreetMap
* Overpass API
* Geoapify
* OCR technologies
* Speech technologies

---

# 📜 License

This project is developed for **educational, hackathon, and demonstration purposes**.

Add an appropriate open-source license if you intend to distribute the project under a specific license.

---

## 🌍 TravelMate

> **Plan. Translate. Explore. Navigate. Stay Safe.**

**One intelligent platform for a smarter travel experience.**
