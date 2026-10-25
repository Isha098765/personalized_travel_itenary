"""
Global configuration, curated destination datasets, and application constants.
"""

# Supported LLM Providers
LLM_PROVIDERS = {
    "demo": "Demo Mode (Offline AI Simulator - Instant & Reliable)",
    "gemini": "Google Gemini (gemini-1.5-flash / gemini-2.0-flash)",
    "groq": "Groq (llama-3.3-70b-versatile / fast inference)"
}

# Currency Conversion Constants (Base USD)
CURRENCY_RATES = {
    "USD": 1.0,
    "INR": 85.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 152.0,
    "AUD": 1.54,
    "AED": 3.67,
    "SGD": 1.34
}

# Standard Daily Time Slots
TIME_SLOTS = [
    {
        "id": "morning",
        "title": "Morning Sightseeing",
        "time": "09:00 - 12:30",
        "icon": "🌅",
        "type": "sightseeing"
    },
    {
        "id": "lunch",
        "title": "Lunch Recommendation",
        "time": "12:30 - 14:00",
        "icon": "🍜",
        "type": "dining"
    },
    {
        "id": "afternoon",
        "title": "Afternoon Leisure & Exploration",
        "time": "14:00 - 17:30",
        "icon": "🏛️",
        "type": "leisure"
    },
    {
        "id": "evening",
        "title": "Evening Dining & Entertainment",
        "time": "18:00 - 22:00",
        "icon": "🌆",
        "type": "evening"
    }
]

# Travel Vibe Options
VIBE_OPTIONS = [
    "Beach & Coastal Escapes 🏖️",
    "Mountains & Alpine Trails 🏔️",
    "Cultural & Heritage Wonder 🏛️",
    "Urban Skylines & Nightlife 🏙️",
    "Culinary & Street Food Haven 🍲",
    "Wellness, Yoga & Nature Retreat 🌿",
    "Thrilling Outdoor Adventure 🏄‍♂️",
    "Romantic & Cozy Getaways 🕯️"
]

# Budget Levels and Daily Benchmark per Person (USD)
BUDGET_TIERS = {
    "Budget": {"min": 35, "max": 75, "desc": "Hostels, street food, public transit, free walking tours"},
    "Moderate": {"min": 80, "max": 180, "desc": "3-star/boutique hotels, casual restaurants, rideshares, paid museums"},
    "Luxury": {"min": 200, "max": 650, "desc": "5-star resorts, fine dining, private tours, bespoke experiences"}
}

# Travel Party Types
PARTY_TYPES = [
    "Solo Traveler 🎒",
    "Couple / Romantic 💑",
    "Family with Kids 👨‍👩‍👧‍👦",
    "Group of Friends 👥",
    "Business + Leisure 💼"
]

# Travel Paces
PACE_LEVELS = [
    "Relaxed (1-2 major sights, lingering coffees & relaxation)",
    "Moderate (Balanced exploration with pleasant downtime)",
    "Fast-Paced (Maximizing every hour, energetic & packed)"
]

# Interests Tags
INTEREST_TAGS = [
    "Historical Landmarks",
    "Local Street Food",
    "Art Galleries & Museums",
    "Scenic Photography",
    "Outdoor Hiking & Trekking",
    "Nightclubs & Speakeasies",
    "Local Markets & Shopping",
    "Water Sports & Beaches",
    "Architecture & Design",
    "Peaceful Parks & Nature",
    "Hidden Speakeasies & Rooftops"
]

# Curated Destination Catalog (for Tab 1 recommendations, clustering centroids, and offline fallbacks)
CURATED_DESTINATIONS = [
    {
        "name": "Tokyo",
        "country": "Japan",
        "continent": "Asia",
        "lat": 35.6762,
        "lon": 139.6503,
        "vibes": ["Urban Skylines & Nightlife 🏙️", "Culinary & Street Food Haven 🍲", "Cultural & Heritage Wonder 🏛️"],
        "budget_tier": "Moderate",
        "avg_daily_usd": 120,
        "best_months": ["March", "April", "May", "October", "November"],
        "climate_season": "Spring / Autumn",
        "highlight_tags": ["Cherry Blossoms", "Michelin Dining", "Futuristic Tech", "Historic Shrines"],
        "emergency_contacts": {"police": "110", "ambulance": "119", "tourist": "+81-3-3201-3331", "general": "110"},
        "clusters": {
            "Day 1": {"name": "Shibuya & Shinjuku District", "lat": 35.6617, "lon": 139.7040},
            "Day 2": {"name": "Asakusa & Ueno Cultural Hub", "lat": 35.7119, "lon": 139.7967},
            "Day 3": {"name": "Ginza & Tsukiji Waterfront", "lat": 35.6655, "lon": 139.7708},
            "Day 4": {"name": "Roppongi & Tokyo Tower Vista", "lat": 35.6586, "lon": 139.7454}
        }
    },
    {
        "name": "Kyoto",
        "country": "Japan",
        "continent": "Asia",
        "lat": 35.0116,
        "lon": 135.7681,
        "vibes": ["Cultural & Heritage Wonder 🏛️", "Wellness, Yoga & Nature Retreat 🌿", "Romantic & Cozy Getaways 🕯️"],
        "budget_tier": "Moderate",
        "avg_daily_usd": 110,
        "best_months": ["March", "April", "October", "November"],
        "climate_season": "Spring / Autumn",
        "highlight_tags": ["Zen Gardens", "Geisha Districts", "Bamboo Groves", "Fushimi Inari"],
        "emergency_contacts": {"police": "110", "ambulance": "119", "tourist": "+81-75-343-0548", "general": "110"},
        "clusters": {
            "Day 1": {"name": "Higashiyama & Gion Historic Quarter", "lat": 34.9949, "lon": 135.7850},
            "Day 2": {"name": "Arashiyama Bamboo & River Valley", "lat": 35.0170, "lon": 135.6710},
            "Day 3": {"name": "Fushimi & South Shrine Trail", "lat": 34.9671, "lon": 135.7727}
        }
    },
    {
        "name": "Paris",
        "country": "France",
        "continent": "Europe",
        "lat": 48.8566,
        "lon": 2.3522,
        "vibes": ["Cultural & Heritage Wonder 🏛️", "Romantic & Cozy Getaways 🕯️", "Culinary & Street Food Haven 🍲"],
        "budget_tier": "Luxury",
        "avg_daily_usd": 180,
        "best_months": ["April", "May", "June", "September", "October"],
        "climate_season": "Spring / Early Autumn",
        "highlight_tags": ["Louvre & Orsay", "Seine Sunsets", "Patisseries & Wine", "Montmartre Bohemian"],
        "emergency_contacts": {"police": "17", "ambulance": "15", "tourist": "112", "general": "112"},
        "clusters": {
            "Day 1": {"name": "1st & 7th Arrondissement (Eiffel & Louvre)", "lat": 48.8584, "lon": 2.2945},
            "Day 2": {"name": "Montmartre & Pigalle Bohemian Hill", "lat": 48.8867, "lon": 2.3431},
            "Day 3": {"name": "Le Marais & Latin Quarter Historic Heart", "lat": 48.8575, "lon": 2.3590},
            "Day 4": {"name": "Canal Saint-Martin & Bastille Arts", "lat": 48.8683, "lon": 2.3653}
        }
    },
    {
        "name": "Rome",
        "country": "Italy",
        "continent": "Europe",
        "lat": 41.9028,
        "lon": 12.4964,
        "vibes": ["Cultural & Heritage Wonder 🏛️", "Culinary & Street Food Haven 🍲", "Romantic & Cozy Getaways 🕯️"],
        "budget_tier": "Moderate",
        "avg_daily_usd": 130,
        "best_months": ["April", "May", "September", "October"],
        "climate_season": "Spring / Autumn",
        "highlight_tags": ["Colosseum & Forum", "Vatican City", "Trastevere Diners", "Piazza Navona"],
        "emergency_contacts": {"police": "113", "ambulance": "118", "tourist": "060608", "general": "112"},
        "clusters": {
            "Day 1": {"name": "Ancient Rome & Colosseum Sector", "lat": 41.8902, "lon": 12.4922},
            "Day 2": {"name": "Vatican & Prati Riverside", "lat": 41.9029, "lon": 12.4534},
            "Day 3": {"name": "Trastevere & Historic Piazzas", "lat": 41.8894, "lon": 12.4705}
        }
    },
    {
        "name": "Bali",
        "country": "Indonesia",
        "continent": "Asia",
        "lat": -8.4095,
        "lon": 115.1889,
        "vibes": ["Beach & Coastal Escapes 🏖️", "Wellness, Yoga & Nature Retreat 🌿", "Thrilling Outdoor Adventure 🏄‍♂️"],
        "budget_tier": "Budget",
        "avg_daily_usd": 50,
        "best_months": ["April", "May", "June", "July", "August", "September"],
        "climate_season": "Dry Sunny Season",
        "highlight_tags": ["Ubud Rice Terraces", "Uluwatu Cliffs", "Beach Clubs", "Spiritual Temples"],
        "emergency_contacts": {"police": "110", "ambulance": "118", "tourist": "112", "general": "112"},
        "clusters": {
            "Day 1": {"name": "Ubud Rainforest & Artisan Heart", "lat": -8.5069, "lon": 115.2625},
            "Day 2": {"name": "Seminyak & Canggu Coastal Vibe", "lat": -8.6500, "lon": 115.1333},
            "Day 3": {"name": "Uluwatu Sunset & Southern Peninsula", "lat": -8.8291, "lon": 115.0849}
        }
    },
    {
        "name": "Barcelona",
        "country": "Spain",
        "continent": "Europe",
        "lat": 41.3879,
        "lon": 2.1699,
        "vibes": ["Urban Skylines & Nightlife 🏙️", "Beach & Coastal Escapes 🏖️", "Cultural & Heritage Wonder 🏛️"],
        "budget_tier": "Moderate",
        "avg_daily_usd": 125,
        "best_months": ["May", "June", "September", "October"],
        "climate_season": "Mediterranean Warm",
        "highlight_tags": ["Sagrada Familia", "Gothic Quarter Tapas", "Barceloneta Beach", "Park Guell"],
        "emergency_contacts": {"police": "091", "ambulance": "061", "tourist": "112", "general": "112"},
        "clusters": {
            "Day 1": {"name": "Gothic Quarter & El Born Tapas", "lat": 41.3833, "lon": 2.1764},
            "Day 2": {"name": "Eixample & Gaudi Masterpieces", "lat": 41.3916, "lon": 2.1648},
            "Day 3": {"name": "Barceloneta Beach & Port Olimpic", "lat": 41.3802, "lon": 2.1896}
        }
    },
    {
        "name": "Jaipur",
        "country": "India",
        "continent": "Asia",
        "lat": 26.9124,
        "lon": 75.7873,
        "vibes": ["Cultural & Heritage Wonder 🏛️", "Culinary & Street Food Haven 🍲", "Romantic & Cozy Getaways 🕯️"],
        "budget_tier": "Budget",
        "avg_daily_usd": 40,
        "best_months": ["October", "November", "December", "January", "February", "March"],
        "climate_season": "Pleasant Winter",
        "highlight_tags": ["Amber Fort", "Hawa Mahal", "Bazaar Street Food", "Royal Palaces"],
        "emergency_contacts": {"police": "100", "ambulance": "108", "tourist": "1363", "general": "112"},
        "clusters": {
            "Day 1": {"name": "Walled Pink City & City Palace", "lat": 26.9258, "lon": 75.8237},
            "Day 2": {"name": "Amer Fort & Jal Mahal Lakeside", "lat": 26.9855, "lon": 75.8513},
            "Day 3": {"name": "Nahargarh Sunset & C-Scheme Cafes", "lat": 26.9366, "lon": 75.8155}
        }
    },
    {
        "name": "Goa",
        "country": "India",
        "continent": "Asia",
        "lat": 15.2993,
        "lon": 74.1240,
        "vibes": ["Beach & Coastal Escapes 🏖️", "Urban Skylines & Nightlife 🏙️", "Culinary & Street Food Haven 🍲"],
        "budget_tier": "Budget",
        "avg_daily_usd": 45,
        "best_months": ["November", "December", "January", "February", "March"],
        "climate_season": "Tropical Coastal",
        "highlight_tags": ["Vagator Sunsets", "Seafood Shacks", "Portuguese Villas", "Water Sports"],
        "emergency_contacts": {"police": "100", "ambulance": "108", "tourist": "1363", "general": "112"},
        "clusters": {
            "Day 1": {"name": "North Coast (Anjuna & Vagator)", "lat": 15.5866, "lon": 73.7439},
            "Day 2": {"name": "Fontainhas Latin Quarter & Panaji", "lat": 15.4989, "lon": 73.8278},
            "Day 3": {"name": "South Goa Tranquil Beaches (Palolem)", "lat": 15.0100, "lon": 74.0232}
        }
    },
    {
        "name": "New York City",
        "country": "USA",
        "continent": "North America",
        "lat": 40.7128,
        "lon": -74.0060,
        "vibes": ["Urban Skylines & Nightlife 🏙️", "Culinary & Street Food Haven 🍲", "Cultural & Heritage Wonder 🏛️"],
        "budget_tier": "Luxury",
        "avg_daily_usd": 240,
        "best_months": ["April", "May", "September", "October", "December"],
        "climate_season": "Spring / Fall / Festive Winter",
        "highlight_tags": ["Broadway Shows", "Central Park", "Skyline Observatories", "Diverse Dining"],
        "emergency_contacts": {"police": "911", "ambulance": "911", "tourist": "311", "general": "911"},
        "clusters": {
            "Day 1": {"name": "Midtown & Broadway Heart", "lat": 40.7580, "lon": -73.9855},
            "Day 2": {"name": "Lower Manhattan & Brooklyn Bridge", "lat": 40.7127, "lon": -74.0059},
            "Day 3": {"name": "Greenwich Village & Chelsea High Line", "lat": 40.7336, "lon": -74.0027},
            "Day 4": {"name": "Central Park & Museum Mile", "lat": 40.7829, "lon": -73.9654}
        }
    },
    {
        "name": "Dubai",
        "country": "United Arab Emirates",
        "continent": "Middle East",
        "lat": 25.2048,
        "lon": 55.2708,
        "vibes": ["Urban Skylines & Nightlife 🏙️", "Beach & Coastal Escapes 🏖️", "Thrilling Outdoor Adventure 🏄‍♂️"],
        "budget_tier": "Luxury",
        "avg_daily_usd": 210,
        "best_months": ["November", "December", "January", "February", "March"],
        "climate_season": "Mild Desert Winter",
        "highlight_tags": ["Burj Khalifa", "Desert Safari Dunes", "Dubai Marina Yachts", "Luxury Shopping"],
        "emergency_contacts": {"police": "999", "ambulance": "998", "tourist": "8004888", "general": "999"},
        "clusters": {
            "Day 1": {"name": "Downtown Dubai & Burj Khalifa", "lat": 25.1972, "lon": 55.2744},
            "Day 2": {"name": "Dubai Marina & Palm Jumeirah", "lat": 25.0805, "lon": 55.1403},
            "Day 3": {"name": "Old Dubai Deira & Gold Souk", "lat": 25.2667, "lon": 55.3000}
        }
    },
    {
        "name": "Reykjavik",
        "country": "Iceland",
        "continent": "Europe",
        "lat": 64.1466,
        "lon": -21.9426,
        "vibes": ["Mountains & Alpine Trails 🏔️", "Thrilling Outdoor Adventure 🏄‍♂️", "Wellness, Yoga & Nature Retreat 🌿"],
        "budget_tier": "Luxury",
        "avg_daily_usd": 220,
        "best_months": ["June", "July", "August", "September", "October"],
        "climate_season": "Midnight Sun / Northern Lights",
        "highlight_tags": ["Blue Lagoon Geothermal", "Golden Circle Geysers", "Glacier Waterfalls", "Aurora Borealis"],
        "emergency_contacts": {"police": "112", "ambulance": "112", "tourist": "112", "general": "112"},
        "clusters": {
            "Day 1": {"name": "Old Harbour & Downtown Reykjavik", "lat": 64.1500, "lon": -21.9400},
            "Day 2": {"name": "Golden Circle Geothermal Valley", "lat": 64.3104, "lon": -20.3024},
            "Day 3": {"name": "Reykjanes Peninsula & Blue Lagoon", "lat": 63.8804, "lon": -22.4495}
        }
    },
    {
        "name": "Cape Town",
        "country": "South Africa",
        "continent": "Africa",
        "lat": -33.9249,
        "lon": 18.4241,
        "vibes": ["Beach & Coastal Escapes 🏖️", "Mountains & Alpine Trails 🏔️", "Culinary & Street Food Haven 🍲"],
        "budget_tier": "Moderate",
        "avg_daily_usd": 95,
        "best_months": ["November", "December", "January", "February", "March", "April"],
        "climate_season": "Sunny Southern Summer",
        "highlight_tags": ["Table Mountain Cableway", "Cape Point Penguins", "V&A Waterfront", "Stellenbosch Wineries"],
        "emergency_contacts": {"police": "10111", "ambulance": "10177", "tourist": "+27-21-487-6800", "general": "112"},
        "clusters": {
            "Day 1": {"name": "Table Mountain & City Bowl", "lat": -33.9573, "lon": 18.4031},
            "Day 2": {"name": "Camps Bay & Atlantic Seaboard", "lat": -33.9500, "lon": 18.3780},
            "Day 3": {"name": "Cape Peninsula & Boulders Beach", "lat": -34.1970, "lon": 18.4510}
        }
    },
    {
        "name": "Zurich & Interlaken",
        "country": "Switzerland",
        "continent": "Europe",
        "lat": 47.3769,
        "lon": 8.5417,
        "vibes": ["Mountains & Alpine Trails 🏔️", "Romantic & Cozy Getaways 🕯️", "Wellness, Yoga & Nature Retreat 🌿"],
        "budget_tier": "Luxury",
        "avg_daily_usd": 250,
        "best_months": ["June", "July", "August", "December", "January", "February"],
        "climate_season": "Alpine Summer / Ski Winter",
        "highlight_tags": ["Jungfraujoch Top of Europe", "Lake Thun & Brienz", "Swiss Chocolatiers", "Scenic Alpine Trains"],
        "emergency_contacts": {"police": "117", "ambulance": "144", "tourist": "112", "general": "112"},
        "clusters": {
            "Day 1": {"name": "Zurich Altstadt & Lake Promenade", "lat": 47.3700, "lon": 8.5430},
            "Day 2": {"name": "Interlaken Lakes & Harder Kulm", "lat": 46.6863, "lon": 7.8632},
            "Day 3": {"name": "Lauterbrunnen Valley & Grindelwald", "lat": 46.5935, "lon": 7.9090}
        }
    },
    {
        "name": "Amalfi Coast",
        "country": "Italy",
        "continent": "Europe",
        "lat": 40.6340,
        "lon": 14.6027,
        "vibes": ["Romantic & Cozy Getaways 🕯️", "Beach & Coastal Escapes 🏖️", "Culinary & Street Food Haven 🍲"],
        "budget_tier": "Luxury",
        "avg_daily_usd": 230,
        "best_months": ["May", "June", "September", "October"],
        "climate_season": "Mediterranean Sunshine",
        "highlight_tags": ["Positano Cliffside", "Limoncello Tasting", "Path of the Gods", "Capri Island Ferries"],
        "emergency_contacts": {"police": "113", "ambulance": "118", "tourist": "112", "general": "112"},
        "clusters": {
            "Day 1": {"name": "Positano Village & Spiaggia Grande", "lat": 40.6281, "lon": 14.4850},
            "Day 2": {"name": "Amalfi Town & Ravello Gardens", "lat": 40.6340, "lon": 14.6027},
            "Day 3": {"name": "Capri Island & Blue Grotto", "lat": 40.5507, "lon": 14.2426}
        }
    },
    {
        "name": "Manali & Solang",
        "country": "India",
        "continent": "Asia",
        "lat": 32.2396,
        "lon": 77.1887,
        "vibes": ["Mountains & Alpine Trails 🏔️", "Thrilling Outdoor Adventure 🏄‍♂️", "Wellness, Yoga & Nature Retreat 🌿"],
        "budget_tier": "Budget",
        "avg_daily_usd": 38,
        "best_months": ["April", "May", "June", "October", "December", "January"],
        "climate_season": "Himalayan Snow / Crisp Summers",
        "highlight_tags": ["Solang Valley Paragliding", "Rohtang Pass Snow", "Old Manali Cafes", "Cedar Pine Treks"],
        "emergency_contacts": {"police": "100", "ambulance": "108", "tourist": "1363", "general": "112"},
        "clusters": {
            "Day 1": {"name": "Old Manali & Hadimba Forest Sanctuary", "lat": 32.2483, "lon": 77.1805},
            "Day 2": {"name": "Solang Adventure Valley & Atal Tunnel", "lat": 32.3167, "lon": 77.1572},
            "Day 3": {"name": "Jogini Waterfalls & Vashisht Hot Springs", "lat": 32.2662, "lon": 77.1989}
        }
    }
]
