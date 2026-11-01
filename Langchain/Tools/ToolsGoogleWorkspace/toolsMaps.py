"""
Tools Google Maps Module

Integrates Google Maps Platform Web Services via the official `googlemaps` Python client.
Provides geocoding, directions, distance matrix, and place search capabilities.
"""

import os
from typing import List, Any, Optional
from langchain.tools import tool
import googlemaps
from Log.log_utils import PrintFunctionName

# Retrieve Google Maps API key from environment or default config
MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

@PrintFunctionName
def ToolsList() -> List[Any]:
    """
    Initialize and return custom LangChain tools for Google Maps services:
    - get_geocode
    - get_directions
    - calculate_distance_matrix
    - search_places
    """
    if not MAPS_API_KEY:
        print("[WARNING] GOOGLE_MAPS_API_KEY environment variable is not set. Google Maps tools require a valid API key.")

    client = googlemaps.Client(key=MAPS_API_KEY) if MAPS_API_KEY else None

    @tool
    def get_geocode(address: str) -> str:
        """Convert a human-readable address or location name into geographic coordinates (latitude and longitude)."""
        if not client:
            return "[ERROR] Google Maps client not initialized. Missing GOOGLE_MAPS_API_KEY."
        try:
            results = client.geocode(address)
            if not results:
                return f"No location found for address: {address}"
            loc = results[0]['geometry']['location']
            formatted = results[0]['formatted_address']
            return f"Address: {formatted}\nLatitude: {loc['lat']}, Longitude: {loc['lng']}"
        except Exception as e:
            return f"[ERROR] Geocoding failed: {str(e)}"

    @tool
    def get_directions(origin: str, destination: str, mode: str = "driving") -> str:
        """Get travel directions and route duration between an origin and destination. Mode can be driving, walking, bicycling, or transit."""
        if not client:
            return "[ERROR] Google Maps client not initialized. Missing GOOGLE_MAPS_API_KEY."
        try:
            directions = client.directions(origin, destination, mode=mode)
            if not directions:
                return f"No route found from {origin} to {destination} using mode '{mode}'."
            leg = directions[0]['legs'][0]
            summary = directions[0].get('summary', '')
            return (
                f"Route Summary: {summary}\n"
                f"Origin: {leg['start_address']}\n"
                f"Destination: {leg['end_address']}\n"
                f"Distance: {leg['distance']['text']}\n"
                f"Duration: {leg['duration']['text']}"
            )
        except Exception as e:
            return f"[ERROR] Directions retrieval failed: {str(e)}"

    @tool
    def calculate_distance_matrix(origins: str, destinations: str, mode: str = "driving") -> str:
        """Calculate travel distance and time duration between multiple origins and destinations."""
        if not client:
            return "[ERROR] Google Maps client not initialized. Missing GOOGLE_MAPS_API_KEY."
        try:
            matrix = client.distance_matrix(origins=[origins], destinations=[destinations], mode=mode)
            element = matrix['rows'][0]['elements'][0]
            if element['status'] != 'OK':
                return f"Could not calculate distance matrix: {element['status']}"
            return (
                f"Distance between {origins} and {destinations}:\n"
                f"Distance: {element['distance']['text']}\n"
                f"Duration: {element['duration']['text']}"
            )
        except Exception as e:
            return f"[ERROR] Distance Matrix calculation failed: {str(e)}"

    @tool
    def search_places(query: str, location: Optional[str] = None, radius: int = 5000) -> str:
        """Search for places of interest, restaurants, or landmarks matching a query near a location or radius (in meters)."""
        if not client:
            return "[ERROR] Google Maps client not initialized. Missing GOOGLE_MAPS_API_KEY."
        try:
            loc_coords = None
            if location:
                geo_res = client.geocode(location)
                if geo_res:
                    loc_coords = geo_res[0]['geometry']['location']

            places = client.places(query=query, location=loc_coords, radius=radius if loc_coords else None)
            results = places.get('results', [])
            if not results:
                return f"No places found matching '{query}'."
            
            output = [f"Places found for '{query}':"]
            for p in results[:5]:  # Top 5 results
                name = p.get('name')
                addr = p.get('formatted_address', p.get('vicinity', 'N/A'))
                rating = p.get('rating', 'N/A')
                output.append(f"• {name} | Address: {addr} | Rating: {rating}")
            return "\n".join(output)
        except Exception as e:
            return f"[ERROR] Places search failed: {str(e)}"

    return [get_geocode, get_directions, calculate_distance_matrix, search_places]
