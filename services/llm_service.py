"""
LLM Integration Service with support for Google Gemini, Groq, and Demo Mode.
Features prompt engineering, JSON schema enforcement, and robust offline mock engines.
"""

import json
import logging
import re
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from models.schemas import (
    TripPreferences, DayItinerary, ActivitySlot, DestinationRecommendation
)
from services.clustering_service import optimize_day_geographic_routing
from config.settings import CURATED_DESTINATIONS, CURRENCY_RATES

logger = logging.getLogger(__name__)


class LLMService:
    @staticmethod
    def _extract_json_from_text(text: str) -> Optional[Any]:
        """Robustly extracts JSON from raw LLM output even if surrounded by markdown or commentary."""
        if not text:
            return None
        text = text.strip()
        # Direct parse attempt
        try:
            return json.loads(text)
        except Exception:
            pass

        # Try markdown block ```json ... ```
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except Exception:
                pass

        # Try finding outermost { ... } or [ ... ]
        first_bracket = min(
            [i for i in [text.find("{"), text.find("[")] if i != -1],
            default=-1
        )
        last_bracket = max(
            [i for i in [text.rfind("}"), text.rfind("]")] if i != -1],
            default=-1
        )
        if first_bracket != -1 and last_bracket != -1 and last_bracket > first_bracket:
            sub = text[first_bracket:last_bracket + 1]
            try:
                return json.loads(sub)
            except Exception:
                pass
        return None

    @classmethod
    def call_gemini(cls, prompt: str, api_key: str, model: str = "gemini-1.5-flash") -> str:
        """Calls Google Gemini v1beta REST API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 3000,
                "responseMimeType": "application/json"
            }
        }
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini API Error ({resp.status_code}): {resp.text}")
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini returned no candidates.")
        return candidates[0]["content"]["parts"][0]["text"]

    @classmethod
    def call_groq(cls, prompt: str, api_key: str, model: str = "llama-3.3-70b-versatile") -> str:
        """Calls Groq OpenAI-compatible REST API."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are an expert AI Travel Planner. You MUST return strictly valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4,
            "response_format": {"type": "json_object"}
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"Groq API Error ({resp.status_code}): {resp.text}")
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    # -------------------------------------------------------------
    # HIGH-FIDELITY OFFLINE DEMO ENGINE
    # -------------------------------------------------------------
    @classmethod
    def _generate_mock_itinerary(cls, prefs: TripPreferences) -> List[DayItinerary]:
        """Produces ultra-realistic, geographically clustered travel plans with authentic details."""
        dest_name = prefs.destination.strip() if prefs.destination else "Tokyo"
        
        # Look for curated match
        matched_dest = None
        for d in CURATED_DESTINATIONS:
            if d["name"].lower() in dest_name.lower() or dest_name.lower() in d["name"].lower():
                matched_dest = d
                break

        if not matched_dest:
            # Fallback to first curated or synthesize realistic template
            matched_dest = CURATED_DESTINATIONS[0]

        base_lat = matched_dest["lat"]
        base_lon = matched_dest["lon"]
        clusters = list(matched_dest.get("clusters", {}).values())

        # Scale costs based on budget level
        multiplier = 1.0
        if prefs.budget_level == "Budget":
            multiplier = 0.55
        elif prefs.budget_level == "Luxury":
            multiplier = 2.2

        days: List[DayItinerary] = []
        try:
            start_dt = datetime.strptime(prefs.start_date, "%Y-%m-%d")
        except Exception:
            start_dt = datetime.now()

        # Destination-specific rich activity catalog templates
        city_templates = {
            "Tokyo": [
                {
                    "theme": "Neon Alleyways & Shinto Heritage",
                    "zone": "Shibuya & Harajuku",
                    "c_lat": 35.6617, "c_lon": 139.7040,
                    "morning": ("Meiji Jingu Shrine & Forest Walk", "Stroll through tranquil 170-acre evergreen forest to Tokyo's iconic imperial shrine.", "Yoyogi Park, Shibuya", 35.6764, 139.6993, 0.0, "Free entry. Wear walking shoes."),
                    "lunch": ("Afuri Ramen Harajuku", "Taste refreshing yuzu-salt ramen with crispy bamboo and delicate broth (vegan options available).", "Harajuku, Shibuya", 35.6705, 139.7045, 14.0, "Use ticket vending machine to order."),
                    "afternoon": ("Takeshita Street & Shibuya Sky", "Explore quirky pop culture boutiques, then head up Shibuya Sky for 360-degree panorama.", "Shibuya Crossing", 35.6598, 139.7024, 22.0, "Pre-book Shibuya Sky ticket for 16:30 sunset."),
                    "evening": ("Omoide Yokocho Izakaya Tour", "Experience lantern-lit alleyway dining with yakitori skewers and draft craft beer.", "Shinjuku West Exit", 35.6931, 139.6997, 35.0, "Small cozy stalls with only 6-8 seats.")
                },
                {
                    "theme": "Old Edo Traditions & Riverfront",
                    "zone": "Asakusa & Ueno",
                    "c_lat": 35.7119, "c_lon": 139.7967,
                    "morning": ("Sensō-ji Temple & Nakamise Souvenirs", "Wander through the massive Thunder Gate into Tokyo's oldest Buddhist temple.", "Asakusa, Taito", 35.7148, 139.7967, 5.0, "Sample fresh ningyo-yaki sweet cakes."),
                    "lunch": ("Daikokuya Tempura (Est. 1887)", "Historic eatery famed for black sauce tendon with jumbo tiger prawns.", "Asakusa 1-38-10", 35.7126, 139.7958, 20.0, "Traditional tatami mat seating."),
                    "afternoon": ("Tokyo National Museum & Ueno Park", "Marvel at samurai armor, ukiyo-e woodblock prints, and serene lotus ponds.", "Ueno Park, Taito", 35.7189, 139.7765, 12.0, "Audio guide available in English."),
                    "evening": ("Tokyo Skytree Sunset & Solamachi", "Ascend 450 meters above ground and enjoy modern fusion dining overlooking city lights.", "Sumida City", 35.7100, 139.8107, 45.0, "Reserve glass floor observatory pass.")
                },
                {
                    "theme": "Culinary Marvels & Glamour",
                    "zone": "Tsukiji Outer Market & Ginza",
                    "c_lat": 35.6655, "c_lon": 139.7708,
                    "morning": ("Tsukiji Outer Market Street Food Tasting", "Savor tamagoyaki omelet, fresh sea urchin, wagyu skewers, and matcha gelato.", "Tsukiji, Chuo", 35.6655, 139.7708, 25.0, "Cash preferred at traditional street stalls."),
                    "lunch": ("Ginza Kagari Michelin Bib Gourmand", "Velvety chicken paitan broth ramen with seasonal artisanal vegetables.", "Ginza 6-4-12", 35.6710, 139.7635, 18.0, "Line moves quickly; worth the wait."),
                    "afternoon": ("TeamLab Planets Digital Art Immersion", "Wade through water and walk among infinite kaleidoscopic crystal rooms.", "Toyosu, Koto", 35.6515, 139.7892, 32.0, "Short pants provided for water exhibits."),
                    "evening": ("Bar High Five & Rooftop Ginza Cocktails", "Experience legendary Japanese mixology with hand-carved ice diamonds.", "Ginza, Chuo", 35.6698, 139.7621, 50.0, "Smart casual dress code.")
                }
            ],
            "Paris": [
                {
                    "theme": "Iconic Monuments & Royal Gardens",
                    "zone": "7th & 1st Arrondissement",
                    "c_lat": 48.8584, "c_lon": 2.2945,
                    "morning": ("Eiffel Tower & Champ de Mars Stroll", "Ascend to the 2nd floor summit for panoramic views of the Seine River.", "Champ de Mars, 7th", 48.8584, 2.2945, 30.0, "Book morning lift slot to avoid midday crowds."),
                    "lunch": ("Café de Flore or Les Antiquaires", "Classic Parisian bistrot with croque monsieur and duck confit.", "Rue du Bac, 7th", 48.8550, 2.3270, 28.0, "Outdoor wicker terrace seating recommended."),
                    "afternoon": ("Musée d'Orsay Impressionist Masterpieces", "Admiration of Monet, Van Gogh, and Degas housed inside a grand Belle Époque railway station.", "1 Rue de la Légion d'Honneur", 48.8599, 2.3265, 18.0, "Skip-the-line digital ticket included."),
                    "evening": ("Seine River Sunset Cruise with Champagne", "Glide past illuminated bridges and Notre-Dame as the golden hour turns to twilight.", "Pont de l'Alma", 48.8638, 2.3021, 40.0, "Wrap a light scarf for river breeze.")
                },
                {
                    "theme": "Bohemian Artistry & Hilltop Views",
                    "zone": "Montmartre & Pigalle",
                    "c_lat": 48.8867, "c_lon": 2.3431,
                    "morning": ("Sacré-Cœur Basilica & Place du Tertre", "Discover artists painting portraits on cobblestone lanes overlooking Paris.", "Montmartre Hill", 48.8867, 2.3431, 0.0, "Free entrance to the basilica dome grounds."),
                    "lunch": ("Le Consulat Traditional Bistro", "Tuck into beef bourguignon or French onion soup at Picasso's former haunt.", "Rue Norvins, 18th", 48.8861, 2.3395, 24.0, "Quaint vintage photography exterior."),
                    "afternoon": ("Musée de Montmartre & Renoir Gardens", "Stroll through the secluded vineyard gardens where Auguste Renoir painted masterpieces.", "12 Rue Cortot", 48.8879, 2.3406, 15.0, "Serene hidden gem away from crowds."),
                    "evening": ("Moulin Rouge Historic Cabaret or Wine Cave", "Sample biodynamic French wines paired with artisanal cheese board in a subterranean cave.", "Rue des Abbesses", 48.8845, 2.3370, 45.0, "Casual romantic vibes.")
                }
            ],
            "Bali": [
                {
                    "theme": "Emerald Rice Terraces & Sacred Temples",
                    "zone": "Ubud Cultural Highlands",
                    "c_lat": -8.5069, "c_lon": 115.2625,
                    "morning": ("Tegallalang Rice Terraces & Jungle Swing", "Wander through stepped green terraces and capture iconic canopy photographs.", "Tegallalang, Ubud", -8.4338, 115.2798, 10.0, "Arrive by 8:30 AM before tourist buses."),
                    "lunch": ("Warung Babi Guling Ibu Oka", "Legendary Balinese spiced roast pork platter with crispy crackling and sambal.", "Jl. Suweta No.2, Ubud", -8.5055, 115.2628, 8.0, "Authentic local flavors."),
                    "afternoon": ("Sacred Monkey Forest Sanctuary", "Meander through moss-covered Hindu temples guarded by hundreds of Balinese macaques.", "Jl. Monkey Forest, Ubud", -8.5188, 115.2588, 7.0, "Keep sunglasses and phones secured."),
                    "evening": ("Ubud Palace Legong Dance & Organic Dinner", "Witness rhythmic Gamelan percussion followed by candlelit farm-to-table dining.", "Ubud Central", -8.5069, 115.2625, 20.0, "Performance starts promptly at 19:30.")
                },
                {
                    "theme": "Clifftop Horizons & Sunset Waves",
                    "zone": "Uluwatu & Bukit Peninsula",
                    "c_lat": -8.8291, "c_lon": 115.0849,
                    "morning": ("Padang Padang Beach Surf & Relax", "Walk through a cliff cave opening to a world-famous golden sand surf cove.", "Pecatu, Uluwatu", -8.8111, 115.1037, 3.0, "Great for swimming and surf lessons."),
                    "lunch": ("Single Fin Clifftop Eatery", "Smoothie bowls, gourmet burgers, and chilled fresh young coconut with ocean panorama.", "Pantai Suluban", -8.8149, 115.0884, 15.0, "Prime clifftop viewing deck."),
                    "afternoon": ("Uluwatu Clifftop Temple Walk", "Spectacular temple perched 70 meters above roaring Indian Ocean waves.", "Pecatu, Uluwatu", -8.8291, 115.0849, 6.0, "Traditional sarong provided at entry."),
                    "evening": ("Kecak Fire Dance & Jimbaran Seafood Dinner", "Hypnotic choir chanting against burning crimson sunset, followed by beachside grilled snapper.", "Jimbaran Bay", -8.7758, 115.1666, 30.0, "Dine with toes in the sand.")
                }
            ]
        }

        # Select matching city template or create dynamic generic template
        templates = city_templates.get(matched_dest["name"])
        if not templates:
            # Create dynamic template for Jaipur, Rome, New York, etc.
            templates = [
                {
                    "theme": f"Historic Heart & Cultural Landmarks of {dest_name}",
                    "zone": "Heritage District",
                    "c_lat": base_lat, "c_lon": base_lon,
                    "morning": (f"{dest_name} Heritage Citadel & Old Quarter", f"Discover the iconic history and monumental architecture of {dest_name}.", f"Central {dest_name}", base_lat + 0.005, base_lon + 0.003, 15.0, "Hire a certified local heritage guide."),
                    "lunch": (f"Local Flavors & Signature Bistro", f"Authentic regional delicacies matching {prefs.dietary} preferences.", f"Old Town Market", base_lat + 0.002, base_lon + 0.001, 18.0, "Ask for chef's daily special."),
                    "afternoon": (f"{dest_name} City Museum & Artisan Quarter", f"Immerse in local folklore, master craftsmanship, and scenic viewpoints.", f"Arts District", base_lat - 0.003, base_lon - 0.002, 12.0, "Great photography spots."),
                    "evening": (f"Sunset Promenade & Twilight Dining", f"Breathtaking skyline views followed by fine local dining and live music.", f"Riverside / Plaza", base_lat - 0.004, base_lon + 0.002, 35.0, "Reserve window or outdoor table.")
                },
                {
                    "theme": f"Hidden Gems & Local Neighborhoods in {dest_name}",
                    "zone": "Uptown & Gardens",
                    "c_lat": base_lat + 0.012, "c_lon": base_lon + 0.015,
                    "morning": (f"Botanical Gardens & Royal Pavilion", f"Peaceful morning stroll through lush historic gardens and pavilions.", f"North {dest_name}", base_lat + 0.015, base_lon + 0.012, 10.0, "Peaceful before 10 AM."),
                    "lunch": (f"Artisan Cafe & Bakery", f"Fresh seasonal salads, baked bread, and specialty single-origin coffees.", f"Garden District", base_lat + 0.013, base_lon + 0.014, 15.0, "Indoor & outdoor seating."),
                    "afternoon": (f"Boutique Shopping & Modern Art Space", f"Explore independent designers, craft markets, and contemporary installations.", f"Design Corridor", base_lat + 0.010, base_lon + 0.018, 14.0, "Pick up authentic local crafts."),
                    "evening": (f"Rooftop Panorama & Evening Entertainment", f"Watch {dest_name} light up at dusk with crafted beverages and culinary pairings.", f"Central Viewpoint", base_lat + 0.008, base_lon + 0.015, 40.0, "Sunset dress code recommended.")
                }
            ]

        # Generate each requested day
        for d_idx in range(prefs.duration_days):
            day_num = d_idx + 1
            curr_date = (start_dt + timedelta(days=d_idx)).strftime("%A, %b %d")
            tmpl = templates[d_idx % len(templates)]
            
            # Slightly offset coordinates for higher days to avoid identical markers
            lat_jitter = (d_idx // len(templates)) * 0.008
            lon_jitter = (d_idx // len(templates)) * 0.009

            m_title, m_desc, m_loc, m_lat, m_lon, m_cost, m_tip = tmpl["morning"]
            l_title, l_desc, l_loc, l_lat, l_lon, l_cost, l_tip = tmpl["lunch"]
            a_title, a_desc, a_loc, a_lat, a_lon, a_cost, a_tip = tmpl["afternoon"]
            e_title, e_desc, e_loc, e_lat, e_lon, e_cost, e_tip = tmpl["evening"]

            slots = [
                ActivitySlot(
                    slot_id="morning",
                    slot_title="Morning Sightseeing",
                    time_window="09:00 - 12:30",
                    title=f"{m_title} (Day {day_num})" if d_idx >= len(templates) else m_title,
                    description=m_desc,
                    location_name=m_loc,
                    latitude=round(m_lat + lat_jitter, 5),
                    longitude=round(m_lon + lon_jitter, 5),
                    zone=tmpl["zone"],
                    category="Sightseeing",
                    estimated_cost_usd=round(m_cost * multiplier, 1),
                    estimated_cost_inr=round(m_cost * multiplier * CURRENCY_RATES["INR"], 1),
                    tips=m_tip,
                    tags=["Heritage", "Sightseeing", "Scenic"]
                ),
                ActivitySlot(
                    slot_id="lunch",
                    slot_title="Lunch Recommendation",
                    time_window="12:30 - 14:00",
                    title=l_title,
                    description=f"{l_desc} (Catered to: {prefs.dietary})",
                    location_name=l_loc,
                    latitude=round(l_lat + lat_jitter, 5),
                    longitude=round(l_lon + lon_jitter, 5),
                    zone=tmpl["zone"],
                    category="Dining",
                    estimated_cost_usd=round(l_cost * multiplier, 1),
                    estimated_cost_inr=round(l_cost * multiplier * CURRENCY_RATES["INR"], 1),
                    tips=l_tip,
                    tags=["Foodie", "Local Cuisine", prefs.dietary]
                ),
                ActivitySlot(
                    slot_id="afternoon",
                    slot_title="Afternoon Leisure & Exploration",
                    time_window="14:00 - 17:30",
                    title=a_title,
                    description=a_desc,
                    location_name=a_loc,
                    latitude=round(a_lat + lat_jitter, 5),
                    longitude=round(a_lon + lon_jitter, 5),
                    zone=tmpl["zone"],
                    category="Leisure",
                    estimated_cost_usd=round(a_cost * multiplier, 1),
                    estimated_cost_inr=round(a_cost * multiplier * CURRENCY_RATES["INR"], 1),
                    tips=a_tip,
                    tags=["Culture", "Walkable", "Photography"]
                ),
                ActivitySlot(
                    slot_id="evening",
                    slot_title="Evening Dining & Entertainment",
                    time_window="18:00 - 22:00",
                    title=e_title,
                    description=e_desc,
                    location_name=e_loc,
                    latitude=round(e_lat + lat_jitter, 5),
                    longitude=round(e_lon + lon_jitter, 5),
                    zone=tmpl["zone"],
                    category="Nightlife & Dining",
                    estimated_cost_usd=round(e_cost * multiplier, 1),
                    estimated_cost_inr=round(e_cost * multiplier * CURRENCY_RATES["INR"], 1),
                    tips=e_tip,
                    tags=["Nightlife", "Scenic Dining", "Atmosphere"]
                )
            ]

            day_plan = DayItinerary(
                day_number=day_num,
                date_str=curr_date,
                theme=f"{tmpl['theme']}" + (f" - Phase {d_idx // len(templates) + 1}" if d_idx >= len(templates) else ""),
                zone_cluster=tmpl["zone"],
                slots=slots
            )
            day_plan = optimize_day_geographic_routing(day_plan)
            day_plan.recalculate_totals(CURRENCY_RATES["INR"])
            days.append(day_plan)

        return days

    # -------------------------------------------------------------
    # MAIN PUBLIC METHODS
    # -------------------------------------------------------------
    @classmethod
    def generate_itinerary(
        cls,
        preferences: TripPreferences,
        provider: str = "demo",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> List[DayItinerary]:
        """
        Generates day-by-day itinerary plans.
        Uses live LLM (Gemini or Groq) if key is provided; otherwise seamlessly uses Demo Mode.
        """
        if provider == "demo" or not api_key:
            return cls._generate_mock_itinerary(preferences)

        prompt = f"""
        You are a World-Class Travel Architect. Generate a {preferences.duration_days}-day itinerary for {preferences.destination}.
        Start Date: {preferences.start_date}
        End Date: {preferences.end_date}
        Budget Level: {preferences.budget_level}
        Travel Party: {preferences.travel_party}
        Pace: {preferences.pace}
        Interests: {', '.join(preferences.interests)}
        Dietary Preference: {preferences.dietary}
        Open Vibe: {preferences.open_vibe or 'None'}

        CRITICAL REQUIREMENT - GEOGRAPHIC CLUSTERING:
        Group activities for each day within the SAME neighborhood/district to eliminate transit backtracking.
        Ensure lunch is walking distance to morning sight.
        Provide realistic latitude and longitude coordinates for each location.

        Return ONLY a JSON object matching this schema:
        {{
            "days": [
                {{
                    "day_number": 1,
                    "date_str": "Day 1 (e.g. Monday, Nov 12)",
                    "theme": "Theme title",
                    "zone_cluster": "Neighborhood Name",
                    "slots": [
                        {{
                            "slot_id": "morning",
                            "slot_title": "Morning Sightseeing",
                            "time_window": "09:00 - 12:30",
                            "title": "Specific attraction name",
                            "description": "Engaging 2-sentence description",
                            "location_name": "Full address or landmark name",
                            "latitude": 35.6762,
                            "longitude": 139.6503,
                            "zone": "Neighborhood Name",
                            "category": "Sightseeing",
                            "estimated_cost_usd": 25.0,
                            "tips": "Practical tip for the user",
                            "tags": ["Tag1", "Tag2"]
                        }},
                        {{
                            "slot_id": "lunch",
                            "slot_title": "Lunch Recommendation",
                            "time_window": "12:30 - 14:00",
                            "title": "Specific restaurant name",
                            "description": "Signature dishes matching dietary restriction",
                            "location_name": "Location",
                            "latitude": 35.6762,
                            "longitude": 139.6503,
                            "zone": "Neighborhood Name",
                            "category": "Dining",
                            "estimated_cost_usd": 18.0,
                            "tips": "Reservation advice",
                            "tags": ["Food", "Local"]
                        }},
                        {{
                            "slot_id": "afternoon",
                            "slot_title": "Afternoon Leisure & Exploration",
                            "time_window": "14:00 - 17:30",
                            "title": "Museum or scenic spot",
                            "description": "Description",
                            "location_name": "Location",
                            "latitude": 35.6762,
                            "longitude": 139.6503,
                            "zone": "Neighborhood Name",
                            "category": "Leisure",
                            "estimated_cost_usd": 15.0,
                            "tips": "Tips",
                            "tags": ["Culture"]
                        }},
                        {{
                            "slot_id": "evening",
                            "slot_title": "Evening Dining & Entertainment",
                            "time_window": "18:00 - 22:00",
                            "title": "Sunset rooftop or dinner venue",
                            "description": "Description",
                            "location_name": "Location",
                            "latitude": 35.6762,
                            "longitude": 139.6503,
                            "zone": "Neighborhood Name",
                            "category": "Nightlife & Dining",
                            "estimated_cost_usd": 35.0,
                            "tips": "Dress code advice",
                            "tags": ["Nightlife", "Dinner"]
                        }}
                    ]
                }}
            ]
        }}
        """

        raw_response = ""
        try:
            if provider == "gemini":
                raw_response = cls.call_gemini(prompt, api_key, model or "gemini-1.5-flash")
            elif provider == "groq":
                raw_response = cls.call_groq(prompt, api_key, model or "llama-3.3-70b-versatile")
            
            parsed = cls._extract_json_from_text(raw_response)
            if not parsed or "days" not in parsed:
                raise ValueError("Parsed JSON did not contain 'days' key.")

            days: List[DayItinerary] = []
            for d in parsed["days"]:
                # Ensure each slot has inr calculated
                for s in d.get("slots", []):
                    cost_usd = float(s.get("estimated_cost_usd", 20.0))
                    s["estimated_cost_inr"] = round(cost_usd * CURRENCY_RATES["INR"], 1)
                
                day_obj = DayItinerary.from_dict(d)
                day_obj = optimize_day_geographic_routing(day_obj)
                day_obj.recalculate_totals(CURRENCY_RATES["INR"])
                days.append(day_obj)

            return days

        except Exception as e:
            logger.warning(f"Live LLM generation failed ({e}). Falling back to Demo Mode engine.")
            # Graceful fallback to rich mock engine
            mock_days = cls._generate_mock_itinerary(preferences)
            return mock_days

    @classmethod
    def swap_single_slot(
        cls,
        target_slot: ActivitySlot,
        day_context: DayItinerary,
        swap_intent: str,
        preferences: TripPreferences,
        provider: str = "demo",
        api_key: Optional[str] = None
    ) -> ActivitySlot:
        """
        Dynamically swaps an individual activity slot based on user intent.
        Keeps slot geographically coherent with the current day's zone cluster.
        """
        if provider != "demo" and api_key:
            prompt = f"""
            The user wants to replace an activity in their {preferences.destination} itinerary.
            Current Zone: {day_context.zone_cluster}
            Target Time Slot: {target_slot.slot_title} ({target_slot.time_window})
            Current Activity to Replace: {target_slot.title} ({target_slot.category})
            User's Swap Intent: "{swap_intent}"
            Budget Level: {preferences.budget_level}
            Dietary Restriction: {preferences.dietary}

            Provide a new matching activity in the SAME or immediate neighboring zone ({day_context.zone_cluster})
            with realistic latitude (~{target_slot.latitude}) and longitude (~{target_slot.longitude}).

            Return ONLY a JSON object matching this schema:
            {{
                "title": "New activity name",
                "description": "Engaging 2-sentence description",
                "location_name": "Landmark or venue name",
                "latitude": {target_slot.latitude + 0.002},
                "longitude": {target_slot.longitude + 0.002},
                "category": "{target_slot.category}",
                "estimated_cost_usd": 25.0,
                "tips": "Helpful tip for visitor",
                "tags": ["Tag1", "Tag2"]
            }}
            """
            try:
                if provider == "gemini":
                    raw = cls.call_gemini(prompt, api_key)
                else:
                    raw = cls.call_groq(prompt, api_key)
                
                data = cls._extract_json_from_text(raw)
                if data and "title" in data:
                    cost_usd = float(data.get("estimated_cost_usd", target_slot.estimated_cost_usd))
                    return ActivitySlot(
                        slot_id=target_slot.slot_id,
                        slot_title=target_slot.slot_title,
                        time_window=target_slot.time_window,
                        title=data["title"],
                        description=data.get("description", "A refreshed local recommendation."),
                        location_name=data.get("location_name", target_slot.location_name),
                        latitude=float(data.get("latitude", target_slot.latitude)),
                        longitude=float(data.get("longitude", target_slot.longitude)),
                        zone=day_context.zone_cluster,
                        category=data.get("category", target_slot.category),
                        estimated_cost_usd=cost_usd,
                        estimated_cost_inr=round(cost_usd * CURRENCY_RATES["INR"], 1),
                        tips=data.get("tips", "Enjoy your refreshed activity!"),
                        tags=data.get("tags", ["Customized", "Refreshed"])
                    )
            except Exception as e:
                logger.warning(f"Live swap failed: {e}. Using intelligent algorithmic swap.")

        # Algorithmic swap fallback
        intent_lower = swap_intent.lower()
        new_title = target_slot.title
        new_desc = target_slot.description
        new_category = target_slot.category
        new_cost = target_slot.estimated_cost_usd
        new_tags = list(target_slot.tags)

        if "vegetarian" in intent_lower or "vegan" in intent_lower:
            new_title = f"Green Oasis Organic Plant-Based Bistro ({day_context.zone_cluster})"
            new_desc = "Farm-fresh vegetarian bowls, woodfired sourdough flatbreads, and cold-pressed botanical juices."
            new_category = "Dining"
            new_tags = ["Vegetarian", "Healthy", "Plant-based"]
        elif "market" in intent_lower or "shopping" in intent_lower:
            new_title = f"{day_context.zone_cluster} Artisanal Craft & Flea Market"
            new_desc = "Bustling local open-air bazaar featuring handcrafted souvenirs, vintage finds, and live buskers."
            new_category = "Leisure"
            new_cost = max(5.0, new_cost * 0.7)
            new_tags = ["Market", "Local Crafts", "Bargains"]
        elif "rain" in intent_lower or "indoor" in intent_lower or "museum" in intent_lower:
            new_title = f"{day_context.zone_cluster} Heritage Fine Arts & Indoor Pavilion"
            new_desc = "Sheltered cultural haven showcasing historical treasures, interactive exhibits, and a cozy atrium cafe."
            new_category = "Culture"
            new_tags = ["Indoor", "Rainy Day", "Museum"]
        elif "adventure" in intent_lower or "outdoor" in intent_lower:
            new_title = f"{day_context.zone_cluster} Urban Adventure & Cycle Trail"
            new_desc = "High-energy guided bike or e-scooter tour traversing hidden viewpoints and panoramic coastal/skyline trails."
            new_category = "Adventure"
            new_cost = new_cost * 1.3
            new_tags = ["Active", "Adventure", "Outdoors"]
        elif "budget" in intent_lower or "free" in intent_lower:
            new_title = f"{day_context.zone_cluster} Scenic Public Garden & Panorama Vista"
            new_desc = "Zero-cost admission tranquil public gardens with manicured flora, sculpture paths, and city vistas."
            new_category = "Sightseeing"
            new_cost = 0.0
            new_tags = ["Free", "Budget-Friendly", "Nature"]
        else:
            new_title = f"Bespoke {target_slot.slot_title.split()[0]} Experience: {swap_intent.capitalize()}"
            new_desc = f"Tailored activity aligning with '{swap_intent}', curated inside the {day_context.zone_cluster} quarter."
            new_tags.append("Customized")

        return ActivitySlot(
            slot_id=target_slot.slot_id,
            slot_title=target_slot.slot_title,
            time_window=target_slot.time_window,
            title=new_title,
            description=new_desc,
            location_name=f"{day_context.zone_cluster} District",
            latitude=target_slot.latitude + 0.0015,
            longitude=target_slot.longitude + 0.0015,
            zone=day_context.zone_cluster,
            category=new_category,
            estimated_cost_usd=round(new_cost, 1),
            estimated_cost_inr=round(new_cost * CURRENCY_RATES["INR"], 1),
            tips="Updated per your custom vibe preferences.",
            tags=new_tags
        )
