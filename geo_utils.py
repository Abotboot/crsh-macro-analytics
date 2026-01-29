"""
Geographic utilities for user location tracking
Uses free IP geolocation API
"""
import requests
from typing import Optional, Dict

def get_location_from_ip(ip_address: str) -> Optional[Dict[str, any]]:
    """
    Get geographic location from IP address using free API
    
    Returns dict with: country, city, latitude, longitude
    """
    if not ip_address or ip_address in ['127.0.0.1', 'localhost', '::1']:
        return None
    
    try:
        # Using ip-api.com - free, no key required, 45 requests/minute
        response = requests.get(
            f"http://ip-api.com/json/{ip_address}",
            timeout=3
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                return {
                    'country': data.get('countryCode'),
                    'city': data.get('city'),
                    'latitude': data.get('lat'),
                    'longitude': data.get('lon')
                }
    except Exception as e:
        print(f"Error getting location: {e}")
    
    return None
