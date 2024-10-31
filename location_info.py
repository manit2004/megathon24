import requests
from math import radians, sin, cos, sqrt, atan2

def get_location_info(latitude, longitude, radius_meters=1000):
    """
    Get detailed information about places near a specific location.
    
    Args:
        latitude (float): Latitude of the location
        longitude (float): Longitude of the location
        radius_meters (int): Search radius in meters (default: 1000)
    
    Returns:
        dict: Dictionary containing categorized nearby places and statistics
    """
    # Overpass API endpoint
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Define categories and their corresponding amenities
    categories = {
        'healthcare': ['hospital', 'clinic', 'doctors', 'dentist', 'pharmacy'],
        'education': ['school', 'university', 'college', 'library'],
        'emergency': ['fire_station', 'police', 'ambulance_station'],
        'transportation': ['bus_station', 'train_station', 'subway_entrance'],
        'services': ['bank', 'post_office', 'atm', 'marketplace']
    }
    
    # Build the query for all amenities
    query_parts = []
    for category, amenities in categories.items():
        for amenity in amenities:
            query_parts.append(
                f'node["amenity"="{amenity}"](around:{radius_meters},{latitude},{longitude});'
                f'way["amenity"="{amenity}"](around:{radius_meters},{latitude},{longitude});'
            )
    
    overpass_query = f"""
    [out:json][timeout:25];
    (
        {"".join(query_parts)}
    );
    out body;
    >;
    out skel qt;
    """
    
    try:
        # Make the API request
        response = requests.post(overpass_url, data={"data": overpass_query})
        response.raise_for_status()
        data = response.json()
        
        # Initialize results dictionary
        results = {
            'summary': {
                'total_places': 0,
                'categories_found': set()
            },
            'places': {}
        }
        
        # Process each place
        for element in data.get('elements', []):
            if 'tags' in element:
                amenity = element['tags'].get('amenity')
                if not amenity:
                    continue
                
                # Find which category this amenity belongs to
                category = next(
                    (cat for cat, amenities in categories.items() if amenity in amenities),
                    'other'
                )
                
                # Calculate distance if coordinates are available
                distance = None
                if 'lat' in element and 'lon' in element:
                    distance = calculate_distance(
                        latitude, longitude,
                        element['lat'], element['lon']
                    )
                
                # Create place info dictionary
                place_info = {
                    'name': element['tags'].get('name', 'Unnamed'),
                    'type': amenity,
                    'distance_meters': round(distance) if distance else None,
                    'coordinates': {
                        'lat': element.get('lat'),
                        'lon': element.get('lon')
                    },
                    'contact': {
                        'phone': element['tags'].get('phone'),
                        'website': element['tags'].get('website')
                    },
                    'address': {
                        'street': element['tags'].get('addr:street'),
                        'housenumber': element['tags'].get('addr:housenumber'),
                        'postcode': element['tags'].get('addr:postcode'),
                        'city': element['tags'].get('addr:city')
                    },
                    'opening_hours': element['tags'].get('opening_hours'),
                    'operator': element['tags'].get('operator')
                }
                
                # Add to results
                if category not in results['places']:
                    results['places'][category] = []
                results['places'][category].append(place_info)
                
                # Update summary
                results['summary']['total_places'] += 1
                results['summary']['categories_found'].add(category)
        
        # Sort places in each category by distance
        for category in results['places']:
            results['places'][category].sort(
                key=lambda x: x['distance_meters'] if x['distance_meters'] is not None else float('inf')
            )
        
        # Convert summary categories set to list
        results['summary']['categories_found'] = list(results['summary']['categories_found'])
        
        # Add radius information
        results['summary']['search_radius_meters'] = radius_meters
        results['summary']['center_coordinates'] = {
            'latitude': latitude,
            'longitude': longitude
        }
        
        return results
    
    except requests.exceptions.RequestException as e:
        return {
            'error': str(e),
            'status': 'failed'
        }

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the distance between two points using the Haversine formula."""
    R = 6371000  # Earth's radius in meters
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

# Example usage
if __name__ == "__main__":
    # Example coordinates (New York City - Times Square)
    lat = 40.7580
    lon = -73.9855
    
    # Get location information
    info = get_location_info(lat, lon)
    
    # Print summary
    print("\nLocation Information Summary:")
    print(f"Total places found: {info['summary']['total_places']}")
    print(f"Categories found: {', '.join(info['summary']['categories_found'])}")
    
    # Print detailed information for each category
    for category, places in info['places'].items():
        print(f"\n{category.upper()} ({len(places)} places found):")
        for place in places[:3]:  # Show top 3 closest places in each category
            print(f"\n- {place['name']}")
            if place['distance_meters']:
                print(f"  Distance: {place['distance_meters']}m")
            if place['address']['street']:
                print(f"  Address: {place['address']['street']} {place['address']['housenumber']}")
            if place['contact']['phone']:
                print(f"  Phone: {place['contact']['phone']}")