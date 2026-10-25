"""
Simulated database persistence service using SQLite and JSON for offline portability.
Provides persistent storage, retrieval, deletion, and JSON export/import of trips.
"""

import os
import sqlite3
import json
import logging
from typing import List, Optional
from models.schemas import TripRecord, TripPreferences, DayItinerary, ActivitySlot

logger = logging.getLogger(__name__)

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "trips.db")


def init_db():
    """Initializes the SQLite database schema if not present."""
    os.makedirs(DB_DIR, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                id TEXT PRIMARY KEY,
                trip_name TEXT NOT NULL,
                destination TEXT NOT NULL,
                duration_days INTEGER NOT NULL,
                start_date TEXT,
                end_date TEXT,
                budget_level TEXT,
                travel_party TEXT,
                total_cost_usd REAL,
                total_cost_inr REAL,
                created_at TEXT,
                trip_data_json TEXT NOT NULL
            )
        """)
        conn.commit()


def save_trip(trip: TripRecord) -> bool:
    """Saves or updates a trip record in SQLite."""
    try:
        init_db()
        payload = json.dumps(trip.to_dict())
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO trips (
                    id, trip_name, destination, duration_days, start_date, end_date,
                    budget_level, travel_party, total_cost_usd, total_cost_inr,
                    created_at, trip_data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trip.id,
                trip.trip_name,
                trip.destination,
                trip.duration_days,
                trip.start_date,
                trip.end_date,
                trip.preferences.budget_level,
                trip.preferences.travel_party,
                trip.total_cost_usd,
                trip.total_cost_inr,
                trip.created_at,
                payload
            ))
            conn.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to save trip to SQLite: {e}")
        return False


def get_all_trips() -> List[TripRecord]:
    """Retrieves all saved trips from SQLite ordered by creation time descending."""
    try:
        init_db()
        trips = []
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT trip_data_json FROM trips ORDER BY created_at DESC
            """)
            rows = cursor.fetchall()
            for row in rows:
                try:
                    data = json.loads(row[0])
                    trips.append(TripRecord.from_dict(data))
                except Exception as inner_e:
                    logger.warning(f"Error parsing trip row: {inner_e}")
        return trips
    except Exception as e:
        logger.error(f"Failed to read trips from SQLite: {e}")
        return []


def get_trip_by_id(trip_id: str) -> Optional[TripRecord]:
    """Retrieves a single trip record by ID."""
    try:
        init_db()
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT trip_data_json FROM trips WHERE id = ?", (trip_id,))
            row = cursor.fetchone()
            if row:
                return TripRecord.from_dict(json.loads(row[0]))
        return None
    except Exception as e:
        logger.error(f"Failed to get trip by ID: {e}")
        return None


def delete_trip(trip_id: str) -> bool:
    """Deletes a trip record by ID."""
    try:
        init_db()
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
            conn.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to delete trip: {e}")
        return False


def export_trip_json(trip: TripRecord) -> str:
    """Serializes a trip into formatted JSON string for export."""
    return json.dumps(trip.to_dict(), indent=2)


def import_trip_json(json_content: str) -> TripRecord:
    """Parses JSON content into a TripRecord."""
    data = json.loads(json_content)
    trip = TripRecord.from_dict(data)
    save_trip(trip)
    return trip
