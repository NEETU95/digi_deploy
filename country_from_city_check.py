import pycountry
from langchain.document_loaders import PubMedLoader
def get_country_by_state(state_name):
    for subdivision in pycountry.subdivisions:
        # Check if the state name is a substring of the subdivision name
        if state_name.lower() in subdivision.name.lower():
            # Get the country using the alpha-2 code of the subdivision
            country = pycountry.countries.get(alpha_2=subdivision.country_code)
            return country.name

    return None

# Example: List of state names
state_names = ["Jerusalem", "New York", "Lima"]

for state_name in state_names:
    country_name = get_country_by_state(state_name)
    if country_name:
        print(f"{state_name} is in {country_name}")
    else:
        print(f"Country for {state_name} not found.")



import geograpy

# Example city names
cities = ["Lima", "Jerusalem"]

# Create a PlaceContext with the city names
places = geograpy.get_place_context(cities=cities)

# Access information about the places (countries) corresponding to the cities
for city, country in zip(cities, places.cities):
    print(f"{city} is in {country}")