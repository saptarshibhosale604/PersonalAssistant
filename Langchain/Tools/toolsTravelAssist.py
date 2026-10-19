from typing import Annotated, List, Any
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from Log.log_utils import PrintFunctionName

_ddg_search = DuckDuckGoSearchRun()

@tool("search_flight_options", description="Search the web for flight options, airline schedules, estimated airfares, and direct/connecting flight details between origin and destination.")
def SearchFlightOptions(
    origin: Annotated[str, "Departure city or airport code"],
    destination: Annotated[str, "Arrival city or airport code"],
    date: Annotated[str, "Departure date (YYYY-MM-DD or descriptive)"]
) -> str:
    """Search for flight options and airfares."""
    try:
        query = f"flights from {origin} to {destination} on {date} price schedule"
        return _ddg_search.run(query)
    except Exception as e:
        return f"Error searching flight options: {str(e)}"

@tool("search_hotel_options", description="Search the web for hotel options, accommodations, reviews, and nightly rates in a specific destination.")
def SearchHotelOptions(
    destination: Annotated[str, "City or location for hotel stay"],
    check_in_date: Annotated[str, "Check-in date (YYYY-MM-DD)"],
    check_out_date: Annotated[str, "Check-out date (YYYY-MM-DD)"],
    preferences: Annotated[str, "Optional preferences like budget, luxury, pet-friendly, pool"] = "standard"
) -> str:
    """Search for hotel options and accommodations."""
    try:
        query = f"best hotels in {destination} {preferences} price {check_in_date} to {check_out_date}"
        return _ddg_search.run(query)
    except Exception as e:
        return f"Error searching hotel options: {str(e)}"

@tool("plan_route_and_transport", description="Plan travel routes, local transportation, transit options (trains, buses, subways, driving routes), and travel times between locations.")
def PlanRouteAndTransport(
    start_location: Annotated[str, "Starting point or transit station/airport"],
    end_location: Annotated[str, "Destination point or hotel/attraction"],
    mode: Annotated[str, "Preferred transit mode (e.g., public transit, walking, driving, taxi)"] = "public transit"
) -> str:
    """Plan route and local transportation."""
    try:
        query = f"how to get from {start_location} to {end_location} by {mode} travel time route"
        return _ddg_search.run(query)
    except Exception as e:
        return f"Error planning route: {str(e)}"

@tool("calculate_trip_budget", description="Calculate estimated total trip cost based on days, hotel cost per night, daily food/travel expenses, and flight cost.")
def CalculateTripBudget(
    days: Annotated[int, "Number of days for the trip"],
    hotel_cost_per_night: Annotated[float, "Average hotel cost per night"],
    daily_expense: Annotated[float, "Estimated daily food and local travel expense"],
    flight_cost: Annotated[float, "Estimated round-trip flight cost"]
) -> str:
    """Calculate estimated total trip budget."""
    try:
        total_hotel = days * hotel_cost_per_night
        total_daily = days * daily_expense
        grand_total = total_hotel + total_daily + flight_cost
        
        breakdown = (
            f"--- Trip Budget Breakdown ({days} Days) ---\n"
            f"Flight Cost: ${flight_cost:.2f}\n"
            f"Hotel Cost ({days} nights @ ${hotel_cost_per_night}/night): ${total_hotel:.2f}\n"
            f"Daily Expenses (${daily_expense}/day): ${total_daily:.2f}\n"
            f"====================================\n"
            f"Estimated Total Budget: ${grand_total:.2f}"
        )
        return breakdown
    except Exception as e:
        return f"Error calculating budget: {str(e)}"

@tool("generate_packing_list", description="Generate a recommended packing list based on destination climate, trip duration, and trip type (e.g. business, adventure, beach).")
def GeneratePackingList(
    destination: Annotated[str, "Trip destination name"],
    trip_type: Annotated[str, "Type of trip (e.g., beach, adventure, business, city-tour)"],
    duration_days: Annotated[int, "Duration of the trip in days"]
) -> str:
    """Generate a smart packing list."""
    try:
        base_items = [
            f"Clothing for {duration_days} days (+ 1 extra change)",
            "Underwear and socks",
            "Toiletries (toothbrush, toothpaste, deodorant, shampoo)",
            "Phone charger and power bank",
            "Passport / ID and travel tickets",
            "Necessary medications and first-aid basics"
        ]
        
        specific_items = []
        trip_type_lower = trip_type.lower()
        if "beach" in trip_type_lower:
            specific_items = ["Swimwear", "Sunglasses", "Sunscreen SPF 50+", "Beach towel", "Flip-flops"]
        elif "adventure" in trip_type_lower or "hiking" in trip_type_lower:
            specific_items = ["Sturdy hiking boots", "Backpack", "Water bottle", "Insect repellent", "Rain jacket"]
        elif "business" in trip_type_lower:
            specific_items = ["Formal suits / blazers", "Laptop & charger", "Notebook and pen", "Business cards"]
        else:
            specific_items = ["Comfortable walking shoes", "Camera", "Light jacket"]
            
        all_items = base_items + specific_items
        
        result = f"--- Recommended Packing List for {destination} ({trip_type}) ---\n"
        for i, item in enumerate(all_items, 1):
            result += f"{i}. [ ] {item}\n"
            
        return result.strip()
    except Exception as e:
        return f"Error generating packing list: {str(e)}"


toolsTravelAssist = [
    SearchFlightOptions,
    SearchHotelOptions,
    PlanRouteAndTransport,
    CalculateTripBudget,
    GeneratePackingList
]

def ToolsList():
    global toolsTravelAssist
    return toolsTravelAssist
