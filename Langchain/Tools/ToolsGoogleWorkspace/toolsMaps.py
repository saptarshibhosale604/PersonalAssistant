"""
Tools Google Maps Module (Fully Modernized: Routes API & Places API New)

Integrates Google Maps Platform Web Services via modernized endpoints:
- Geocoding API
- Routes API (Compute Routes) for get_directions & calculate_distance_matrix
- Places API (New) (Text Search) for search_places
"""

import os
import requests
from typing import List, Any, Optional
from langchain.tools import tool
import googlemaps
from Log.log_utils import PrintFunctionName

MAPS_API_KEY = (
    os.getenv("GOOGLE_MAPS_API_KEY")
    or os.getenv("GOMAPS_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
    or ""
)

@PrintFunctionName
def ToolsList() -> List[Any]:
    """
    Initialize and return custom LangChain tools for Google Maps using modernized API endpoints:
    - get_geocode
    - get_directions (Routes API v2)
    - calculate_distance_matrix (Routes API v2 distance calculation)
    - search_places (Places API New)
    """
    if not MAPS_API_KEY:
        print("[WARNING] GOOGLE_MAPS_API_KEY environment variable is not set.")

    client = googlemaps.Client(key=MAPS_API_KEY) if MAPS_API_KEY else None

    def _handle_error(e: Exception, api_name: str) -> str:
        err_msg = str(e)
        if "REQUEST_DENIED" in err_msg or "LegacyApiNotActivatedMapError" in err_msg:
            return (
                f"[ERROR] {api_name} Access Denied. "
                f"Please enable the Routes API and Places API in your Google Cloud Console project. Details: {err_msg}"
            )
        return f"[ERROR] {api_name} failed: {err_msg}"

    @tool
    def get_geocode(address: str) -> str:
        """Convert a human-readable address or location name into geographic coordinates (latitude and longitude)."""
        if not client:
            return "[ERROR] Google Maps client not initialized. Missing API key."
        try:
            results = client.geocode(address)
            if not results:
                return f"No location found for address: {address}"
            loc = results[0]['geometry']['location']
            formatted = results[0]['formatted_address']
            return f"Address: {formatted}\nLatitude: {loc['lat']}, Longitude: {loc['lng']}"
        except Exception as e:
            return _handle_error(e, "Geocoding API")

    @tool
    def get_directions(origin: str, destination: str, mode: str = "driving") -> str:
        """Get travel directions and route duration between an origin and destination using the Routes API."""
        if not MAPS_API_KEY:
            return "[ERROR] API key not configured."
        
        try:
            url = "https://routes.googleapis.com/directions/v2:computeRoutes"
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": MAPS_API_KEY,
                "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.legs"
            }
            
            travel_mode_map = {
                "driving": "DRIVE",
                "walking": "WALK",
                "bicycling": "BICYCLE",
                "transit": "TRANSIT"
            }
            t_mode = travel_mode_map.get(mode.lower(), "DRIVE")
            
            payload = {
                "origin": {"address": origin},
                "destination": {"address": destination},
                "travelMode": t_mode,
                "routingPreference": "TRAFFIC_UNAWARE"
            }
            
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            data = resp.json()
            
            if resp.status_code == 200 and "routes" in data and data["routes"]:
                route = data["routes"][0]
                distance_meters = route.get("distanceMeters", 0)
                duration_str = route.get("duration", "N/A")
                return (
                    f"Route (via Routes API):\n"
                    f"Origin: {origin}\n"
                    f"Destination: {destination}\n"
                    f"Distance: {distance_meters / 1000:.2f} km ({distance_meters} meters)\n"
                    f"Duration: {duration_str}"
                )
            else:
                error_info = data.get("error", {}).get("message", resp.text)
                return f"[ERROR] Routes API returned error: {error_info}"
        except Exception as e:
            return _handle_error(e, "Routes API")

    @tool
    def calculate_distance_matrix(origins: str, destinations: str, mode: str = "driving") -> str:
        """Calculate travel distance and time duration between origins and destinations using the Routes API."""
        if not MAPS_API_KEY:
            return "[ERROR] API key not configured."
            
        try:
            # Using Routes API v2 computeRoutes for distance & duration calculation
            url = "https://routes.googleapis.com/directions/v2:computeRoutes"
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": MAPS_API_KEY,
                "X-Goog-FieldMask": "routes.distanceMeters,routes.duration"
            }
            
            travel_mode_map = {
                "driving": "DRIVE",
                "walking": "WALK",
                "bicycling": "BICYCLE",
                "transit": "TRANSIT"
            }
            t_mode = travel_mode_map.get(mode.lower(), "DRIVE")
            
            payload = {
                "origin": {"address": origins},
                "destination": {"address": destinations},
                "travelMode": t_mode,
                "routingPreference": "TRAFFIC_UNAWARE"
            }
            
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            data = resp.json()
            
            if resp.status_code == 200 and "routes" in data and data["routes"]:
                route = data["routes"][0]
                distance_meters = route.get("distanceMeters", 0)
                duration_str = route.get("duration", "N/A")
                return (
                    f"Distance Calculation (via Routes API):\n"
                    f"From: {origins} -> To: {destinations} (Mode: {mode})\n"
                    f"Distance: {distance_meters / 1000:.2f} km ({distance_meters} meters)\n"
                    f"Duration: {duration_str}"
                )
            else:
                error_info = data.get("error", {}).get("message", resp.text)
                return f"[ERROR] Routes API Distance Calculation returned error: {error_info}"
        except Exception as e:
            return _handle_error(e, "Routes API (Distance Calculation)")

    @tool
    def search_places(query: str, location: Optional[str] = None, radius: int = 5000) -> str:
        """Search for places of interest, restaurants, or landmarks matching a query using Places API (New) Text Search."""
        if not MAPS_API_KEY:
            return "[ERROR] API key not configured."
            
        try:
            url = "https://places.googleapis.com/v1/places:searchText"
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": MAPS_API_KEY,
                "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating"
            }
            
            payload = {
                "textQuery": query
            }
            
            if location and client:
                geo = client.geocode(location)
                if geo:
                    loc = geo[0]['geometry']['location']
                    payload["locationBias"] = {
                        "circle": {
                            "center": {"latitude": loc['lat'], "longitude": loc['lng']},
                            "radius": float(radius)
                        }
                    }
                    
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            data = resp.json()
            
            if resp.status_code == 200 and "places" in data:
                places_list = data["places"]
                if not places_list:
                    return f"No places found matching '{query}'."
                output = [f"Places Search Results (Places API New) for '{query}':"]
                for p in places_list[:5]:
                    name = p.get("displayName", {}).get("text", "Unknown")
                    addr = p.get("formattedAddress", "N/A")
                    rating = p.get("rating", "N/A")
                    output.append(f"• {name} | Address: {addr} | Rating: {rating}")
                return "\n".join(output)
            else:
                error_info = data.get("error", {}).get("message", resp.text)
                return f"[ERROR] Places API New returned error: {error_info}"
        except Exception as e:
            return _handle_error(e, "Places API (New)")

    return [get_geocode, get_directions, calculate_distance_matrix, search_places]
