"""
ZIP Code Lookup Utilities
Handles ZIP code validation and auto-population of location data
Updated with comprehensive metropolitan area electricity rates (2025)
"""

import re
from typing import Dict, Optional, List, Any, Tuple

# ========================================================================
# METROPOLITAN AREA ELECTRICITY RATES (2025)
# Based on major utility companies and regional averages
# Format: (zip_start, zip_end, state, metro_name, geography_type, fuel_price, electricity_rate)
# ========================================================================

METRO_AREA_RATES = [
    # NORTHEAST - High rates due to infrastructure costs and imported energy
    (2101, 2299, 'MA', 'Boston Metro', 'Urban', 3.80, 0.27),
    (1701, 1899, 'MA', 'Worcester/Suburbs', 'Suburban', 3.75, 0.26),
    (6001, 6199, 'CT', 'Connecticut', 'Mixed', 3.75, 0.30),  # Highest in continental US
    (2801, 2999, 'RI', 'Providence Metro', 'Urban', 3.75, 0.28),
    (3801, 3999, 'NH', 'New Hampshire', 'Mixed', 3.65, 0.23),
    (4001, 4999, 'ME', 'Maine', 'Mixed', 3.70, 0.16),
    (5001, 5999, 'VT', 'Vermont', 'Rural', 3.70, 0.17),
    
    # NEW YORK - Varies significantly by region
    (10001, 10499, 'NY', 'Manhattan', 'Urban', 3.95, 0.26),
    (10500, 10999, 'NY', 'Bronx/Westchester', 'Urban', 3.90, 0.25),
    (11001, 11999, 'NY', 'Brooklyn/Queens', 'Urban', 3.90, 0.25),
    (12001, 12999, 'NY', 'Albany/Capital Region', 'Suburban', 3.75, 0.19),
    (13001, 13999, 'NY', 'Syracuse/Central NY', 'Suburban', 3.70, 0.18),
    (14001, 14999, 'NY', 'Buffalo/Western NY', 'Suburban', 3.70, 0.17),
    
    # NEW JERSEY - High density, high rates
    (7001, 7999, 'NJ', 'Northern NJ Metro', 'Urban', 3.70, 0.20),
    (8001, 8999, 'NJ', 'Central/Southern NJ', 'Suburban', 3.65, 0.19),
    
    # PENNSYLVANIA - Mix of urban and industrial
    (15001, 15999, 'PA', 'Pittsburgh Metro', 'Urban', 3.65, 0.15),
    (16001, 17999, 'PA', 'Central PA', 'Suburban', 3.60, 0.14),
    (18001, 18999, 'PA', 'Northeast PA', 'Suburban', 3.60, 0.15),
    (19001, 19699, 'PA', 'Philadelphia Metro', 'Urban', 3.65, 0.17),
    
    # DELAWARE & MARYLAND
    (19700, 19999, 'DE', 'Delaware', 'Suburban', 3.45, 0.14),
    (20001, 20599, 'DC', 'Washington DC', 'Urban', 3.60, 0.16),
    (20600, 21999, 'MD', 'Maryland Metro', 'Suburban', 3.55, 0.18),
    
    # VIRGINIA
    (22001, 22999, 'VA', 'Northern Virginia', 'Suburban', 3.50, 0.14),
    (23001, 24699, 'VA', 'Central/Coastal VA', 'Suburban', 3.45, 0.13),
    
    # WEST VIRGINIA
    (24700, 26999, 'WV', 'West Virginia', 'Rural', 3.40, 0.12),
    
    # MIDWEST - Generally moderate rates
    (43001, 43999, 'OH', 'Columbus Metro', 'Urban', 3.40, 0.15),
    (44001, 44999, 'OH', 'Cleveland Metro', 'Urban', 3.45, 0.16),
    (45001, 45999, 'OH', 'Cincinnati/Dayton', 'Urban', 3.40, 0.15),
    (48001, 48999, 'MI', 'Detroit Metro', 'Urban', 3.50, 0.17),
    (49001, 49999, 'MI', 'West/North Michigan', 'Suburban', 3.45, 0.16),
    (60001, 60699, 'IL', 'Chicago Metro', 'Urban', 3.60, 0.16),
    (61001, 62999, 'IL', 'Central/Southern IL', 'Suburban', 3.50, 0.14),
    (46001, 46999, 'IN', 'Indianapolis Metro', 'Urban', 3.35, 0.14),
    (47001, 47999, 'IN', 'Southern Indiana', 'Suburban', 3.30, 0.13),
    (53001, 53999, 'WI', 'Milwaukee/Madison', 'Urban', 3.45, 0.15),
    (54001, 54999, 'WI', 'Northern Wisconsin', 'Rural', 3.40, 0.14),
    (55001, 55999, 'MN', 'Minneapolis-St Paul', 'Urban', 3.45, 0.14),
    (56001, 56799, 'MN', 'Southern Minnesota', 'Rural', 3.40, 0.13),
    (50001, 52999, 'IA', 'Iowa', 'Mixed', 3.25, 0.12),
    (63001, 63999, 'MO', 'St Louis Metro', 'Urban', 3.25, 0.13),
    (64001, 64999, 'MO', 'Kansas City Metro', 'Urban', 3.20, 0.13),
    (65001, 65899, 'MO', 'Central Missouri', 'Suburban', 3.15, 0.12),
    (66001, 67999, 'KS', 'Kansas', 'Mixed', 3.15, 0.14),
    (68001, 69999, 'NE', 'Nebraska', 'Mixed', 3.30, 0.11),
    (57001, 57999, 'SD', 'South Dakota', 'Rural', 3.35, 0.12),
    (58001, 58999, 'ND', 'North Dakota', 'Rural', 3.25, 0.11),
    
    # SOUTH - Generally lower rates except FL
    (40001, 42799, 'KY', 'Kentucky', 'Mixed', 3.30, 0.11),
    (37001, 38599, 'TN', 'Tennessee', 'Mixed', 3.20, 0.12),
    (27001, 28999, 'NC', 'North Carolina', 'Mixed', 3.35, 0.13),
    (29001, 29999, 'SC', 'South Carolina', 'Mixed', 3.25, 0.14),
    (30001, 31999, 'GA', 'Atlanta Metro', 'Urban', 3.30, 0.14),
    (32001, 32999, 'FL', 'Central/North Florida', 'Mixed', 3.40, 0.14),
    (33001, 33999, 'FL', 'South Florida/Miami', 'Urban', 3.45, 0.15),
    (34001, 34999, 'FL', 'Southwest Florida', 'Suburban', 3.35, 0.14),
    (35001, 36999, 'AL', 'Alabama', 'Mixed', 3.20, 0.13),
    (38601, 39999, 'MS', 'Mississippi', 'Mixed', 3.10, 0.12),
    (70001, 71499, 'LA', 'Louisiana', 'Mixed', 3.05, 0.11),
    (71600, 72999, 'AR', 'Arkansas', 'Mixed', 3.10, 0.11),
    (73001, 74999, 'OK', 'Oklahoma', 'Mixed', 3.15, 0.12),
    
    # TEXAS - Deregulated market, varies by city
    (75001, 75499, 'TX', 'Dallas-Fort Worth', 'Urban', 3.25, 0.14),
    (76001, 76999, 'TX', 'Fort Worth/West', 'Urban', 3.20, 0.13),
    (77001, 77599, 'TX', 'Houston Metro', 'Urban', 3.20, 0.13),
    (78001, 78999, 'TX', 'Austin/San Antonio', 'Urban', 3.30, 0.13),
    (79001, 79999, 'TX', 'West Texas', 'Rural', 3.15, 0.12),
    
    # MOUNTAIN WEST
    (59001, 59999, 'MT', 'Montana', 'Rural', 3.60, 0.12),
    (82001, 83199, 'WY', 'Wyoming', 'Rural', 3.50, 0.12),
    (83200, 83999, 'ID', 'Idaho', 'Rural', 3.65, 0.10),
    (80001, 81699, 'CO', 'Colorado', 'Mixed', 3.50, 0.14),
    (87001, 88499, 'NM', 'New Mexico', 'Mixed', 3.40, 0.14),
    (84001, 84799, 'UT', 'Utah', 'Mixed', 3.75, 0.11),
    (85001, 86599, 'AZ', 'Arizona', 'Mixed', 3.85, 0.14),
    (88901, 89999, 'NV', 'Nevada', 'Mixed', 4.05, 0.13),
    
    # PACIFIC NORTHWEST - Low rates due to hydropower
    (98001, 99399, 'WA', 'Western Washington', 'Mixed', 4.20, 0.10),
    (99401, 99499, 'WA', 'Eastern Washington', 'Rural', 4.10, 0.09),
    (97001, 97999, 'OR', 'Oregon', 'Mixed', 4.10, 0.11),
    
    # ALASKA - Highest rates after Hawaii
    (99500, 99999, 'AK', 'Alaska', 'Rural', 4.15, 0.24),
    
    # CALIFORNIA - Highest rates in continental US for major metros
    (90001, 90899, 'CA', 'Los Angeles Metro', 'Urban', 4.70, 0.28),
    (91001, 91899, 'CA', 'LA Suburbs/Valleys', 'Suburban', 4.65, 0.27),
    (92001, 92199, 'CA', 'San Diego Metro', 'Urban', 4.55, 0.38),  # SDG&E - HIGHEST
    (92600, 92899, 'CA', 'Orange County', 'Suburban', 4.65, 0.27),
    (92200, 92599, 'CA', 'Inland Empire', 'Suburban', 4.60, 0.26),
    (93500, 93599, 'CA', 'Inland Empire East', 'Suburban', 4.55, 0.25),
    (93001, 93499, 'CA', 'Central Valley', 'Suburban', 4.50, 0.24),
    (94001, 94999, 'CA', 'San Francisco/Peninsula', 'Urban', 4.85, 0.32),
    (95001, 95199, 'CA', 'San Jose/Silicon Valley', 'Urban', 4.75, 0.30),
    (94500, 94799, 'CA', 'East Bay', 'Suburban', 4.70, 0.30),
    (95200, 95999, 'CA', 'Sacramento/North CA', 'Suburban', 4.60, 0.28),
    (96001, 96199, 'CA', 'Northern CA', 'Rural', 4.55, 0.27),
    
    # HAWAII - Highest rates in nation (imported fuel)
    (96701, 96899, 'HI', 'Hawaii', 'Mixed', 4.95, 0.42),
]

# State-based fuel price averages (fallback when ZIP not in metro database)
STATE_FUEL_PRICES = {
    'AL': 3.20, 'AK': 4.15, 'AZ': 3.85, 'AR': 3.10, 'CA': 4.65, 'CO': 3.50, 'CT': 3.75,
    'DE': 3.45, 'FL': 3.40, 'GA': 3.30, 'HI': 4.95, 'ID': 3.65, 'IL': 3.60, 'IN': 3.35,
    'IA': 3.25, 'KS': 3.15, 'KY': 3.30, 'LA': 3.05, 'ME': 3.70, 'MD': 3.55, 'MA': 3.80,
    'MI': 3.50, 'MN': 3.45, 'MS': 3.10, 'MO': 3.20, 'MT': 3.60, 'NE': 3.30, 'NV': 4.05,
    'NH': 3.65, 'NJ': 3.70, 'NM': 3.40, 'NY': 3.90, 'NC': 3.35, 'ND': 3.25, 'OH': 3.40,
    'OK': 3.15, 'OR': 4.10, 'PA': 3.65, 'RI': 3.75, 'SC': 3.25, 'SD': 3.35, 'TN': 3.20,
    'TX': 3.25, 'UT': 3.75, 'VT': 3.70, 'VA': 3.45, 'WA': 4.20, 'WV': 3.40, 'WI': 3.45,
    'WY': 3.50, 'DC': 3.60
}

# State-based electricity rates (cents per kWh) - Updated 2025
STATE_ELECTRICITY_RATES = {
    'AL': 0.13, 'AK': 0.24, 'AZ': 0.14, 'AR': 0.11, 'CA': 0.33, 'CO': 0.14, 'CT': 0.30,
    'DE': 0.14, 'FL': 0.14, 'GA': 0.14, 'HI': 0.42, 'ID': 0.10, 'IL': 0.16, 'IN': 0.14,
    'IA': 0.12, 'KS': 0.14, 'KY': 0.11, 'LA': 0.11, 'ME': 0.16, 'MD': 0.18, 'MA': 0.27,
    'MI': 0.17, 'MN': 0.14, 'MS': 0.12, 'MO': 0.13, 'MT': 0.12, 'NE': 0.11, 'NV': 0.13,
    'NH': 0.23, 'NJ': 0.20, 'NM': 0.14, 'NY': 0.20, 'NC': 0.13, 'ND': 0.11, 'OH': 0.15,
    'OK': 0.12, 'OR': 0.11, 'PA': 0.17, 'RI': 0.28, 'SC': 0.14, 'SD': 0.12, 'TN': 0.12,
    'TX': 0.13, 'UT': 0.11, 'VT': 0.17, 'VA': 0.13, 'WA': 0.10, 'WV': 0.12, 'WI': 0.15,
    'WY': 0.12, 'DC': 0.16
}

# Comprehensive ZIP code range mapping for state determination
ZIP_CODE_RANGES = {
    'AL': [(35000, 36999)],
    'AK': [(99500, 99999)],
    'AZ': [(85000, 86599)],
    'AR': [(71600, 72999), (75502, 75502)],
    'CA': [(90000, 96199)],
    'CO': [(80000, 81699)],
    'CT': [(6000, 6999)],
    'DE': [(19700, 19999)],
    'DC': [(20000, 20599)],
    'FL': [(32000, 34999)],
    'GA': [(30000, 31999), (39800, 39999)],
    'HI': [(96700, 96899)],
    'ID': [(83200, 83999)],
    'IL': [(60000, 62999)],
    'IN': [(46000, 47999)],
    'IA': [(50000, 52999)],
    'KS': [(66000, 67999)],
    'KY': [(40000, 42799)],
    'LA': [(70000, 71499)],
    'ME': [(3900, 4999)],
    'MD': [(20600, 21999)],
    'MA': [(1000, 2799), (5501, 5599)],
    'MI': [(48000, 49999)],
    'MN': [(55000, 56799)],
    'MS': [(38600, 39999)],
    'MO': [(63000, 65899)],
    'MT': [(59000, 59999)],
    'NE': [(68000, 69999)],
    'NV': [(88900, 89999)],
    'NH': [(3000, 3899)],
    'NJ': [(7000, 8999)],
    'NM': [(87000, 88499)],
    'NY': [(10000, 14999), (6390, 6390)],
    'NC': [(27000, 28999)],
    'ND': [(58000, 58999)],
    'OH': [(43000, 45999)],
    'OK': [(73000, 74999)],
    'OR': [(97000, 97999)],
    'PA': [(15000, 19699)],
    'RI': [(2800, 2999)],
    'SC': [(29000, 29999)],
    'SD': [(57000, 57999)],
    'TN': [(37000, 38599)],
    'TX': [(73301, 73301), (75000, 79999), (88500, 88599)],
    'UT': [(84000, 84799)],
    'VT': [(5000, 5999)],
    'VA': [(20100, 20199), (22000, 24699)],
    'WA': [(98000, 99499)],
    'WV': [(24700, 26999)],
    'WI': [(53000, 54999)],
    'WY': [(82000, 83199)]
}

def validate_zip_code(zip_code: str) -> bool:
    """Validate ZIP code format (5 digits)"""
    if not zip_code:
        return False
    zip_pattern = re.compile(r'^\d{5}$')
    return bool(zip_pattern.match(str(zip_code)))

def lookup_zip_code_data(zip_code: str) -> Optional[Dict[str, Any]]:
    """
    Look up location data for a ZIP code using metropolitan area ranges
    Returns dict with state, geography_type, fuel_price, electricity_rate
    """
    if not validate_zip_code(zip_code):
        return None
    
    zip_int = int(zip_code)
    
    # Search through metropolitan area ranges
    for zip_start, zip_end, state, metro_name, geography_type, fuel_price, electricity_rate in METRO_AREA_RATES:
        if zip_start <= zip_int <= zip_end:
            return {
                'state': state,
                'metro_area': metro_name,
                'geography_type': geography_type,
                'fuel_price': fuel_price,
                'electricity_rate': electricity_rate
            }
    
    return None

def determine_state_from_zip(zip_code: str) -> Optional[str]:
    """Determine state from ZIP code using comprehensive ranges"""
    if not validate_zip_code(zip_code):
        return None
    
    zip_int = int(zip_code)
    
    for state, ranges in ZIP_CODE_RANGES.items():
        for start, end in ranges:
            if start <= zip_int <= end:
                return state
    
    return None

def get_state_from_zip(zip_code: str) -> Optional[str]:
    """Alias for determine_state_from_zip for backwards compatibility"""
    return determine_state_from_zip(zip_code)

def get_geography_type_from_zip(zip_code: str) -> str:
    """Determine geography type from ZIP code"""
    if not validate_zip_code(zip_code):
        return 'Suburban'
    
    # First try metro area lookup
    zip_data = lookup_zip_code_data(zip_code)
    if zip_data:
        geo_type = zip_data.get('geography_type', 'Suburban')
        # Convert "Mixed" to "Suburban" for consistency
        return 'Suburban' if geo_type == 'Mixed' else geo_type
    
    # Fallback to basic classification
    zip_int = int(zip_code)
    
    # Major urban centers
    urban_zip_ranges = [
        (10001, 10299), (11201, 11299), (11101, 11199),  # NYC
        (90001, 90099), (90201, 90299), (91401, 91499),  # LA
        (60601, 60661), (60007, 60199),  # Chicago
        (77001, 77099), (77201, 77299),  # Houston
        (85001, 85099), (85201, 85299),  # Phoenix
        (19101, 19199), (19201, 19299),  # Philadelphia
        (78201, 78299),  # San Antonio
        (92101, 92199),  # San Diego
        (75201, 75299),  # Dallas
        (95101, 95199), (94301, 94399),  # San Jose/Silicon Valley
        (78701, 78799),  # Austin
        (32201, 32299),  # Jacksonville
        (94102, 94199),  # San Francisco
        (43201, 43299),  # Columbus
        (28201, 28299),  # Charlotte
        (76101, 76199),  # Fort Worth
        (46201, 46299),  # Indianapolis
        (98101, 98199),  # Seattle
        (80201, 80299),  # Denver
        (20001, 20099),  # Washington DC
        (2101, 2199), (2201, 2299),  # Boston
        (79901, 79999),  # El Paso
        (48201, 48299),  # Detroit
        (37201, 37299),  # Nashville
        (97201, 97299),  # Portland
        (38101, 38199),  # Memphis
        (73101, 73199),  # Oklahoma City
        (89101, 89199),  # Las Vegas
        (40201, 40299),  # Louisville
        (21201, 21299),  # Baltimore
        (53201, 53299),  # Milwaukee
        (87101, 87199),  # Albuquerque
        (85701, 85799),  # Tucson
        (93701, 93799),  # Fresno
        (95801, 95899),  # Sacramento
        (64101, 64199),  # Kansas City
        (30301, 30399),  # Atlanta
        (80901, 80999),  # Colorado Springs
        (68101, 68199),  # Omaha
        (27601, 27699),  # Raleigh
        (33101, 33199),  # Miami
        (44101, 44199),  # Cleveland
        (74101, 74199),  # Tulsa
        (55401, 55499),  # Minneapolis
        (67201, 67299),  # Wichita
        (70112, 70199)   # New Orleans
    ]
    
    for start, end in urban_zip_ranges:
        if start <= zip_int <= end:
            return 'Urban'
    
    # Rural indicators - very low population density areas
    rural_zip_patterns = [
        (99501, 99999),  # Alaska rural areas
        (59001, 59099),  # Montana rural
        (82001, 82999),  # Wyoming rural
        (58001, 58099),  # North Dakota rural
        (57001, 57099),  # South Dakota rural
        (89001, 89099),  # Nevada rural
        (83001, 83199),  # Idaho rural
        (5001, 5099),    # Vermont rural
        (4001, 4199),    # Maine rural
        (24701, 25999)   # West Virginia rural
    ]
    
    for start, end in rural_zip_patterns:
        if start <= zip_int <= end:
            return 'Rural'
    
    # Default to suburban for most ZIP codes
    return 'Suburban'

def get_fuel_price_estimate(zip_code: str, state: str = '') -> float:
    """Get estimated fuel price for location"""
    # Try ZIP code lookup first
    zip_data = lookup_zip_code_data(zip_code)
    if zip_data:
        return zip_data.get('fuel_price', 3.50)
    
    # Fall back to state average
    if state in STATE_FUEL_PRICES:
        return STATE_FUEL_PRICES[state]
    
    # National average fallback
    return 3.50

def get_electricity_rate_estimate(zip_code: str, state: str = '') -> float:
    """Get estimated electricity rate for location"""
    # Try ZIP code lookup first
    zip_data = lookup_zip_code_data(zip_code)
    if zip_data:
        return zip_data.get('electricity_rate', 0.15)
    
    # Fall back to state average
    if state in STATE_ELECTRICITY_RATES:
        return STATE_ELECTRICITY_RATES[state]
    
    # National average fallback
    return 0.15

def validate_and_lookup_location(zip_code: str) -> Dict[str, Any]:
    """Comprehensive location validation and lookup"""
    result = {
        'is_valid': False,
        'zip_code': zip_code,
        'state': '',
        'metro_area': '',
        'geography_type': '',
        'fuel_price': 3.50,
        'electricity_rate': 0.15,
        'error_message': ''
    }
    
    # Validate format
    if not validate_zip_code(zip_code):
        result['error_message'] = 'Invalid ZIP code format. Please enter 5 digits.'
        return result
    
    # Try metro area lookup first
    zip_data = lookup_zip_code_data(zip_code)
    
    if zip_data:
        result['is_valid'] = True
        result['state'] = zip_data['state']
        result['metro_area'] = zip_data.get('metro_area', '')
        geo_type = zip_data['geography_type']
        # Convert "Mixed" to "Suburban" for consistency with existing code
        result['geography_type'] = 'Suburban' if geo_type == 'Mixed' else geo_type
        result['fuel_price'] = zip_data['fuel_price']
        result['electricity_rate'] = zip_data['electricity_rate']
    else:
        # Fall back to state lookup
        state = determine_state_from_zip(zip_code)
        if state:
            result['is_valid'] = True
            result['state'] = state
            result['geography_type'] = get_geography_type_from_zip(zip_code)
            result['fuel_price'] = STATE_FUEL_PRICES.get(state, 3.50)
            result['electricity_rate'] = STATE_ELECTRICITY_RATES.get(state, 0.15)
            result['error_message'] = 'ZIP code recognized but detailed data unavailable. Using state averages.'
        else:
            result['error_message'] = f'ZIP code {zip_code} not found in database.'
    
    return result

def get_regional_cost_multiplier(geography_type: str, state: str = '') -> float:
    """
    Get cost multiplier based on geography type and state
    Used for adjusting maintenance and other costs by region
    """
    base_multipliers = {
        'Urban': 1.15,
        'Suburban': 1.0,
        'Rural': 0.85,
        'Mixed': 1.0  # Added for new metro areas
    }
    
    # High-cost states get additional multiplier
    high_cost_states = ['CA', 'NY', 'MA', 'CT', 'HI', 'AK', 'NJ']
    low_cost_states = ['MS', 'AL', 'AR', 'WV', 'OK', 'KS', 'ND', 'SD']
    
    multiplier = base_multipliers.get(geography_type, 1.0)
    
    if state in high_cost_states:
        multiplier *= 1.10
    elif state in low_cost_states:
        multiplier *= 0.90
    
    return multiplier

def get_zip_code_coverage_stats() -> Dict[str, Any]:
    """Get statistics about ZIP code coverage"""
    total_metros = len(METRO_AREA_RATES)
    states_covered = len(set([metro[2] for metro in METRO_AREA_RATES]))
    
    # Count by geography type
    geography_counts = {}
    for metro in METRO_AREA_RATES:
        geo_type = metro[4]
        geography_counts[geo_type.lower()] = geography_counts.get(geo_type.lower(), 0) + 1
    
    return {
        'total_metro_areas': total_metros,
        'states_covered': states_covered,
        'coverage_by_geography': geography_counts,
        'states_list': sorted(STATE_ELECTRICITY_RATES.keys())
    }

def search_nearby_zip_codes(zip_code: str, radius: int = 10) -> List[Dict[str, Any]]:
    """Search for nearby ZIP codes with data (uses metro area ranges)"""
    if not validate_zip_code(zip_code):
        return []
    
    zip_int = int(zip_code)
    nearby_zips = []
    
    # Search within radius for ZIP codes in metro ranges
    for test_zip in range(max(10000, zip_int - radius), min(99999, zip_int + radius + 1)):
        test_zip_str = f"{test_zip:05d}"
        data = lookup_zip_code_data(test_zip_str)
        if data:
            data['zip_code'] = test_zip_str
            data['distance'] = abs(test_zip - zip_int)
            nearby_zips.append(data)
    
    # Sort by distance and remove duplicates
    seen_metros = set()
    unique_zips = []
    for item in sorted(nearby_zips, key=lambda x: x['distance']):
        metro_key = (item['state'], item.get('metro_area', ''))
        if metro_key not in seen_metros:
            seen_metros.add(metro_key)
            unique_zips.append(item)
    
    return unique_zips[:5]  # Return top 5 results

# Test function
def test_zip_code_lookup():
    """Test ZIP code lookup functionality with comprehensive examples"""
    test_zips = [
        '92009',  # San Diego (Carlsbad) - highest CA rate
        '02138',  # Cambridge, MA
        '10001',  # Manhattan, NY
        '60601',  # Chicago, IL
        '90210',  # Beverly Hills, CA
        '94102',  # San Francisco, CA
        '33101',  # Miami, FL
        '30301',  # Atlanta, GA
        '98101',  # Seattle, WA
        '78701',  # Austin, TX
        '80201',  # Denver, CO
        '75201',  # Dallas, TX
        '19101',  # Philadelphia, PA
        '85001',  # Phoenix, AZ
    ]
    
    print("Comprehensive Metropolitan Area ZIP Code Lookup Test:")
    print("=" * 70)
    
    for zip_code in test_zips:
        result = validate_and_lookup_location(zip_code)
        print(f"\nZIP: {zip_code}")
        print(f"  Valid: {result['is_valid']}")
        print(f"  Metro Area: {result['metro_area']}")
        print(f"  State: {result['state']}")
        print(f"  Geography: {result['geography_type']}")
        print(f"  Fuel Price: ${result['fuel_price']:.2f}")
        print(f"  Electricity: ${result['electricity_rate']:.3f}/kWh")
        if result['error_message']:
            print(f"  Message: {result['error_message']}")
        
        # Test regional multiplier
        multiplier = get_regional_cost_multiplier(result['geography_type'], result['state'])
        print(f"  Cost Multiplier: {multiplier:.2f}x")
    
    print("\n" + "=" * 70)
    
    # Display coverage statistics
    coverage = get_zip_code_coverage_stats()
    print(f"\nDatabase Coverage Statistics:")
    print(f"Total Metro Areas: {coverage['total_metro_areas']}")
    print(f"States covered: {coverage['states_covered']}/51 (includes DC)")
    print(f"Coverage by geography:")
    for geo_type, count in coverage['coverage_by_geography'].items():
        print(f"  {geo_type.title()}: {count} metro areas")
    print(f"\nAll states covered: {', '.join(coverage['states_list'][:20])}...")

if __name__ == "__main__":
    test_zip_code_lookup()