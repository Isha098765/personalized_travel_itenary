# Personalized Travel Itinerary Planner ✈️🌴
**Skill Wallet Capstone Project 4 — Production-Ready Travel SaaS Application**

A full-stack, AI-powered travel itinerary planner built with Streamlit, Python, ReportLab, and modern wanderlust design aesthetics. The platform eliminates transit backtracking through intelligent geographic clustering, enables dynamic slot swapping, provides simulated database persistence without external dependencies, and exports publication-grade offline PDF travel guides.

---

## 🌟 Key Features & Epic Modules

### 1. Configuration & User Preferences (Epic 3)
- **Multi-Engine AI Integration**:
  - **Demo Mode (Default)**: Instant, zero-friction simulation with authentic curated data, real coordinates, local bistros, and realistic prices.
  - **Google Gemini**: Direct REST calls (`gemini-1.5-flash`, `gemini-2.0-flash`, `gemini-1.5-pro`) with JSON output enforcement.
  - **Groq Cloud Inference**: Blazing-fast inference via `llama-3.3-70b-versatile` or `llama-3.1-8b-instant`.
  - Secure credential handling (keys are stored purely in memory for the active session).
- **Comprehensive Trip Intake Form**:
  - Fixed destination selection or open-ended mood/vibe exploration (Beach, Mountains, Culture, Urban, Foodie, Adventure, Wellness).
  - Duration picker (1 to 7+ days) with automatic date range alignment.
  - 3-tier budget model (Budget, Moderate, Luxury) with daily cost projections.
  - Travel party options (Solo, Couple, Family with Kids, Friends, Business).
  - Pacing preferences (Relaxed, Moderate, Fast-Paced).
  - Dietary customization (Vegetarian, Vegan, Halal, Gluten-Free, Jain).

### 2. Tab 1: Smart Destination Recommender (Epic 3)
- Recommends top 3 matching world cities for undecided travelers.
- Multi-factor algorithmic scoring factoring in budget tier, party dynamics, mood/vibe, and optimal weather season for travel dates.
- Visual cards displaying:
  - Compatibility percentage badge (`96% Match`)
  - Curated highlight tags (e.g. `UNESCO Heritage`, `Michelin Dining`)
  - Estimated daily expenses in USD and INR
  - Optimal travel seasons and must-visit landmarks
  - **1-Click "Plan Trip" Button**: Instantly populates the planner and shifts to Tab 2.

### 3. Tab 2: Day-by-Day Optimized Itinerary Generator (Epic 4)
- Structured daily schedules divided into 4 sequential time slots:
  1. **Morning Sightseeing** (09:00 - 12:30)
  2. **Lunch Recommendation** (12:30 - 14:00) with dietary-aware signature dishes
  3. **Afternoon Leisure & Exploration** (14:00 - 17:30)
  4. **Evening Dining & Entertainment** (18:00 - 22:00)
- **Geographic Clustering Logic**:
  - Calculates great-circle Haversine distances between successive stops.
  - Groups activities by neighborhood cluster to eliminate zigzagging across town.
  - Transit chips detailing transit mode, estimated minutes, and distance.
- **Interactive Geospatial & Financial Analytics**:
  - Pydeck 3D scatter map visualizing activity coordinates per day.
  - Altair daily spending progression bar charts and categorical spend breakdowns (Dining, Sightseeing, Leisure, Nightlife).
  - Dual currency tracking in USD and INR with live budget health status.

### 4. Tab 3: Vibe Customization & Dynamic Slot Swap (Epic 4)
- Modify specific activity slots without re-generating the entire itinerary.
- Quick 1-click preset prompt buttons:
  - 🥗 *Switch to Vegetarian / Vegan Spot*
  - 🌧️ *Rainy Day Indoor Cultural Pavilion*
  - 💰 *Budget-Friendly / Free Public Sights*
  - ⚡ *High-Energy Adventure & Outdoor Trails*
- **Single-Day Regeneration**: Refresh an entire day's theme and cluster while keeping all other days preserved.

### 5. Tab 4: Trip Management & Offline PDF Export (Epic 5)
- **Zero-Cloud Local SQLite Persistence**:
  - Save multiple trips locally in `data/trips.db`.
  - Saved Trips gallery with 1-click load, delete, and JSON export/import.
- **Publication-Ready Offline PDF Travel Guide**:
  - Generated on-the-fly using `ReportLab` into a downloadable `.pdf`.
  - Includes styled header banner, summary matrix, day-by-day itinerary tables, inter-slot transit directions, emergency numbers (police, medical, tourist helpline), and essential travel packing checklists.

---

## 🏛️ Project Architecture

```
personalized_travel/
├── app.py                      # Main Streamlit SaaS application
├── requirements.txt            # Python dependencies
├── README.md                   # Architecture & documentation
├── config/
│   ├── __init__.py
│   └── settings.py             # Curated destinations, exchange rates, time slots
├── models/
│   ├── __init__.py
│   └── schemas.py              # TripPreferences, ActivitySlot, DayItinerary, TripRecord
├── services/
│   ├── __init__.py
│   ├── clustering_service.py   # Haversine distance, sequencing, transit estimation
│   ├── llm_service.py          # Gemini & Groq REST APIs + Offline Demo engine
│   ├── recommender_service.py  # Seasonal & vibe compatibility destination scoring
│   ├── pdf_service.py          # ReportLab PDF travel guide compiler
│   └── storage_service.py      # SQLite repository + JSON portability
├── assets/
│   └── styles.css              # Wanderlust teal & sapphire UI design system
├── tests/
│   ├── __init__.py
│   └── test_all_services.py    # Unit & integration test suite
└── data/
    └── trips.db                # Auto-initialized local SQLite database
```

---

## 🚀 Quickstart & Local Setup

### 1. Clone & Navigate
```bash
git clone <repo-url>
cd personalized_travel
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
python tests/test_all_services.py
```

### 4. Launch the Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## ☁️ 1-Click Streamlit Community Cloud Deployment

1. Push this repository to GitHub.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Select your repository and set `Main file path` to `app.py`.
4. Deploy! The app runs immediately in **Demo Mode** with zero database setup. Users can optionally input their personal Google Gemini or Groq API keys in the sidebar.
