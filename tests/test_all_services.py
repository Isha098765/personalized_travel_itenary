"""
Automated unit and integration test suite for the Travel Itinerary Planner.
Verifies schemas, clustering, LLM mock engine, recommendations, SQLite storage, and PDF output.
"""

import os
import sys
import uuid
import unittest
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import (
    TripPreferences, ActivitySlot, DayItinerary, TripRecord, DestinationRecommendation
)
from services.clustering_service import (
    haversine_distance_km, estimate_transit_info, optimize_day_geographic_routing,
    score_clustering_efficiency
)
from services.llm_service import LLMService
from services.recommender_service import RecommenderService
from services.storage_service import (
    init_db, save_trip, get_all_trips, get_trip_by_id, delete_trip,
    export_trip_json, import_trip_json
)
from services.pdf_service import generate_itinerary_pdf


class TestTravelPlanner(unittest.TestCase):
    def setUp(self):
        init_db()
        self.prefs = TripPreferences(
            destination="Tokyo",
            duration_days=3,
            start_date=str(date.today()),
            end_date=str(date.today() + timedelta(days=2)),
            budget_level="Moderate",
            travel_party="Solo Traveler 🎒",
            pace="Moderate",
            interests=["Historical Landmarks", "Local Street Food"],
            dietary="Vegetarian"
        )

    def test_clustering_haversine(self):
        """Verify Haversine distance calculation and transit logic."""
        # Tokyo Station to Shibuya Crossing is ~6.5 km
        dist = haversine_distance_km(35.6812, 139.7671, 35.6598, 139.7024)
        self.assertGreater(dist, 5.0)
        self.assertLess(dist, 8.5)

        # Walking distance ~ 0.5 km
        short_desc, mins = estimate_transit_info(0.5)
        self.assertIn("stroll", short_desc)
        self.assertLessEqual(mins, 15)

    def test_llm_demo_generation(self):
        """Verify Demo Mode creates structured day itineraries with sequential slots."""
        days = LLMService.generate_itinerary(self.prefs, provider="demo")
        self.assertEqual(len(days), 3)
        for day in days:
            self.assertEqual(len(day.slots), 4)
            slot_ids = [s.slot_id for s in day.slots]
            self.assertEqual(slot_ids, ["morning", "lunch", "afternoon", "evening"])
            self.assertGreater(day.daily_cost_usd, 0)
            self.assertGreater(day.daily_cost_inr, 0)

    def test_slot_swap(self):
        """Verify dynamic slot swapping updates activity without wiping other slots."""
        days = LLMService.generate_itinerary(self.prefs, provider="demo")
        day1 = days[0]
        orig_slot = day1.slots[1]  # Lunch slot
        
        swapped = LLMService.swap_single_slot(
            target_slot=orig_slot,
            day_context=day1,
            swap_intent="Find a pure vegan cafe with organic smoothie bowls",
            preferences=self.prefs,
            provider="demo"
        )
        self.assertEqual(swapped.slot_id, "lunch")
        self.assertIn("Vegetarian", swapped.tags)
        self.assertNotEqual(swapped.title, orig_slot.title)

    def test_destination_recommender(self):
        """Verify Tab 1 destination recommender returns top 3 matching cities."""
        recs = RecommenderService.recommend_destinations(
            vibe_preference="Beach & Coastal Escapes 🏖️",
            budget_level="Budget",
            travel_party="Group of Friends 👥",
            travel_month="December"
        )
        self.assertEqual(len(recs), 3)
        for r in recs:
            self.assertIsInstance(r, DestinationRecommendation)
            self.assertGreaterEqual(r.vibe_match_score, 60)
            self.assertGreater(len(r.highlight_tags), 0)

    def test_sqlite_persistence_and_export(self):
        """Verify saving, loading, deleting trips and JSON export/import."""
        days = LLMService.generate_itinerary(self.prefs, provider="demo")
        test_id = f"test_{uuid.uuid4().hex[:6]}"
        trip = TripRecord(
            id=test_id,
            trip_name="Automated Test Trip",
            destination="Paris",
            duration_days=3,
            start_date=self.prefs.start_date,
            end_date=self.prefs.end_date,
            preferences=self.prefs,
            days=days
        )
        trip.recalculate_totals()
        
        # Save
        saved = save_trip(trip)
        self.assertTrue(saved)

        # Retrieve
        fetched = get_trip_by_id(test_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.destination, "Paris")
        self.assertEqual(len(fetched.days), 3)

        # JSON Export / Import
        json_str = export_trip_json(fetched)
        imported = import_trip_json(json_str)
        self.assertEqual(imported.id, test_id)

        # Delete
        deleted = delete_trip(test_id)
        self.assertTrue(deleted)
        self.assertIsNone(get_trip_by_id(test_id))

    def test_pdf_generation(self):
        """Verify ReportLab PDF generation builds a valid PDF binary."""
        days = LLMService.generate_itinerary(self.prefs, provider="demo")
        trip = TripRecord(
            id="pdf_test",
            trip_name="PDF Validation Expedition",
            destination="Tokyo",
            duration_days=3,
            start_date=self.prefs.start_date,
            end_date=self.prefs.end_date,
            preferences=self.prefs,
            days=days
        )
        trip.recalculate_totals()
        pdf_bytes = generate_itinerary_pdf(trip)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 2000)
        # PDF files begin with %PDF
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
