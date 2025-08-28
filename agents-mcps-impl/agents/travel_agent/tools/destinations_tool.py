import httpx
from google.adk.tools import BaseTool, ToolContext
from typing_extensions import override, Any
import os
from typing import List, Dict


class DestinationsTool(BaseTool):
    """A tool that provides comprehensive information about cities across different geographical regions.

    Attributes:
        name: The name of the tool.
        description: A brief description of what the tool does.
    """
    name = "DestinationsTool"
    description = "Lists cities in countries, continents, or united regions with detailed information"

    # Expanded destination data with more cities per country/region
    _destinations_data = {
        # Europe
        "europe": ["Paris", "London", "Rome", "Barcelona", "Amsterdam", "Berlin", "Prague", "Vienna", "Athens", "Lisbon", 
                  "Madrid", "Budapest", "Copenhagen", "Dublin", "Brussels", "Zurich", "Stockholm", "Oslo", "Helsinki"],
        "france": ["Paris", "Nice", "Lyon", "Marseille", "Bordeaux", "Strasbourg", "Toulouse", "Montpellier", 
                  "Lille", "Nantes", "Cannes", "Avignon", "Aix-en-Provence", "Annecy", "Colmar"],
        "italy": ["Rome", "Florence", "Venice", "Milan", "Naples", "Turin", "Bologna", "Verona", 
                 "Siena", "Pisa", "Palermo", "Genoa", "Sorrento", "Cinque Terre", "Lake Como", "Amalfi"],
        "spain": ["Barcelona", "Madrid", "Seville", "Valencia", "Granada", "Malaga", "Bilbao", "San Sebastian", 
                 "Toledo", "Cordoba", "Ibiza", "Mallorca", "Tenerife", "Cadiz", "Zaragoza"],
        "germany": ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne", "Dresden", "Stuttgart", "Nuremberg", 
                   "Heidelberg", "Leipzig", "Dusseldorf", "Bremen", "Hannover", "Freiburg", "Rothenburg"],
        "united kingdom": ["London", "Edinburgh", "Manchester", "Liverpool", "Glasgow", "Oxford", "Cambridge", "Bath", 
                          "York", "Belfast", "Cardiff", "Bristol", "Birmingham", "Brighton", "Stonehenge"],
        "switzerland": ["Zurich", "Geneva", "Bern", "Lucerne", "Zermatt", "Interlaken", "Lausanne", "Basel", 
                       "Lugano", "St. Moritz", "Montreux", "Grindelwald", "Davos"],
        
        # North America
        "usa": ["New York", "Los Angeles", "Chicago", "San Francisco", "Miami", "Las Vegas", "Boston", "Washington DC", 
               "Seattle", "New Orleans", "San Diego", "Austin", "Nashville", "Portland", "Charleston", "Savannah", 
               "Orlando", "Philadelphia", "Denver", "Honolulu", "Anchorage", "Atlanta"],
        "canada": ["Toronto", "Vancouver", "Montreal", "Quebec City", "Calgary", "Ottawa", "Victoria", "Halifax", 
                  "Banff", "Whistler", "Niagara Falls", "Edmonton", "Winnipeg", "Jasper", "St. John's"],
        "mexico": ["Mexico City", "Cancun", "Puerto Vallarta", "Oaxaca", "Guadalajara", "San Miguel de Allende", 
                  "Merida", "Playa del Carmen", "Tulum", "Los Cabos", "Puebla", "Monterrey"],
        
        # Asia
        "japan": ["Tokyo", "Kyoto", "Osaka", "Hiroshima", "Nara", "Sapporo", "Fukuoka", "Nagoya", 
                 "Yokohama", "Kobe", "Hakone", "Kanazawa", "Nikko", "Okinawa", "Takayama", "Kamakura"],
        "china": ["Beijing", "Shanghai", "Xi'an", "Hong Kong", "Chengdu", "Guilin", "Hangzhou", "Suzhou", 
                 "Guangzhou", "Shenzhen", "Lhasa", "Kunming", "Harbin", "Nanjing", "Macau"],
        "india": ["Delhi", "Mumbai", "Jaipur", "Agra", "Bangalore", "Chennai", "Kolkata", "Goa", 
                 "Varanasi", "Udaipur", "Kochi", "Hyderabad", "Amritsar", "Rishikesh", "Darjeeling"],
        "thailand": ["Bangkok", "Chiang Mai", "Phuket", "Krabi", "Koh Samui", "Pattaya", "Ayutthaya", 
                    "Hua Hin", "Koh Phi Phi", "Sukhothai", "Kanchanaburi"],
        
        # Oceania
        "australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Gold Coast", "Cairns", "Hobart", 
                     "Darwin", "Canberra", "Uluru", "Byron Bay", "Great Barrier Reef", "Margaret River", "Broome"],
        "new zealand": ["Auckland", "Wellington", "Queenstown", "Christchurch", "Rotorua", "Napier", "Dunedin", 
                       "Taupo", "Milford Sound", "Nelson", "Wanaka", "Kaikoura"],
        
        # Africa
        "south africa": ["Cape Town", "Johannesburg", "Durban", "Pretoria", "Stellenbosch", "Kruger National Park", 
                        "Garden Route", "Port Elizabeth", "Franschhoek", "Knysna"],
        "morocco": ["Marrakesh", "Casablanca", "Fez", "Tangier", "Rabat", "Chefchaouen", "Essaouira", 
                   "Agadir", "Meknes", "Ouarzazate"]
    }

    # Countries by continent/region with more comprehensive lists
    _countries_by_region = {
        "europe": ["France", "Italy", "Spain", "Germany", "United Kingdom", "Greece", "Portugal", "Netherlands", 
                  "Switzerland", "Belgium", "Austria", "Czech Republic", "Poland", "Hungary", "Sweden", "Norway",
                  "Denmark", "Finland", "Ireland", "Croatia", "Slovenia", "Estonia", "Latvia", "Lithuania",
                  "Luxembourg", "Malta", "Cyprus", "Slovakia", "Romania", "Bulgaria", "Serbia", "Montenegro"],
        
        "asia": ["Japan", "China", "India", "Thailand", "Vietnam", "Indonesia", "Malaysia", "Singapore", 
                "South Korea", "Philippines", "Cambodia", "Nepal", "Sri Lanka", "Taiwan", "Laos", "Myanmar",
                "Bhutan", "Mongolia", "Bangladesh", "Pakistan", "UAE", "Qatar", "Saudi Arabia", "Jordan",
                "Israel", "Lebanon", "Turkey"],
        
        "north america": ["USA", "Canada", "Mexico", "Costa Rica", "Cuba", "Jamaica", "Panama", "Guatemala",
                         "Dominican Republic", "Puerto Rico", "Bahamas", "Belize", "El Salvador", "Honduras",
                         "Nicaragua", "Haiti", "Trinidad and Tobago"],
        
        "south america": ["Brazil", "Argentina", "Peru", "Colombia", "Chile", "Ecuador", "Bolivia", "Venezuela",
                         "Uruguay", "Paraguay", "Guyana", "Suriname", "French Guiana"],
        
        "africa": ["South Africa", "Morocco", "Egypt", "Kenya", "Tanzania", "Namibia", "Botswana", "Ghana",
                  "Ethiopia", "Madagascar", "Zambia", "Zimbabwe", "Uganda", "Rwanda", "Senegal", "Mauritius",
                  "Tunisia", "Algeria", "Nigeria", "Mozambique", "Seychelles"],
        
        "oceania": ["Australia", "New Zealand", "Fiji", "Papua New Guinea", "Solomon Islands", "Vanuatu",
                   "Samoa", "Tonga", "Cook Islands", "French Polynesia", "New Caledonia"]
    }

    # United regions with their component countries
    _united_regions = {
        "scandinavia": ["Sweden", "Norway", "Denmark", "Finland", "Iceland"],
        "benelux": ["Belgium", "Netherlands", "Luxembourg"],
        "british isles": ["United Kingdom", "Ireland"],
        "iberian peninsula": ["Spain", "Portugal", "Andorra"],
        "balkans": ["Croatia", "Slovenia", "Serbia", "Bosnia and Herzegovina", "Montenegro", "North Macedonia", 
                   "Albania", "Bulgaria", "Romania", "Greece"],
        "baltic states": ["Estonia", "Latvia", "Lithuania"],
        "middle east": ["Turkey", "Syria", "Lebanon", "Israel", "Jordan", "Iraq", "Iran", "Saudi Arabia", 
                       "UAE", "Qatar", "Bahrain", "Kuwait", "Oman", "Yemen"],
        "southeast asia": ["Thailand", "Vietnam", "Indonesia", "Malaysia", "Singapore", "Philippines", 
                          "Cambodia", "Laos", "Myanmar", "Brunei", "East Timor"],
        "caribbean": ["Cuba", "Jamaica", "Dominican Republic", "Puerto Rico", "Bahamas", "Haiti", 
                     "Trinidad and Tobago", "Barbados", "Saint Lucia", "Antigua and Barbuda"],
        "central america": ["Mexico", "Guatemala", "Belize", "El Salvador", "Honduras", "Nicaragua", 
                           "Costa Rica", "Panama"]
    }

    # City information with key facts
    _city_info = {
        "paris": {"country": "France", "landmarks": ["Eiffel Tower", "Louvre Museum", "Notre Dame Cathedral"], 
                 "cuisine": "French cuisine featuring croissants, baguettes, and fine dining"},
        "rome": {"country": "Italy", "landmarks": ["Colosseum", "Vatican City", "Trevi Fountain"], 
                "cuisine": "Italian cuisine with pasta, pizza, and gelato"},
        "tokyo": {"country": "Japan", "landmarks": ["Tokyo Skytree", "Meiji Shrine", "Imperial Palace"], 
                 "cuisine": "Japanese cuisine including sushi, ramen, and tempura"},
        "new york": {"country": "USA", "landmarks": ["Statue of Liberty", "Times Square", "Central Park"], 
                    "cuisine": "Diverse international cuisine, famous for bagels, pizza, and fine dining"}
    }

    async def list_cities_capped(self, location: str, max_cities: int = 2) -> Dict[str, Any]:
        """Lists cities in a given country, continent, or united region with a cap on the number of cities returned.

        Attributes:
            location: The country, continent, or united region for which to list cities.
            max_cities: The maximum number of cities to return (default is 2).
        Returns:
            A dictionary containing cities data and related information, with cities list capped to max_cities.
        """
        # Get the full result
        result = await self.list_cities(location)

        # If the result contains cities, limit the number to max_cities
        if "cities" in result and isinstance(result["cities"], list):
            # Create a copy of the result to avoid modifying the original data
            capped_result = result.copy()
            capped_result["cities"] = result["cities"][:2]
            return capped_result

        # Return the original result if it doesn't contain a cities list
        return result

    async def list_cities(self, location: str) -> Dict[str, Any]:
        """Lists cities in a given country, continent, or united region with detailed information.

        Attributes:
            location: The country, continent, or united region for which to list cities.
        Returns:
            A dictionary containing cities data and related information.
        """
        location = location.lower()
        
        # If the location is a continent/region, return countries in that region
        if location in self._countries_by_region:
            return {
                "region_type": "continent",
                "region_name": location.title(),
                "countries": self._countries_by_region[location],
                "message": f"Here are the countries in {location.title()}. You can ask for cities in any of these countries."
            }
        
        # If the location is a united region, return countries in that region
        elif location in self._united_regions:
            return {
                "region_type": "united region",
                "region_name": location.title(),
                "countries": self._united_regions[location],
                "message": f"Here are the countries in the {location.title()} region. You can ask for cities in any of these countries."
            }
        
        # If the location is a country, return cities in that country
        elif location in self._destinations_data:
            return {
                "region_type": "country",
                "country_name": location.title(),
                "cities": self._destinations_data[location],
                "message": f"Here are popular cities and destinations in {location.title()}."
            }
        
        # If we have detailed info about a specific city
        elif location in self._city_info:
            city_data = self._city_info[location]
            return {
                "region_type": "city",
                "city_name": location.title(),
                "country": city_data["country"],
                "landmarks": city_data["landmarks"],
                "cuisine": city_data["cuisine"],
                "message": f"Here's information about {location.title()}, located in {city_data['country']}."
            }
        
        else:
            # Try to find a partial match for countries
            for country in self._destinations_data.keys():
                if location in country or country in location:
                    return {
                        "region_type": "country",
                        "country_name": country.title(),
                        "cities": self._destinations_data[country],
                        "message": f"Here are popular cities and destinations in {country.title()}."
                    }
            
            # Try to find a partial match for regions
            for region in self._countries_by_region.keys():
                if location in region or region in location:
                    return {
                        "region_type": "continent",
                        "region_name": region.title(),
                        "countries": self._countries_by_region[region],
                        "message": f"Here are the countries in {region.title()}. You can ask for cities in any of these countries."
                    }
            
            # Try to find a partial match for united regions
            for region in self._united_regions.keys():
                if location in region or region in location:
                    return {
                        "region_type": "united region",
                        "region_name": region.title(),
                        "countries": self._united_regions[region],
                        "message": f"Here are the countries in the {region.title()} region. You can ask for cities in any of these countries."
                    }
            
            return {
                "error": f"Sorry, I don't have information about cities in '{location}'. Try a different country, continent, or region name like 'Europe', 'USA', 'Southeast Asia', or 'Scandinavia'."
            }

    @override
    async def run_async(
            self, *, args: dict[str, Any], tool_context: ToolContext
    ) -> Any:
        """Runs the destinations tool with the given arguments and context.

        Args:
            args: The LLM-filled arguments. The args should include a "location" key
            tool_context: The context of the tool.

        Returns:
            A dictionary containing cities/destinations or an error message.
        """
        print("Running DestinationsTool with args:", args)

        location = args["location"]
        return await self.list_cities(location=location)