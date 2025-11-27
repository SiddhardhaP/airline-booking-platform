"""
Flight Search Agent
Searches for flights using backend API
"""
import os
import httpx
import logging
from .base import AgentState

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
logger = logging.getLogger(__name__)

# City to airport code mapping (expanded for better coverage)
CITY_TO_AIRPORT = {
    # India
    "hyderabad": "HYD",
    "mumbai": "BOM",
    "delhi": "DEL",
    "bangalore": "BLR",
    "chennai": "MAA",
    "kolkata": "CCU",
    "pune": "PNQ",
    "ahmedabad": "AMD",
    "goa": "GOI",
    "kochi": "COK",
    "cochin": "COK",
    "chandigarh": "IXC",
    "jaipur": "JAI",
    "lucknow": "LKO",
    "vijayawada": "VGA",
    "visakhapatnam": "VTZ",
    "vizag": "VTZ",
    "indore": "IDR",
    "nagpur": "NAG",
    "surat": "STV",
    "coimbatore": "CJB",
    "trivandrum": "TRV",
    "thiruvananthapuram": "TRV",
    "bagdogra": "IXB",
    "guwahati": "GAU",
    "ranchi": "IXR",
    "patna": "PAT",
    "bhubaneswar": "BBI",
    "port blair": "IXZ",
    "srinagar": "SXR",
    "jammu": "IXJ",
    "agartala": "IXA",
    "allahabad": "IXD",
    "raipur": "RPR",
    "jabalpur": "JLR",
    "udaipur": "UDR",
    "jodhpur": "JDH",
    "vadodara": "BDQ",
    "baroda": "BDQ",
    "aurangabad": "IXU",
    "mangalore": "IXE",
    
    # USA
    "new york": "JFK",
    "los angeles": "LAX",
    "chicago": "ORD",
    "san francisco": "SFO",
    "dallas": "DFW",
    "miami": "MIA",
    "seattle": "SEA",
    "las vegas": "LAS",
    "atlanta": "ATL",
    "boston": "BOS",
    "denver": "DEN",
    "phoenix": "PHX",
    "san diego": "SAN",
    "washington": "IAD",
    "philadelphia": "PHL",
    "detroit": "DTW",
    "minneapolis": "MSP",
    "baltimore": "BWI",
    "houston": "IAH",
    "orlando": "MCO",
    "tampa": "TPA",
    "fort lauderdale": "FLL",
    "portland": "PDX",
    "st louis": "STL",
    "cleveland": "CLE",
    "nashville": "BNA",
    "austin": "AUS",
    
    # Europe
    "london": "LHR",
    "paris": "CDG",
    "frankfurt": "FRA",
    "amsterdam": "AMS",
    "madrid": "MAD",
    "rome": "FCO",
    "istanbul": "IST",
    "berlin": "BER",
    "munich": "MUC",
    "düsseldorf": "DUS",
    "hamburg": "HAM",
    "zurich": "ZRH",
    "geneva": "GVA",
    "vienna": "VIE",
    "brussels": "BRU",
    "copenhagen": "CPH",
    "stockholm": "ARN",
    "oslo": "OSL",
    "helsinki": "HEL",
    "dublin": "DUB",
    "edinburgh": "EDI",
    "manchester": "MAN",
    "barcelona": "BCN",
    "lisbon": "LIS",
    "athens": "ATH",
    "prague": "PRG",
    "budapest": "BUD",
    "warsaw": "WAW",
    "milan": "MXP",
    "venice": "VCE",
    "florence": "FLR",
    
    # Middle East & Asia
    "dubai": "DXB",
    "abu dhabi": "AUH",
    "singapore": "SIN",
    "bangkok": "BKK",
    "kuala lumpur": "KUL",
    "hong kong": "HKG",
    "tokyo": "NRT",
    "seoul": "ICN",
    "beijing": "PEK",
    "shanghai": "PVG",
    "guangzhou": "CAN",
    "shenzhen": "SZX",
    "chengdu": "CTU",
    "osaka": "KIX",
    "doha": "DOH",
    "riyadh": "RUH",
    "jeddah": "JED",
    "manama": "BAH",
    "kuwait": "KWI",
    "kuwait city": "KWI",
    "muscat": "MCT",
    "jakarta": "CGK",
    "bali": "DPS",
    "manila": "MNL",
    "dhaka": "DAC",
    "kathmandu": "KTM",
    "colombo": "CMB",
    "islamabad": "ISB",
    "karachi": "KHI",
    "lahore": "LHE",
    "hanoi": "HAN",
    "ho chi minh city": "SGN",
    "saigon": "SGN",
    
    # Australia & Oceania
    "sydney": "SYD",
    "melbourne": "MEL",
    "brisbane": "BNE",
    "perth": "PER",
    "adelaide": "ADL",
    "auckland": "AKL",
    "wellington": "WLG",
    
    # Canada
    "toronto": "YYZ",
    "vancouver": "YVR",
    "montreal": "YUL",
    "calgary": "YYC",
    "edmonton": "YEG",
    "ottawa": "YOW",
    
    # South America
    "são paulo": "GRU",
    "sao paulo": "GRU",
    "rio de janeiro": "GIG",
    "rio": "GIG",
    "buenos aires": "EZE",
    "santiago": "SCL",
    "lima": "LIM",
    "bogotá": "BOG",
    "bogota": "BOG",
    
    # Africa
    "johannesburg": "JNB",
    "cape town": "CPT",
    "cairo": "CAI",
    "nairobi": "NBO",
    "lagos": "LOS",
    "casablanca": "CMN",
}


def normalize_airport_code(code_or_city: str) -> str:
    """Convert city name or airport code to uppercase airport code"""
    if not code_or_city:
        return None
    
    code_or_city = code_or_city.strip().lower()
    
    # If it's already a 3-letter code, return uppercase
    if len(code_or_city) == 3 and code_or_city.isalpha():
        return code_or_city.upper()
    
    # Try to map city name to airport code
    return CITY_TO_AIRPORT.get(code_or_city, code_or_city.upper())


async def flight_search_agent(state: AgentState) -> AgentState:
    """Search for flights using backend API"""
    slots = state["slots"]
    logger.info(f"Flight Search Agent: Starting search with slots: {slots}")
    
    origin = normalize_airport_code(slots.get("origin"))
    destination = normalize_airport_code(slots.get("destination"))
    departure_date = slots.get("departure_date")
    # Handle None values - default to 1 if not provided or None
    adults_raw = slots.get("adults")
    if adults_raw is None:
        adults = 1
    else:
        # Ensure it's an integer
        try:
            adults = int(adults_raw)
            if adults < 1:
                adults = 1
        except (ValueError, TypeError):
            adults = 1
    
    logger.info(f"Flight Search Agent: Normalized - Origin: {origin}, Destination: {destination}, Date: {departure_date}, Adults: {adults}")
    
    if not all([origin, destination, departure_date]):
        missing = []
        if not origin:
            missing.append("origin (city or airport code)")
        if not destination:
            missing.append("destination (city or airport code)")
        if not departure_date:
            missing.append("departure date (YYYY-MM-DD)")
        
        # Show what we understood
        understood = []
        if origin:
            understood.append(f"Origin: {origin}")
        if destination:
            understood.append(f"Destination: {destination}")
        if departure_date:
            understood.append(f"Date: {departure_date}")
        
        response = "I need a few more details to search for flights.\n"
        if understood:
            response += f"I understood: {', '.join(understood)}\n"
        response += f"Please provide: {', '.join(missing)}"
        
        state["response"] = response
        return state
    
    try:
        logger.info(f"Flight Search Agent: Calling API - {BACKEND_URL}/api/flight/search")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/api/flight/search",
                json={
                    "origin": origin,
                    "destination": destination,
                    "departure_date": departure_date,
                    "adults": adults,
                    "children": 0,
                    "infants": 0,
                },
                timeout=20.0,  # Reduced from 30.0 to 20.0
            )
            
            logger.info(f"Flight Search Agent: API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                state["flight_search_results"] = data.get("offers", [])
                logger.info(f"Flight Search Agent: Found {len(state['flight_search_results'])} flights")
                
                if state["flight_search_results"]:
                    offers_text = "\n".join([
                        f"{i+1}. {offer['airline']} {offer['flight_no']} - ₹{offer['price']:.2f} ({offer['origin']} to {offer['destination']}, Offer ID: {offer['offer_id']})"
                        for i, offer in enumerate(state["flight_search_results"])
                    ])
                    state["response"] = f"✈️ I found {len(state['flight_search_results'])} flights from {origin} to {destination} on {departure_date}:\n\n{offers_text}\n\nPlease select an offer by number (1-{len(state['flight_search_results'])}) or provide the offer ID."
                else:
                    state["response"] = f"❌ No flights found from {origin} to {destination} on {departure_date}. Please try different dates or airports."
            else:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "")
                    logger.error(f"Flight Search Agent: API error - {error_detail}")
                except:
                    pass
                state["response"] = f"Sorry, I couldn't search for flights right now. {error_detail if error_detail else 'Please try again.'}"
    
    except Exception as e:
        logger.error(f"Flight Search Agent: Exception occurred: {str(e)}", exc_info=True)
        state["response"] = f"Flight search failed: {str(e)}\n\nI was searching for:\n- Origin: {origin}\n- Destination: {destination}\n- Date: {departure_date}\n\nPlease check if the airport codes and date format are correct."
    
    return state

