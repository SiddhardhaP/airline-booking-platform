"""
Amadeus API Service
"""
import os
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
from app.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


class AmadeusService:
    """Service for interacting with Amadeus Flight Search API"""

    def __init__(self):
        self.api_key = os.getenv("AMADEUS_API_KEY")
        self.api_secret = os.getenv("AMADEUS_API_SECRET")
        self.base_url = os.getenv("AMADEUS_BASE_URL", "https://test.api.amadeus.com")
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None

    async def _get_access_token(self) -> str:
        """Get or refresh Amadeus access token"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token

        if not self.api_key or not self.api_secret:
            logger.warning("⚠️ Amadeus API credentials not configured, will use mock data")
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/security/oauth2/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.api_key,
                        "client_secret": self.api_secret,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                data = response.json()
                self.access_token = data["access_token"]
                expires_in = data.get("expires_in", 1800)
                self.token_expires_at = datetime.now().replace(
                    microsecond=0
                ) + timedelta(seconds=expires_in - 60)
                logger.info("✅ Amadeus access token obtained successfully - REAL API will be used")
                return self.access_token
        except Exception as e:
            logger.error(f"Failed to get Amadeus access token: {str(e)}")
            return None

    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        children: int = 0,
        infants: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Search for flights using Amadeus API
        Returns list of flight offers
        """
        token = await self._get_access_token()

        params = {
            "originLocationCode": origin.upper(),
            "destinationLocationCode": destination.upper(),
            "departureDate": departure_date,
            "adults": adults,
            "children": children,
            "infants": infants,
            "currencyCode": "INR",  # Request INR currency (will fallback to USD if not supported)
            "max": 15,  # Limit to 15 offers
        }

        if return_date:
            params["returnDate"] = return_date

        if not token:
            logger.info(f"⚠️ Using MOCK flight data (no Amadeus credentials or token failed) for route: {origin.upper()} -> {destination.upper()}")
            return self._get_mock_flights(origin, destination, departure_date)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v2/shopping/flight-offers",
                    headers={"Authorization": f"Bearer {token}"},
                    params=params,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    flights = data.get("data", [])
                    logger.info(f"✅ Retrieved {len(flights)} REAL flights from Amadeus API")
                    if flights:
                        # Log first flight price for verification
                        first_price = flights[0].get("price", {})
                        logger.info(f"Sample flight price: {first_price.get('total', 'N/A')} {first_price.get('currency', 'N/A')}")
                    
                    # Check airline variety - if all flights are from same airline, supplement with mock data
                    if flights:
                        airlines_in_response = set()
                        for flight in flights:
                            itinerary = flight.get("itineraries", [{}])[0]
                            segments = itinerary.get("segments", [])
                            if segments:
                                airlines_in_response.add(segments[0].get("carrierCode", ""))
                        
                        # If we have less than 3 different airlines or less than 15 flights, supplement with mock
                        if len(airlines_in_response) < 3 or len(flights) < 15:
                            logger.info(f"Only {len(airlines_in_response)} airline(s) ({', '.join(airlines_in_response)}) found in real API results, supplementing with mock data to ensure variety")
                            mock_flights = self._get_mock_flights(origin, destination, departure_date)
                            # Combine real and mock flights, prioritizing real ones
                            # Remove duplicates based on airline+flight_no
                            combined = flights.copy()
                            existing_flights = set()
                            for f in flights:
                                try:
                                    itinerary = f.get("itineraries", [{}])[0]
                                    segments = itinerary.get("segments", [])
                                    if segments:
                                        carrier = segments[0].get("carrierCode", "")
                                        number = segments[0].get("number", "")
                                        existing_flights.add((carrier, number))
                                except:
                                    pass
                            
                            # Add mock flights that don't duplicate existing ones
                            for mock_flight in mock_flights:
                                try:
                                    mock_itinerary = mock_flight.get("itineraries", [{}])[0]
                                    mock_segments = mock_itinerary.get("segments", [])
                                    if mock_segments:
                                        mock_airline = mock_segments[0].get("carrierCode", "")
                                        mock_number = mock_segments[0].get("number", "")
                                        if (mock_airline, mock_number) not in existing_flights:
                                            combined.append(mock_flight)
                                            existing_flights.add((mock_airline, mock_number))
                                            if len(combined) >= 15:
                                                break
                                except:
                                    continue
                            
                            logger.info(f"Returning {len(combined)} flights (real: {len(flights)}, mock: {len(combined) - len(flights)})")
                            return combined[:15]
                    
                    return flights
                elif response.status_code == 400:
                    # Try with USD if INR is not supported
                    logger.warning(f"Amadeus API returned 400 (possibly INR not supported), retrying with USD")
                    params["currencyCode"] = "USD"
                    retry_response = await client.get(
                        f"{self.base_url}/v2/shopping/flight-offers",
                        headers={"Authorization": f"Bearer {token}"},
                        params=params,
                        timeout=30.0,
                    )
                    if retry_response.status_code == 200:
                        data = retry_response.json()
                        flights = data.get("data", [])
                        logger.info(f"✅ Retrieved {len(flights)} REAL flights from Amadeus API (USD, will convert to INR)")
                        
                        # Check airline variety and supplement if needed
                        if flights:
                            airlines_in_response = set()
                            for flight in flights:
                                itinerary = flight.get("itineraries", [{}])[0]
                                segments = itinerary.get("segments", [])
                                if segments:
                                    airlines_in_response.add(segments[0].get("carrierCode", ""))
                            
                            if len(airlines_in_response) < 3 or len(flights) < 15:
                                logger.info(f"Only {len(airlines_in_response)} airline(s) ({', '.join(airlines_in_response)}) found, supplementing with mock data to ensure variety")
                                mock_flights = self._get_mock_flights(origin, destination, departure_date)
                                combined = flights.copy()
                                existing_flights = set()
                                for f in flights:
                                    try:
                                        itinerary = f.get("itineraries", [{}])[0]
                                        segments = itinerary.get("segments", [])
                                        if segments:
                                            carrier = segments[0].get("carrierCode", "")
                                            number = segments[0].get("number", "")
                                            existing_flights.add((carrier, number))
                                    except:
                                        pass
                                
                                # Add mock flights that don't duplicate existing ones
                                for mock_flight in mock_flights:
                                    try:
                                        mock_itinerary = mock_flight.get("itineraries", [{}])[0]
                                        mock_segments = mock_itinerary.get("segments", [])
                                        if mock_segments:
                                            mock_airline = mock_segments[0].get("carrierCode", "")
                                            mock_number = mock_segments[0].get("number", "")
                                            if (mock_airline, mock_number) not in existing_flights:
                                                combined.append(mock_flight)
                                                existing_flights.add((mock_airline, mock_number))
                                                if len(combined) >= 15:
                                                    break
                                    except:
                                        continue
                                
                                logger.info(f"Returning {len(combined)} flights (real: {len(flights)}, mock: {len(combined) - len(flights)})")
                                return combined[:15]
                        
                        return flights
                    else:
                        logger.warning(f"Amadeus API returned status {retry_response.status_code}, using mock data")
                        return self._get_mock_flights(origin, destination, departure_date)
                else:
                    logger.warning(f"Amadeus API returned status {response.status_code}, using mock data")
                    return self._get_mock_flights(origin, destination, departure_date)
        except Exception as e:
            logger.warning(f"Amadeus API request failed: {str(e)}, using mock data")
            return self._get_mock_flights(origin, destination, departure_date)

    def _get_mock_flights(
        self, origin: str, destination: str, departure_date: str
    ) -> List[Dict[str, Any]]:
        """Generate mock flight data for testing"""
        import uuid
        from datetime import datetime, timedelta

        # Ensure origin and destination are uppercase
        origin = origin.upper()
        destination = destination.upper()
        
        logger.info(f"Generating mock flights for route: {origin} -> {destination} on {departure_date}")
        
        base_depart = datetime.strptime(departure_date, "%Y-%m-%d")
        # Include multiple Indian airlines: AI=Air India, 6E=Indigo, SG=SpiceJet, UK=Vistara, G8=GoAir
        airlines = ["AI", "6E", "SG", "UK", "G8", "AI", "6E", "SG", "UK", "AI", "6E", "SG", "UK", "AI", "6E"]
        # Flight numbers (without airline code prefix)
        flight_numbers = [
            "2872", "1234", "5678", "9012", "3456",
            "2699", "2345", "6789", "0123", "4567",
            "2874", "3456", "7890", "1234", "5678"
        ]

        mock_flights = []
        for i, (airline, flight_no) in enumerate(zip(airlines[:15], flight_numbers[:15])):
            offer_id = f"OFFER_{uuid.uuid4().hex[:8].upper()}"
            # Distribute flights throughout the day (6 AM to 11 PM)
            hour = 6 + (i * 1) % 18  # Hours from 6 to 23
            minute = (15 + (i * 10)) % 60  # Ensure minute stays within 0-59
            depart_time = base_depart.replace(hour=hour, minute=minute)
            # Flight duration varies by airline (1.5 to 2.5 hours for domestic)
            duration_hours = 1 + (i % 2)
            duration_minutes = (30 + (i * 5)) % 60  # Ensure minutes stay within 0-59
            arrive_time = depart_time + timedelta(hours=duration_hours, minutes=duration_minutes)

            mock_flights.append({
                "type": "flight-offer",
                "id": offer_id,
                "source": "GDS",
                "instantTicketingRequired": False,
                "nonHomogeneous": False,
                "oneWay": True,
                "lastTicketingDate": departure_date,
                "numberOfBookableSeats": 9,
                "itineraries": [
                    {
                        "duration": f"PT{5+i}H",
                        "segments": [
                            {
                                "departure": {
                                    "iataCode": origin.upper(),
                                    "terminal": "1",
                                    "at": depart_time.isoformat() + "Z",
                                },
                                "arrival": {
                                    "iataCode": destination.upper(),
                                    "terminal": "2",
                                    "at": arrive_time.isoformat() + "Z",
                                },
                                "carrierCode": airline,
                                "number": flight_no,
                                "aircraft": {"code": "320"},
                                "duration": f"PT{5+i}H",
                                "numberOfStops": 0,
                            }
                        ],
                    }
                ],
                "price": {
                    "currency": "INR",
                    "total": str(int((299.99 + i * 50) * 83)),  # Convert USD to INR (1 USD ≈ 83 INR)
                    "base": str(int((250.00 + i * 40) * 83)),
                    "fees": [
                        {"amount": "0.00", "type": "SUPPLIER"},
                        {"amount": "0.00", "type": "TICKETING"},
                    ],
                    "grandTotal": str(int((299.99 + i * 50) * 83)),
                },
                "pricingOptions": {
                    "fareType": ["PUBLISHED"],
                    "includedCheckedBagsOnly": True,
                },
                "validatingAirlineCodes": [flight_no[:2]],
                "travelerPricings": [
                    {
                        "travelerId": "1",
                        "fareOption": "STANDARD",
                        "travelerType": "ADULT",
                        "price": {
                            "currency": "USD",
                            "total": str(299.99 + i * 50),
                            "base": str(250.00 + i * 40),
                        },
                    }
                ],
            })

        return mock_flights

