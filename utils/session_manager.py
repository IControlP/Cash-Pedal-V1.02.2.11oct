"""
Enhanced Session State Management with Persistent Settings
Handles both temporary session data and persistent user settings
"""

import streamlit as st
from typing import Dict, Any, Optional, Tuple

def initialize_session_state():
    """Initialize all session state variables with default values"""
    
    # Vehicle comparison data
    if 'comparison_vehicles' not in st.session_state:
        st.session_state.comparison_vehicles = []
    
    if 'comparison_results' not in st.session_state:
        st.session_state.comparison_results = {}
    
    # Current vehicle calculation
    if 'current_vehicle' not in st.session_state:
        st.session_state.current_vehicle = {}
    
    if 'current_results' not in st.session_state:
        st.session_state.current_results = {}
    
    # User preferences and settings
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {
            'comparison_priority': 'cost',
            'max_vehicles': 5,
            'default_years': 5
        }
    
    # ZIP code and location data (legacy - now handled by persistent_settings)
    if 'location_data' not in st.session_state:
        st.session_state.location_data = {
            'zip_code': '',
            'state': '',
            'geography_type': '',
            'fuel_price': 0.0,
            'electricity_rate': 0.0
        }
    
    # Calculation flags
    if 'calculation_complete' not in st.session_state:
        st.session_state.calculation_complete = False
    
    if 'show_comparison' not in st.session_state:
        st.session_state.show_comparison = False
    
    # Form data persistence (legacy - now handled by persistent_settings)
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    # Initialize persistent settings
    initialize_persistent_settings()

def initialize_persistent_settings():
    """Initialize persistent settings that survive between calculations"""
    if 'persistent_settings' not in st.session_state:
        st.session_state.persistent_settings = {
            # Location & Regional Settings
            'location': {
                'zip_code': '',
                'state': '',
                'geography_type': 'Suburban',
                'fuel_price': 3.50,
                'electricity_rate': 0.12,
                'is_set': False
            },
            # Personal Information
            'personal': {
                'user_age': 25,
                'gross_income': 60000,
                'annual_mileage': 12000,
                'driving_style': 'normal',
                'terrain': 'flat',
                'num_household_vehicles': 1,
                'is_set': False
            },
            # Insurance Settings
            'insurance': {
                'coverage_type': 'standard',
                'shop_type': 'independent',
                'is_set': False
            },
            # Analysis Preferences
            'analysis': {
                'comparison_priority': 'cost',
                'default_analysis_years': 5,
                'is_set': False
            }
        }

def clear_session_state():
    """Clear all session state data but preserve persistent settings"""
    keys_to_clear = [
        'comparison_vehicles',
        'comparison_results', 
        'current_vehicle',
        'current_results',
        'location_data',  # Legacy
        'calculation_complete',
        'show_comparison',
        'form_data'  # Legacy
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Reinitialize with defaults (but keep persistent settings)
    initialize_session_state()

def clear_all_data():
    """Clear everything including persistent settings"""
    keys_to_clear = [
        'comparison_vehicles',
        'comparison_results', 
        'current_vehicle',
        'current_results',
        'location_data',
        'calculation_complete',
        'show_comparison',
        'form_data',
        'persistent_settings',  # This will clear saved user settings
        'show_location_form',
        'show_personal_form',
        'show_insurance_form',
        'show_settings_summary'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Reinitialize everything from scratch
    initialize_session_state()

def save_persistent_setting(category: str, data: Dict[str, Any]):
    """Save settings to persistent storage"""
    if 'persistent_settings' not in st.session_state:
        initialize_persistent_settings()
    
    st.session_state.persistent_settings[category].update(data)
    st.session_state.persistent_settings[category]['is_set'] = True

def get_persistent_setting(category: str, key: str = None, default=None):
    """Get persistent settings"""
    if 'persistent_settings' not in st.session_state:
        initialize_persistent_settings()
    
    if key is None:
        return st.session_state.persistent_settings.get(category, {})
    else:
        return st.session_state.persistent_settings.get(category, {}).get(key, default)

def are_persistent_settings_complete() -> bool:
    """Check if all essential persistent settings are configured"""
    location_set = get_persistent_setting('location', 'is_set', False)
    personal_set = get_persistent_setting('personal', 'is_set', False)
    insurance_set = get_persistent_setting('insurance', 'is_set', False)
    
    return location_set and personal_set and insurance_set

def get_persistent_settings_completion() -> Dict[str, bool]:
    """Get completion status of each persistent setting category"""
    return {
        'location': get_persistent_setting('location', 'is_set', False),
        'personal': get_persistent_setting('personal', 'is_set', False),
        'insurance': get_persistent_setting('insurance', 'is_set', False),
        'analysis': get_persistent_setting('analysis', 'is_set', False)
    }

def update_location_data(zip_code: str, state: str = '', geography_type: str = '', 
                        fuel_price: float = 0.0, electricity_rate: float = 0.0):
    """Update location data in session state (legacy support)"""
    # Update legacy location_data for backward compatibility
    st.session_state.location_data.update({
        'zip_code': zip_code,
        'state': state,
        'geography_type': geography_type,
        'fuel_price': fuel_price,
        'electricity_rate': electricity_rate
    })
    
    # Also update persistent settings
    location_data = {
        'zip_code': zip_code,
        'state': state,
        'geography_type': geography_type,
        'fuel_price': fuel_price,
        'electricity_rate': electricity_rate
    }
    save_persistent_setting('location', location_data)

def add_vehicle_to_comparison(vehicle_data: Dict[str, Any], results: Dict[str, Any] = None) -> Tuple[bool, str]:
    """
    Add a vehicle to the comparison list with its calculation results
    
    Args:
        vehicle_data: Dictionary containing vehicle configuration
        results: Dictionary containing calculation results (optional, will use current_results if not provided)
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Get results from parameter or session state
    if results is None:
        if 'current_results' in st.session_state and st.session_state.current_results:
            results = st.session_state.current_results
        else:
            return False, "No calculation results available. Please calculate TCO first."
    
    # Check for duplicates
    make = vehicle_data.get('make', '')
    model = vehicle_data.get('model', '')
    year = vehicle_data.get('year', '')
    trim = vehicle_data.get('trim', '')
    transaction_type = vehicle_data.get('transaction_type', '')
    
    for existing_vehicle in st.session_state.comparison_vehicles:
        # Handle both old format (dict) and new format (dict with 'data' key)
        existing_data = existing_vehicle.get('data', existing_vehicle)
        
        if (existing_data.get('make') == make and
            existing_data.get('model') == model and
            existing_data.get('year') == year and
            existing_data.get('trim') == trim and
            existing_data.get('transaction_type') == transaction_type):
            return False, "This vehicle configuration is already in your comparison."
    
    # Check maximum vehicles limit
    max_vehicles = st.session_state.user_preferences.get('max_vehicles', 5)
    if len(st.session_state.comparison_vehicles) >= max_vehicles:
        return False, f"Maximum of {max_vehicles} vehicles allowed in comparison."
    
    # Create vehicle entry with embedded results (new format)
    vehicle_entry = {
        'data': vehicle_data.copy(),
        'results': results.copy(),
        'name': f"{year} {make} {model} {trim}"
    }
    
    # Add vehicle to comparison list
    st.session_state.comparison_vehicles.append(vehicle_entry)
    
    # Also save to comparison_results for backward compatibility
    vehicle_key = f"{make}_{model}_{year}_{trim}_{transaction_type}"
    st.session_state.comparison_results[vehicle_key] = {
        'vehicle_data': vehicle_data,
        'results': results
    }
    
    return True, f"Vehicle added to comparison. Total: {len(st.session_state.comparison_vehicles)}"

def remove_vehicle_from_comparison(index: int):
    """Remove a vehicle from comparison by index"""
    if 0 <= index < len(st.session_state.comparison_vehicles):
        removed_vehicle = st.session_state.comparison_vehicles.pop(index)
        
        # Handle both old and new format
        vehicle_data = removed_vehicle.get('data', removed_vehicle)
        
        # Clean up associated results from comparison_results dict
        vehicle_key = f"{vehicle_data.get('make')}_{vehicle_data.get('model')}_{vehicle_data.get('year')}_{vehicle_data.get('trim')}_{vehicle_data.get('transaction_type')}"
        if vehicle_key in st.session_state.comparison_results:
            del st.session_state.comparison_results[vehicle_key]
        return True, "Vehicle removed from comparison."
    return False, "Invalid vehicle index."

def get_comparison_vehicle_count():
    """Get the number of vehicles in comparison"""
    return len(st.session_state.comparison_vehicles)

def is_comparison_ready():
    """Check if comparison is ready (has at least 2 vehicles)"""
    return len(st.session_state.comparison_vehicles) >= 2

def save_calculation_results(vehicle_data: Dict[str, Any], results: Dict[str, Any]):
    """Save calculation results for a vehicle"""
    vehicle_key = f"{vehicle_data.get('make')}_{vehicle_data.get('model')}_{vehicle_data.get('year')}_{vehicle_data.get('trim')}_{vehicle_data.get('transaction_type')}"
    st.session_state.comparison_results[vehicle_key] = {
        'vehicle_data': vehicle_data,
        'results': results
    }

def get_calculation_results(vehicle_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get saved calculation results for a vehicle"""
    vehicle_key = f"{vehicle_data.get('make')}_{vehicle_data.get('model')}_{vehicle_data.get('year')}_{vehicle_data.get('trim')}_{vehicle_data.get('transaction_type')}"
    return st.session_state.comparison_results.get(vehicle_key)

def update_user_preferences(preferences: Dict[str, Any]):
    """Update user preferences in session state"""
    st.session_state.user_preferences.update(preferences)

def get_session_stats():
    """Get session statistics for display"""
    completion = get_persistent_settings_completion()
    
    return {
        'vehicles_in_comparison': len(st.session_state.comparison_vehicles),
        'calculations_completed': len(st.session_state.comparison_results),
        'comparison_ready': is_comparison_ready(),
        'current_vehicle_configured': bool(st.session_state.get('current_vehicle')),
        'current_calculation_complete': st.session_state.get('calculation_complete', False),
        'persistent_settings_complete': are_persistent_settings_complete(),
        'settings_completion': completion
    }

def create_vehicle_form_data_with_persistent_settings(vehicle_specific_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create complete form data by combining vehicle-specific data with persistent settings
    
    Args:
        vehicle_specific_data: Dictionary with vehicle-specific fields (make, model, year, etc.)
    
    Returns:
        Complete form data dictionary ready for calculation
    """
    # Start with empty form data
    form_data = {}
    
    # Add location data
    location = get_persistent_setting('location')
    if location.get('is_set', False):
        form_data.update({
            'zip_code': location.get('zip_code', ''),
            'state': location.get('state', ''),
            'geography_type': location.get('geography_type', 'Suburban'),
            'fuel_price': location.get('fuel_price', 3.50),
            'electricity_rate': location.get('electricity_rate', 0.12)
        })
    
    # Add personal data
    personal = get_persistent_setting('personal')
    if personal.get('is_set', False):
        form_data.update({
            'user_age': personal.get('user_age', 35),
            'gross_income': personal.get('gross_income', 60000),
            'annual_mileage': personal.get('annual_mileage', 12000),
            'driving_style': personal.get('driving_style', 'normal'),
            'terrain': personal.get('terrain', 'flat'),
            'num_household_vehicles': personal.get('num_household_vehicles', 2)
        })
    
    # Add insurance data
    insurance = get_persistent_setting('insurance')
    if insurance.get('is_set', False):
        form_data.update({
            'coverage_type': insurance.get('coverage_type', 'standard'),
            'shop_type': insurance.get('shop_type', 'independent')
        })
    
    # Add analysis data
    analysis = get_persistent_setting('analysis')
    if analysis.get('is_set', False):
        form_data.update({
            'comparison_priority': analysis.get('comparison_priority', 'cost'),
            'analysis_years': analysis.get('default_analysis_years', 5)
        })
    
    # Override with vehicle-specific data
    form_data.update(vehicle_specific_data)
    
    # Set validation flag
    form_data['is_valid'] = True
    
    return form_data

def display_persistent_settings_status():
    """Display a compact status of persistent settings"""
    completion = get_persistent_settings_completion()
    
    status_items = []
    if completion['location']:
        zip_code = get_persistent_setting('location', 'zip_code', '')
        status_items.append(f"📍 {zip_code}")
    
    if completion['personal']:
        age = get_persistent_setting('personal', 'user_age', 35)
        income = get_persistent_setting('personal', 'gross_income', 60000)
        status_items.append(f"👤 Age {age}, ${income:,}")
    
    if completion['insurance']:
        coverage = get_persistent_setting('insurance', 'coverage_type', 'standard')
        status_items.append(f"🛡️ {coverage.title()}")
    
    if status_items:
        st.info(f"**Saved Settings:** {' | '.join(status_items)}")
    else:
        st.warning("💡 **Tip:** Save your personal info, location, and insurance settings to speed up future calculations!")

def quick_calculate_with_persistent_settings(vehicle_data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, str]:
    """Quickly create calculation data using persistent settings"""
    
    if not are_persistent_settings_complete():
        missing = []
        completion = get_persistent_settings_completion()
        if not completion['location']:
            missing.append("Location")
        if not completion['personal']:
            missing.append("Personal Info")
        if not completion['insurance']:
            missing.append("Insurance")
        
        return {}, False, f"Please configure: {', '.join(missing)}"
    
    # Create complete form data
    complete_data = create_vehicle_form_data_with_persistent_settings(vehicle_data)
    
    return complete_data, True, "Ready for calculation"