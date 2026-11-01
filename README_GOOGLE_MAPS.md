# 🗺️ Google Maps Integration Guide

This document provides instructions on how to set up, configure, and operate the **Google Maps Toolkit** (`toolsMaps`) within the RPI Personal Assistant project.

---

## 📂 Architecture & Location
- **Maps Module:** `Langchain/Tools/ToolsGoogleWorkspace/toolsMaps.py`
- **Tool Manager Registration:** `Langchain/Tools/toolsManager.py` (`toolsMaps`)
- **Dependencies Config:** `Langchain/Tools/ToolsGoogleWorkspace/requirements.txt`

---

## 🚀 Step 1: Install Dependencies
Ensure `googlemaps` is installed in your environment:
```powershell
pip install -r Langchain/Tools/ToolsGoogleWorkspace/requirements.txt
```

---

## 🔑 Step 2: Configure API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the following APIs for your project:
   - **Geocoding API**
   - **Directions API**
   - **Distance Matrix API**
   - **Places API**
3. Create an **API Key** under **APIs & Services** > **Credentials**.
4. Set the API key in your environment variables or `.env` file:
   ```env
   GOOGLE_MAPS_API_KEY=your_actual_google_maps_api_key_here
   ```

---

## 📋 Available Tools
The assistant is now equipped with 4 Google Maps tools:
1. **`get_geocode`**: Converts addresses or place names into geographic coordinates (latitude and longitude).
2. **`get_directions`**: Gets turn-by-turn routing and travel duration between origin and destination (`driving`, `walking`, `bicycling`, or `transit`).
3. **`calculate_distance_matrix`**: Computes travel distance and time duration between multiple points.
4. **`search_places`**: Searches for points of interest, restaurants, or landmarks near a location or radius.
