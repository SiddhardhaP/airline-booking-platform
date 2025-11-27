"""
Airport database for autocomplete
Contains IATA code, city name, airport name, and country
"""
AIRPORTS = [
    # India
    {"code": "HYD", "city": "Hyderabad", "name": "Rajiv Gandhi International Airport", "country": "India"},
    {"code": "BOM", "city": "Mumbai", "name": "Chhatrapati Shivaji Maharaj International Airport", "country": "India"},
    {"code": "DEL", "city": "Delhi", "name": "Indira Gandhi International Airport", "country": "India"},
    {"code": "BLR", "city": "Bangalore", "name": "Kempegowda International Airport", "country": "India"},
    {"code": "MAA", "city": "Chennai", "name": "Chennai International Airport", "country": "India"},
    {"code": "CCU", "city": "Kolkata", "name": "Netaji Subhas Chandra Bose International Airport", "country": "India"},
    {"code": "PNQ", "city": "Pune", "name": "Pune Airport", "country": "India"},
    {"code": "AMD", "city": "Ahmedabad", "name": "Sardar Vallabhbhai Patel International Airport", "country": "India"},
    {"code": "GOI", "city": "Goa", "name": "Goa International Airport", "country": "India"},
    {"code": "COK", "city": "Kochi", "name": "Cochin International Airport", "country": "India"},
    {"code": "IXC", "city": "Chandigarh", "name": "Chandigarh Airport", "country": "India"},
    {"code": "JAI", "city": "Jaipur", "name": "Jaipur International Airport", "country": "India"},
    {"code": "LKO", "city": "Lucknow", "name": "Chaudhary Charan Singh International Airport", "country": "India"},
    {"code": "VGA", "city": "Vijayawada", "name": "Vijayawada Airport", "country": "India"},
    {"code": "VTZ", "city": "Visakhapatnam", "name": "Visakhapatnam Airport", "country": "India"},
    {"code": "IDR", "city": "Indore", "name": "Devi Ahilya Bai Holkar Airport", "country": "India"},
    {"code": "NAG", "city": "Nagpur", "name": "Dr. Babasaheb Ambedkar International Airport", "country": "India"},
    {"code": "STV", "city": "Surat", "name": "Surat Airport", "country": "India"},
    {"code": "CJB", "city": "Coimbatore", "name": "Coimbatore International Airport", "country": "India"},
    {"code": "TRV", "city": "Trivandrum", "name": "Trivandrum International Airport", "country": "India"},
    {"code": "IXB", "city": "Bagdogra", "name": "Bagdogra Airport", "country": "India"},
    {"code": "GAU", "city": "Guwahati", "name": "Lokpriya Gopinath Bordoloi International Airport", "country": "India"},
    {"code": "IXR", "city": "Ranchi", "name": "Birsa Munda Airport", "country": "India"},
    {"code": "PAT", "city": "Patna", "name": "Jay Prakash Narayan Airport", "country": "India"},
    {"code": "BBI", "city": "Bhubaneswar", "name": "Biju Patnaik International Airport", "country": "India"},
    {"code": "IXZ", "city": "Port Blair", "name": "Veer Savarkar International Airport", "country": "India"},
    {"code": "SXR", "city": "Srinagar", "name": "Sheikh ul-Alam International Airport", "country": "India"},
    {"code": "IXJ", "city": "Jammu", "name": "Jammu Airport", "country": "India"},
    {"code": "IXA", "city": "Agartala", "name": "Agartala Airport", "country": "India"},
    {"code": "IXD", "city": "Allahabad", "name": "Allahabad Airport", "country": "India"},
    {"code": "RPR", "city": "Raipur", "name": "Swami Vivekananda Airport", "country": "India"},
    {"code": "JLR", "city": "Jabalpur", "name": "Jabalpur Airport", "country": "India"},
    {"code": "UDR", "city": "Udaipur", "name": "Maharana Pratap Airport", "country": "India"},
    {"code": "JDH", "city": "Jodhpur", "name": "Jodhpur Airport", "country": "India"},
    {"code": "BDQ", "city": "Vadodara", "name": "Vadodara Airport", "country": "India"},
    {"code": "IXU", "city": "Aurangabad", "name": "Aurangabad Airport", "country": "India"},
    {"code": "IXE", "city": "Mangalore", "name": "Mangalore International Airport", "country": "India"},
    
    # USA
    {"code": "JFK", "city": "New York", "name": "John F. Kennedy International Airport", "country": "United States"},
    {"code": "LAX", "city": "Los Angeles", "name": "Los Angeles International Airport", "country": "United States"},
    {"code": "ORD", "city": "Chicago", "name": "O'Hare International Airport", "country": "United States"},
    {"code": "SFO", "city": "San Francisco", "name": "San Francisco International Airport", "country": "United States"},
    {"code": "DFW", "city": "Dallas", "name": "Dallas/Fort Worth International Airport", "country": "United States"},
    {"code": "MIA", "city": "Miami", "name": "Miami International Airport", "country": "United States"},
    {"code": "SEA", "city": "Seattle", "name": "Seattle-Tacoma International Airport", "country": "United States"},
    {"code": "LAS", "city": "Las Vegas", "name": "McCarran International Airport", "country": "United States"},
    {"code": "ATL", "city": "Atlanta", "name": "Hartsfield-Jackson Atlanta International Airport", "country": "United States"},
    {"code": "BOS", "city": "Boston", "name": "Logan International Airport", "country": "United States"},
    {"code": "DEN", "city": "Denver", "name": "Denver International Airport", "country": "United States"},
    {"code": "PHX", "city": "Phoenix", "name": "Phoenix Sky Harbor International Airport", "country": "United States"},
    {"code": "SAN", "city": "San Diego", "name": "San Diego International Airport", "country": "United States"},
    {"code": "IAD", "city": "Washington", "name": "Washington Dulles International Airport", "country": "United States"},
    {"code": "DCA", "city": "Washington", "name": "Ronald Reagan Washington National Airport", "country": "United States"},
    {"code": "PHL", "city": "Philadelphia", "name": "Philadelphia International Airport", "country": "United States"},
    {"code": "DTW", "city": "Detroit", "name": "Detroit Metropolitan Airport", "country": "United States"},
    {"code": "MSP", "city": "Minneapolis", "name": "Minneapolis-Saint Paul International Airport", "country": "United States"},
    {"code": "BWI", "city": "Baltimore", "name": "Baltimore/Washington International Airport", "country": "United States"},
    {"code": "HOU", "city": "Houston", "name": "William P. Hobby Airport", "country": "United States"},
    {"code": "IAH", "city": "Houston", "name": "George Bush Intercontinental Airport", "country": "United States"},
    {"code": "MCO", "city": "Orlando", "name": "Orlando International Airport", "country": "United States"},
    {"code": "TPA", "city": "Tampa", "name": "Tampa International Airport", "country": "United States"},
    {"code": "FLL", "city": "Fort Lauderdale", "name": "Fort Lauderdale-Hollywood International Airport", "country": "United States"},
    {"code": "PDX", "city": "Portland", "name": "Portland International Airport", "country": "United States"},
    {"code": "STL", "city": "St. Louis", "name": "St. Louis Lambert International Airport", "country": "United States"},
    {"code": "CLE", "city": "Cleveland", "name": "Cleveland Hopkins International Airport", "country": "United States"},
    {"code": "BNA", "city": "Nashville", "name": "Nashville International Airport", "country": "United States"},
    {"code": "AUS", "city": "Austin", "name": "Austin-Bergstrom International Airport", "country": "United States"},
    
    # Europe
    {"code": "LHR", "city": "London", "name": "Heathrow Airport", "country": "United Kingdom"},
    {"code": "CDG", "city": "Paris", "name": "Charles de Gaulle Airport", "country": "France"},
    {"code": "FRA", "city": "Frankfurt", "name": "Frankfurt Airport", "country": "Germany"},
    {"code": "AMS", "city": "Amsterdam", "name": "Amsterdam Airport Schiphol", "country": "Netherlands"},
    {"code": "MAD", "city": "Madrid", "name": "Adolfo Suárez Madrid–Barajas Airport", "country": "Spain"},
    {"code": "FCO", "city": "Rome", "name": "Leonardo da Vinci–Fiumicino Airport", "country": "Italy"},
    {"code": "IST", "city": "Istanbul", "name": "Istanbul Airport", "country": "Turkey"},
    {"code": "BER", "city": "Berlin", "name": "Berlin Brandenburg Airport", "country": "Germany"},
    {"code": "MUC", "city": "Munich", "name": "Munich Airport", "country": "Germany"},
    {"code": "DUS", "city": "Düsseldorf", "name": "Düsseldorf Airport", "country": "Germany"},
    {"code": "HAM", "city": "Hamburg", "name": "Hamburg Airport", "country": "Germany"},
    {"code": "ZRH", "city": "Zurich", "name": "Zurich Airport", "country": "Switzerland"},
    {"code": "GVA", "city": "Geneva", "name": "Geneva Airport", "country": "Switzerland"},
    {"code": "VIE", "city": "Vienna", "name": "Vienna International Airport", "country": "Austria"},
    {"code": "BRU", "city": "Brussels", "name": "Brussels Airport", "country": "Belgium"},
    {"code": "CPH", "city": "Copenhagen", "name": "Copenhagen Airport", "country": "Denmark"},
    {"code": "ARN", "city": "Stockholm", "name": "Stockholm Arlanda Airport", "country": "Sweden"},
    {"code": "OSL", "city": "Oslo", "name": "Oslo Airport", "country": "Norway"},
    {"code": "HEL", "city": "Helsinki", "name": "Helsinki Airport", "country": "Finland"},
    {"code": "DUB", "city": "Dublin", "name": "Dublin Airport", "country": "Ireland"},
    {"code": "EDI", "city": "Edinburgh", "name": "Edinburgh Airport", "country": "United Kingdom"},
    {"code": "MAN", "city": "Manchester", "name": "Manchester Airport", "country": "United Kingdom"},
    {"code": "BCN", "city": "Barcelona", "name": "Barcelona-El Prat Airport", "country": "Spain"},
    {"code": "LIS", "city": "Lisbon", "name": "Lisbon Airport", "country": "Portugal"},
    {"code": "ATH", "city": "Athens", "name": "Athens International Airport", "country": "Greece"},
    {"code": "PRG", "city": "Prague", "name": "Václav Havel Airport Prague", "country": "Czech Republic"},
    {"code": "BUD", "city": "Budapest", "name": "Budapest Ferenc Liszt International Airport", "country": "Hungary"},
    {"code": "WAW", "city": "Warsaw", "name": "Warsaw Chopin Airport", "country": "Poland"},
    {"code": "MXP", "city": "Milan", "name": "Milan Malpensa Airport", "country": "Italy"},
    {"code": "VCE", "city": "Venice", "name": "Venice Marco Polo Airport", "country": "Italy"},
    {"code": "FLR", "city": "Florence", "name": "Florence Airport", "country": "Italy"},
    
    # Middle East & Asia
    {"code": "DXB", "city": "Dubai", "name": "Dubai International Airport", "country": "United Arab Emirates"},
    {"code": "AUH", "city": "Abu Dhabi", "name": "Abu Dhabi International Airport", "country": "United Arab Emirates"},
    {"code": "SIN", "city": "Singapore", "name": "Singapore Changi Airport", "country": "Singapore"},
    {"code": "BKK", "city": "Bangkok", "name": "Suvarnabhumi Airport", "country": "Thailand"},
    {"code": "KUL", "city": "Kuala Lumpur", "name": "Kuala Lumpur International Airport", "country": "Malaysia"},
    {"code": "HKG", "city": "Hong Kong", "name": "Hong Kong International Airport", "country": "Hong Kong"},
    {"code": "NRT", "city": "Tokyo", "name": "Narita International Airport", "country": "Japan"},
    {"code": "ICN", "city": "Seoul", "name": "Incheon International Airport", "country": "South Korea"},
    {"code": "PEK", "city": "Beijing", "name": "Beijing Capital International Airport", "country": "China"},
    {"code": "PVG", "city": "Shanghai", "name": "Shanghai Pudong International Airport", "country": "China"},
    {"code": "CAN", "city": "Guangzhou", "name": "Guangzhou Baiyun International Airport", "country": "China"},
    {"code": "SZX", "city": "Shenzhen", "name": "Shenzhen Bao'an International Airport", "country": "China"},
    {"code": "CTU", "city": "Chengdu", "name": "Chengdu Shuangliu International Airport", "country": "China"},
    {"code": "HND", "city": "Tokyo", "name": "Tokyo Haneda Airport", "country": "Japan"},
    {"code": "KIX", "city": "Osaka", "name": "Kansai International Airport", "country": "Japan"},
    {"code": "GMP", "city": "Seoul", "name": "Gimpo International Airport", "country": "South Korea"},
    {"code": "DOH", "city": "Doha", "name": "Hamad International Airport", "country": "Qatar"},
    {"code": "RUH", "city": "Riyadh", "name": "King Khalid International Airport", "country": "Saudi Arabia"},
    {"code": "JED", "city": "Jeddah", "name": "King Abdulaziz International Airport", "country": "Saudi Arabia"},
    {"code": "BAH", "city": "Manama", "name": "Bahrain International Airport", "country": "Bahrain"},
    {"code": "KWI", "city": "Kuwait City", "name": "Kuwait International Airport", "country": "Kuwait"},
    {"code": "MCT", "city": "Muscat", "name": "Muscat International Airport", "country": "Oman"},
    {"code": "CGK", "city": "Jakarta", "name": "Soekarno-Hatta International Airport", "country": "Indonesia"},
    {"code": "DPS", "city": "Bali", "name": "Ngurah Rai International Airport", "country": "Indonesia"},
    {"code": "MNL", "city": "Manila", "name": "Ninoy Aquino International Airport", "country": "Philippines"},
    {"code": "DAC", "city": "Dhaka", "name": "Hazrat Shahjalal International Airport", "country": "Bangladesh"},
    {"code": "KTM", "city": "Kathmandu", "name": "Tribhuvan International Airport", "country": "Nepal"},
    {"code": "CMB", "city": "Colombo", "name": "Bandaranaike International Airport", "country": "Sri Lanka"},
    {"code": "ISB", "city": "Islamabad", "name": "Islamabad International Airport", "country": "Pakistan"},
    {"code": "KHI", "city": "Karachi", "name": "Jinnah International Airport", "country": "Pakistan"},
    {"code": "LHE", "city": "Lahore", "name": "Allama Iqbal International Airport", "country": "Pakistan"},
    {"code": "HAN", "city": "Hanoi", "name": "Noi Bai International Airport", "country": "Vietnam"},
    {"code": "SGN", "city": "Ho Chi Minh City", "name": "Tan Son Nhat International Airport", "country": "Vietnam"},
    {"code": "BWN", "city": "Bandar Seri Begawan", "name": "Brunei International Airport", "country": "Brunei"},
    
    # Australia & Oceania
    {"code": "SYD", "city": "Sydney", "name": "Sydney Kingsford Smith Airport", "country": "Australia"},
    {"code": "MEL", "city": "Melbourne", "name": "Melbourne Airport", "country": "Australia"},
    {"code": "BNE", "city": "Brisbane", "name": "Brisbane Airport", "country": "Australia"},
    {"code": "PER", "city": "Perth", "name": "Perth Airport", "country": "Australia"},
    {"code": "ADL", "city": "Adelaide", "name": "Adelaide Airport", "country": "Australia"},
    {"code": "AKL", "city": "Auckland", "name": "Auckland Airport", "country": "New Zealand"},
    {"code": "WLG", "city": "Wellington", "name": "Wellington Airport", "country": "New Zealand"},
    
    # Canada
    {"code": "YYZ", "city": "Toronto", "name": "Toronto Pearson International Airport", "country": "Canada"},
    {"code": "YVR", "city": "Vancouver", "name": "Vancouver International Airport", "country": "Canada"},
    {"code": "YUL", "city": "Montreal", "name": "Montreal-Pierre Elliott Trudeau International Airport", "country": "Canada"},
    {"code": "YYC", "city": "Calgary", "name": "Calgary International Airport", "country": "Canada"},
    {"code": "YEG", "city": "Edmonton", "name": "Edmonton International Airport", "country": "Canada"},
    {"code": "YOW", "city": "Ottawa", "name": "Ottawa Macdonald-Cartier International Airport", "country": "Canada"},
    
    # South America
    {"code": "GRU", "city": "São Paulo", "name": "São Paulo-Guarulhos International Airport", "country": "Brazil"},
    {"code": "GIG", "city": "Rio de Janeiro", "name": "Rio de Janeiro-Galeão International Airport", "country": "Brazil"},
    {"code": "EZE", "city": "Buenos Aires", "name": "Ministro Pistarini International Airport", "country": "Argentina"},
    {"code": "SCL", "city": "Santiago", "name": "Arturo Merino Benítez International Airport", "country": "Chile"},
    {"code": "LIM", "city": "Lima", "name": "Jorge Chávez International Airport", "country": "Peru"},
    {"code": "BOG", "city": "Bogotá", "name": "El Dorado International Airport", "country": "Colombia"},
    
    # Africa
    {"code": "JNB", "city": "Johannesburg", "name": "O. R. Tambo International Airport", "country": "South Africa"},
    {"code": "CPT", "city": "Cape Town", "name": "Cape Town International Airport", "country": "South Africa"},
    {"code": "CAI", "city": "Cairo", "name": "Cairo International Airport", "country": "Egypt"},
    {"code": "NBO", "city": "Nairobi", "name": "Jomo Kenyatta International Airport", "country": "Kenya"},
    {"code": "LOS", "city": "Lagos", "name": "Murtala Muhammed International Airport", "country": "Nigeria"},
    {"code": "CMN", "city": "Casablanca", "name": "Mohammed V International Airport", "country": "Morocco"},
]


def search_airports(query: str, limit: int = 10) -> list:
    """
    Search airports by IATA code, city name, or airport name
    Returns list of matching airports
    """
    if not query or len(query) < 2:
        return []
    
    query_lower = query.lower().strip()
    results = []
    
    for airport in AIRPORTS:
        # Check if query matches IATA code (exact match preferred)
        if airport["code"].lower() == query_lower:
            results.insert(0, airport)  # Exact code match at top
            continue
        
        # Check if query matches city name
        if query_lower in airport["city"].lower():
            results.append(airport)
            continue
        
        # Check if query matches airport name
        if query_lower in airport["name"].lower():
            results.append(airport)
            continue
        
        # Check if query matches IATA code (partial)
        if query_lower in airport["code"].lower():
            results.append(airport)
            continue
    
    # Remove duplicates while preserving order
    seen = set()
    unique_results = []
    for airport in results:
        airport_id = airport["code"]
        if airport_id not in seen:
            seen.add(airport_id)
            unique_results.append(airport)
    
    return unique_results[:limit]


def get_city_by_code(code: str) -> str:
    """
    Get city name by airport IATA code
    Returns city name if found, otherwise returns the code
    """
    if not code:
        return None
    
    code_upper = code.upper().strip()
    for airport in AIRPORTS:
        if airport["code"] == code_upper:
            return airport["city"]
    
    return None  # Return None if not found

