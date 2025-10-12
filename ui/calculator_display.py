"""
Enhanced Calculator Display with ALL Requested Features + Detailed Maintenance Breakdown + MPG Display
- ZIP code-based fuel/electricity pricing
- EV detection and charging style selection
- Maintenance duplicate removal and validation
- Specification-compliant variable names
- Comprehensive error handling and fallback modes
- Detailed maintenance schedule breakdown from calculator_display_10AUG.py
- Vehicle MPG database integration and UI display
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List
import pandas as pd

# Import with fallback handling
try:
    from ui.input_forms import collect_all_form_data, display_all_forms_visible
    from services.prediction_service import PredictionService
    from utils.session_manager import add_vehicle_to_comparison, save_calculation_results
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    SERVICES_AVAILABLE = False

# Import MPG database functions
try:
    from data.vehicle_mpg_database import (
        get_vehicle_mpg, 
        get_mpg_display_text, 
        get_fuel_efficiency_rating,
        compare_mpg_to_class_average,
        estimate_annual_fuel_cost
    )
    MPG_DATABASE_AVAILABLE = True
except ImportError:
    MPG_DATABASE_AVAILABLE = False

def detect_electric_vehicle(make: str, model: str) -> bool:
    """Detect if make/model is an electric vehicle - FIXED for Audi"""
    model_lower = model.lower()
    make_lower = make.lower()
    
    # Tesla is always electric
    if make_lower == 'tesla':
        return True
    
    # Comprehensive EV model detection - EXACT matches to avoid false positives
    ev_models = [
        # Nissan
        'leaf', 'ariya',
        # Tesla
        'model 3', 'model s', 'model x', 'model y', 'cybertruck',
        # Chevrolet/GM
        'bolt ev', 'bolt euv', 'equinox ev', 'blazer ev', 'silverado ev',
        # Hyundai/Kia
        'ioniq electric', 'ioniq 5', 'ioniq 6', 'kona electric', 
        'niro ev', 'soul ev', 'ev6', 'ev9',
        # BMW - ONLY electric i-series
        'i3', 'i4', 'i5', 'i7', 'ix', 'ix1', 'ix3', 'ixm60',
        # Audi - ONLY e-tron models (NOT regular A4, A6, etc.)
        'e-tron gt', 'q4 e-tron', 'q5 e-tron', 'q6 e-tron', 'q8 e-tron',
        # Porsche
        'taycan',
        # Volkswagen
        'id.3', 'id.4', 'id.5', 'id.7', 'id.buzz',
        # Ford
        'mustang mach-e', 'mach-e', 'f-150 lightning', ' lightning ', 'e-transit',
        # Mercedes
        'eqb', 'eqc', 'eqe', 'eqs', 'eqv',
        # Volvo
        'c40 recharge', 'xc40 recharge',
        # Other
        'polestar', 'lucid air', 'rivian', 'i-pace', 'mini electric', 'cooper se',
        'lyriq', 'hummer ev', 'prologue', 'zdx', 'bz4x', 'solterra', 'mx-30'
    ]
    
    # Check for exact EV model matches
    for ev_model in ev_models:
        if ev_model in model_lower:
            # SPECIAL CHECK: For 'e-tron', make sure it's actually an e-tron model
            if ev_model == 'e-tron' or 'e-tron' in ev_model:
                # Only mark as electric if model contains 'e-tron' with space/hyphen
                # This prevents matching 'electron' or random 'e' + 'tron' patterns
                if 'e-tron' in model_lower or 'etron' in model_lower:
                    return True
            else:
                return True
    
    # Check for generic EV keywords - but be specific
    # Only match if these appear as distinct words, not as part of other words
    if ' ev ' in f' {model_lower} ':  # Surrounded by spaces
        return True
    if model_lower.endswith(' ev'):  # Ends with EV
        return True
    if model_lower.startswith('ev '):  # Starts with EV  
        return True
    
    # BEV (Battery Electric Vehicle) indicator
    if ' bev' in model_lower or model_lower.endswith('bev'):
        return True
    
    return False

def get_vehicle_energy_type(make: str, model: str) -> str:
    """Determine vehicle energy type (gas, electric, hybrid)"""
    model_lower = model.lower()
    
    if detect_electric_vehicle(make, model):
        return 'electric'
    
    # Check for hybrid
    hybrid_keywords = ['hybrid', 'prius', 'insight', 'accord hybrid', 'camry hybrid']
    if any(keyword in model_lower for keyword in hybrid_keywords):
        return 'hybrid'
    
    return 'gasoline'

def display_vehicle_mpg_info(make: str, model: str, year: int, trim: str = None,
                            annual_mileage: int = None, fuel_price: float = None,
                            electricity_rate: float = None, charging_preference: str = None,
                            driving_style: str = None, terrain: str = None):
    """
    Display comprehensive MPG information for the selected vehicle
    
    Args:
        make: Vehicle make
        model: Vehicle model
        year: Vehicle year
        trim: Vehicle trim (optional)
        annual_mileage: Annual miles driven (optional - if None, don't show fuel costs)
        fuel_price: Price per gallon for gas vehicles (optional)
        electricity_rate: Base electricity rate for EVs (optional)
        charging_preference: EV charging pattern (optional)
        driving_style: 'gentle', 'normal', or 'aggressive' (optional)
        terrain: 'flat' or 'hilly' (optional)
    """
    
    if not MPG_DATABASE_AVAILABLE:
        st.info("💡 MPG database not available - using estimates")
        return
    
    # Get MPG data
    mpg_data = get_vehicle_mpg(make, model, year, trim)
    
    if mpg_data:
        # Create MPG display section
        st.markdown("---")
        st.subheader("⛽ Fuel Economy Information")
        
        # Main MPG display
        col1, col2, col3 = st.columns(3)
        
        with col1:
            display_text = get_mpg_display_text(mpg_data)
            st.metric("Fuel Economy", display_text)
        
        with col2:
            efficiency_rating = get_fuel_efficiency_rating(mpg_data)
            rating_color = {
                "Excellent": "🟢",
                "Good": "🟡", 
                "Fair": "🟠",
                "Poor": "🔴"
            }
            st.metric("Efficiency Rating", f"{rating_color.get(efficiency_rating, '⚪')} {efficiency_rating}")
        
        with col3:
            data_source = mpg_data.get('source', 'unknown')
            source_labels = {
                'database': 'EPA Data',
                'database_trim_specific': 'EPA (Trim Specific)',
                'database_default_trim': 'EPA (Model Average)',
                'estimated': 'Estimated'
            }
            st.metric("Data Source", source_labels.get(data_source, 'Estimated'))
        
        # Detailed breakdown for non-electric vehicles
        if not mpg_data.get('is_electric', False):
            with st.expander("📊 Detailed MPG Breakdown"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("City MPG", f"{mpg_data.get('city', 0)}")
                with col2:
                    st.metric("Highway MPG", f"{mpg_data.get('highway', 0)}")
                with col3:
                    st.metric("Combined MPG", f"{mpg_data.get('combined', 0)}")
        
        # Class comparison
        comparison = compare_mpg_to_class_average(mpg_data, make, model)
        
        if comparison:
            with st.expander("🎯 Class Comparison"):
                st.write(f"**Vehicle Class:** {comparison['class_name']}")
                st.write(f"**Class Average:** {comparison['class_average']} {'MPGe' if mpg_data.get('is_electric') else 'MPG'}")
                
                if comparison['comparison'] == 'above':
                    st.success(f"✅ This vehicle is {comparison['difference']:.1f} {'MPGe' if mpg_data.get('is_electric') else 'MPG'} **above** the class average!")
                else:
                    st.warning(f"⚠️ This vehicle is {comparison['difference']:.1f} {'MPGe' if mpg_data.get('is_electric') else 'MPG'} **below** the class average.")
        
        if annual_mileage is not None and fuel_price is not None and electricity_rate is not None:
            st.markdown("---")
            display_fuel_cost_estimate(
                mpg_data=mpg_data,
                annual_mileage=annual_mileage,
                fuel_price=fuel_price,
                electricity_rate=electricity_rate,
                charging_preference=charging_preference or 'mixed',
                driving_style=driving_style or 'normal',
                terrain=terrain or 'flat'
            )
        
        return mpg_data
    
    return None

def display_fuel_cost_estimate(mpg_data: Dict[str, Any], annual_mileage: int, fuel_price: float, 
                              electricity_rate: float = 0.12, charging_preference: str = 'mixed',
                              driving_style: str = 'normal', terrain: str = 'flat'):
    """
    Display estimated annual fuel costs based on MPG data with driving adjustments
    
    Args:
        mpg_data: Vehicle MPG/MPGe data dictionary
        annual_mileage: Annual miles driven
        fuel_price: Price per gallon for gas vehicles
        electricity_rate: Base home electricity rate for EVs
        charging_preference: EV charging pattern (home_primary/mixed/public_heavy)
        driving_style: 'gentle', 'normal', or 'aggressive'
        terrain: 'flat' or 'hilly'
    """
    
    if not mpg_data:
        return
    
    # Calculate annual cost with driving adjustments
    annual_cost = estimate_annual_fuel_cost(mpg_data, annual_mileage, fuel_price, 
                                           electricity_rate, charging_preference,
                                           driving_style, terrain)
    monthly_cost = annual_cost / 12
    cost_per_mile = annual_cost / annual_mileage if annual_mileage > 0 else 0
    
    st.markdown("#### 💰 Estimated Fuel Costs")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Annual Cost", f"${annual_cost:.0f}")
    
    with col2:
        st.metric("Monthly Cost", f"${monthly_cost:.0f}")
    
    with col3:
        st.metric("Cost per Mile", f"${cost_per_mile:.3f}")
    
    # Calculate efficiency adjustments for display
    driving_style_multipliers = {
        'gentle': 1.15,
        'normal': 1.0,
        'aggressive': 0.85
    }
    terrain_multipliers = {
        'flat': 1.05,
        'hilly': 0.95
    }
    
    style_multiplier = driving_style_multipliers.get(driving_style, 1.0)
    terrain_multiplier = terrain_multipliers.get(terrain, 1.0)
    combined_multiplier = style_multiplier * terrain_multiplier
    
    # Show calculation details with adjustments
    if mpg_data.get('is_electric'):
        mpge = mpg_data.get('mpge_combined', 120)
        adjusted_mpge = mpge * combined_multiplier
        kwh_per_mile = 33.7 / adjusted_mpge if adjusted_mpge > 0 else 0.28
        kwh_per_100mi = kwh_per_mile * 100
        
        # Show charging preference impact
        charging_labels = {
            'home_primary': 'Home Primary (80% home)',
            'mixed': 'Mixed Charging (60% home)',
            'public_heavy': 'Public Heavy (40% home)'
        }
        charging_label = charging_labels.get(charging_preference, 'Mixed')
        
        # Show adjustment impact
        adjustment_text = ""
        if driving_style != 'normal' or terrain != 'flat':
            adjustment_pct = (combined_multiplier - 1.0) * 100
            adjustment_text = f" • {adjustment_pct:+.0f}% for {driving_style} driving on {terrain} terrain"
        
        st.info(f"⚡ **Electric Vehicle**: {mpge} MPGe base → {adjusted_mpge:.0f} MPGe adjusted • "
                f"{kwh_per_100mi:.1f} kWh/100mi • ${electricity_rate:.3f}/kWh base rate • "
                f"{charging_label}{adjustment_text}")
    else:
        combined_mpg = mpg_data.get('combined', 25)
        adjusted_mpg = combined_mpg * combined_multiplier
        annual_gallons = annual_mileage / adjusted_mpg if adjusted_mpg > 0 else 0
        
        # Show adjustment impact
        adjustment_text = ""
        if driving_style != 'normal' or terrain != 'flat':
            adjustment_pct = (combined_multiplier - 1.0) * 100
            adjustment_text = f" • {adjustment_pct:+.0f}% for {driving_style} driving on {terrain} terrain"
        
        st.info(f"⛽ **Gasoline Vehicle**: {combined_mpg} MPG base → {adjusted_mpg:.1f} MPG adjusted • "
                f"{annual_gallons:.0f} gallons/year • ${fuel_price:.2f}/gallon{adjustment_text}")
    
    return {
        'annual_cost': annual_cost,
        'monthly_cost': monthly_cost,
        'cost_per_mile': cost_per_mile
    }

def get_vehicle_energy_type(make: str, model: str) -> str:
    """Determine vehicle energy type (gas, electric, hybrid)"""
    model_lower = model.lower()
    
    if detect_electric_vehicle(make, model):
        return 'electric'
    
    # Check for hybrid
    hybrid_keywords = ['hybrid', 'prius', 'insight', 'accord hybrid', 'camry hybrid']
    if any(keyword in model_lower for keyword in hybrid_keywords):
        return 'hybrid'
    
    return 'gasoline'

def get_fuel_price_from_location(zip_code: str = None, state: str = None) -> float:
    """Get fuel price from ZIP code or state with regular/premium distinction"""
    # Base regular gas prices by state (current 2025 averages)
    state_regular_prices = {
        'CA': 4.65, 'TX': 3.25, 'FL': 3.40, 'NY': 3.85, 'IL': 3.60,
        'PA': 3.65, 'OH': 3.35, 'GA': 3.25, 'NC': 3.35, 'MI': 3.50,
        'WA': 4.20, 'OR': 4.10, 'NV': 4.05, 'AZ': 3.85, 'CO': 3.50,
        'MA': 3.75, 'TN': 3.30, 'IN': 3.45, 'MO': 3.35, 'WI': 3.55,
        'MN': 3.45, 'AL': 3.20, 'SC': 3.30, 'KY': 3.35, 'LA': 3.15
    }
    
    # ZIP code to state mapping for major metros (optional enhancement)
    zip_to_state = {
        '90210': 'CA', '10001': 'NY', '60601': 'IL', '77001': 'TX', '33101': 'FL',
        '98101': 'WA', '97201': 'OR', '80201': 'CO', '30301': 'GA', '48201': 'MI',
        '02101': 'MA', '37201': 'TN', '46201': 'IN', '63101': 'MO', '53201': 'WI',
        '55401': 'MN', '35201': 'AL', '29201': 'SC', '40201': 'KY', '70112': 'LA'
    }
    
    # Determine state from ZIP code if provided
    if zip_code and len(zip_code) == 5 and zip_code.isdigit():
        inferred_state = zip_to_state.get(zip_code, state)
        if inferred_state:
            state = inferred_state
    
    return state_regular_prices.get(state, 3.50)

def get_premium_fuel_price(regular_price: float) -> float:
    """Calculate premium fuel price (typically $0.30-$0.50 more than regular)"""
    return regular_price + 0.40

# ui/calculator_display.py - UPDATED Premium Fuel Detection Function
# Comprehensive detection based on complete vehicle database review

def determine_fuel_type_and_price(make: str, model: str, year: int, trim: str = "", 
                                 zip_code: str = None, state: str = None) -> Dict[str, Any]:
    """
    Determine if vehicle requires premium fuel and return appropriate pricing
    UPDATED: Comprehensive detection based on full database analysis
    """
    
    make_lower = make.lower()
    model_lower = model.lower()
    trim_lower = trim.lower() if trim else ""
    
    # Get base regular fuel price for location
    regular_price = get_fuel_price_from_location(zip_code, state)
    
    # Electric vehicles don't use fuel
    if detect_electric_vehicle(make, model):
        return {
            'fuel_type': 'electric',
            'fuel_price': 0.0,
            'requires_premium': False,
            'price_info': f"Electric vehicle - uses electricity instead of fuel"
        }
    
    # Determine if vehicle requires premium fuel
    requires_premium = False
    
    # ========================================================================
    # 1. LUXURY BRANDS - All models require premium
    # ========================================================================
    luxury_brands_premium = [
        'bmw', 'mercedes-benz', 'audi', 'lexus', 'infiniti', 'acura', 
        'porsche', 'maserati', 'alfa romeo', 'jaguar', 'land rover'
    ]
    if make_lower in luxury_brands_premium:
        requires_premium = True
    
    # ========================================================================
    # 2. PERFORMANCE & LUXURY MODELS BY MANUFACTURER
    # ========================================================================
    performance_models = {
        # TOYOTA - Premium fuel models
        'toyota': ['supra', 'prius prime', 'land cruiser'],
        
        # HONDA - Premium fuel models
        'honda': ['type r', 'nsx', 'pilot elite', 'pilot touring', 'pilot black edition',
                  'passport elite', 'odyssey elite', 'ridgeline black edition'],
        
        # CHEVROLET - Performance models
        'chevrolet': ['corvette', 'camaro ss', 'camaro zl1', 'camaro 2ss', 'camaro zl1 1le',
                     'tahoe rst', 'suburban rst', 'silverado high country'],
        
        # FORD - Premium fuel models
        'ford': ['mustang gt', 'mustang shelby', 'mustang mach 1', 'mustang gt500',
                'f-150 raptor', 'f-150 platinum', 'f-150 limited', 'f-150 king ranch',
                'expedition platinum', 'expedition king ranch', 'explorer st', 'explorer platinum'],
        
        # HYUNDAI/GENESIS - Performance & luxury
        'hyundai': ['veloster n', 'veloster turbo', 'genesis', 'genesis 5.0', 'genesis r-spec',
                   'santa fe calligraphy', 'palisade calligraphy', 'sonata n line'],
        
        # NISSAN - Performance models
        'nissan': ['gt-r', '370z', '400z', 'z', 'maxima', 'maxima platinum', 'maxima sr',
                  'pathfinder platinum', 'armada platinum'],
        
        # MAZDA - Turbocharged & premium models
        'mazda': ['cx-90', 'cx-70', 'cx-9 signature', 'cx-5 turbo', 'mazda6 turbo',
                 'mazda3 turbo', 'cx-50 turbo'],
        
        # SUBARU - Performance models
        'subaru': ['wrx', 'sti', 'brz', 'ascent touring', 'outback touring xt'],
        
        # CADILLAC - All V-series and luxury trims
        'cadillac': ['cts-v', 'ats-v', 'ct4-v', 'ct5-v', 'ct6-v', 'escalade', 
                    'escalade platinum', 'escalade sport', 'xt5 platinum', 'xt6 platinum'],
        
        # DODGE - Performance models
        'dodge': ['hellcat', 'srt', 'viper', 'charger r/t', 'charger srt', 'charger hellcat',
                 'challenger r/t', 'challenger srt', 'challenger hellcat', 'durango srt', 'durango r/t'],
        
        # JEEP - Performance & premium trims
        'jeep': ['srt', 'trackhawk', 'grand cherokee srt', 'grand cherokee summit',
                'wrangler rubicon 392', 'grand cherokee overland', 'grand cherokee high altitude'],
        
        # BUICK - Premium trims
        'buick': ['enclave avenir', 'enclave premium', 'envision avenir'],
        
        # GMC - Denali trims (premium line)
        'gmc': ['yukon denali', 'yukon xl denali', 'sierra denali', 'sierra at4',
               'acadia denali', 'terrain denali', 'canyon denali'],
        
        # LINCOLN - All models require premium
        'lincoln': ['navigator', 'aviator', 'nautilus', 'corsair', 'continental'],
        
        # CHRYSLER - V6 and premium models
        'chrysler': ['300c', '300s', '300 platinum', 'pacifica hybrid'],
        
        # RAM - Premium trims
        'ram': ['1500 limited', '1500 longhorn', '1500 laramie longhorn', '1500 rebel',
               '2500 laramie', '2500 limited', '3500 limited', 'trx'],
        
        # VOLKSWAGEN - Performance models
        'volkswagen': ['golf r', 'golf gti', 'jetta gli', 'tiguan r-line', 'atlas cross sport r-line'],
        
        # VOLVO - All turbocharged (most models)
        'volvo': ['s60', 's90', 'v60', 'v90', 'xc40', 'xc60', 'xc90'],
        
        # KIA - Performance models
        'kia': ['stinger', 'stinger gt', 'k5 gt', 'sportage sx', 'sorento sx', 'telluride sx'],
        
        # MINI - All turbocharged models
        'mini': ['cooper s', 'cooper jcw', 'countryman s', 'clubman s'],
    }
    
    # Check if model matches any performance model
    if make_lower in performance_models:
        for perf_model in performance_models[make_lower]:
            if perf_model in model_lower or perf_model in trim_lower:
                requires_premium = True
                break
    
    # ========================================================================
    # 3. HIGH-PERFORMANCE TRIM INDICATORS
    # ========================================================================
    premium_trim_indicators = [
        # Engine-based
        'turbo', 'supercharged', 'v8', 'v10', 'v12', 'twin turbo', 'biturbo',
        
        # Performance badges
        'srt', 'ss', 'rs', 'r/t', 'gt', 'gti', 'gli', 'si', 'type r', 'type s',
        'nismo', 'sti', 'wrx', 'n line', 'n',
        
        # Luxury performance
        'amg', 'm sport', 'm3', 'm4', 'm5', 'quattro', 's line', 'rs', 'f sport', 
        'red sport', 'sport plus',
        
        # Premium luxury trims
        'platinum', 'denali', 'summit', 'calligraphy', 'avenir', 'prestige',
        'premium plus', 'limited black edition',
        
        # Special editions
        '392', 'hellcat', 'demon', 'redeye', 'trackhawk', 'raptor', 'tremor',
        'fx4', 'king ranch', 'limited', 'longhorn',
        
        # Performance packages
        'sport package', 'performance package', 'track package', 'carbon',
    ]
    
    # Check trim indicators
    for indicator in premium_trim_indicators:
        if indicator in trim_lower or indicator in model_lower:
            requires_premium = True
            break
    
    # ========================================================================
    # 4. SPECIFIC HIGH-END TRIMS BY MANUFACTURER
    # ========================================================================
    high_end_trims = {
        'toyota': ['limited', 'platinum', 'trd pro', '1794 edition', 'capstone'],
        'honda': ['touring', 'elite', 'black edition'],
        'ford': ['platinum', 'king ranch', 'limited', 'tremor', 'lariat'],
        'chevrolet': ['high country', 'premier', 'ltz', 'rst'],
        'gmc': ['denali', 'at4', 'slt'],
        'ram': ['limited', 'laramie longhorn', 'rebel', 'trx'],
        'jeep': ['summit', 'overland', 'high altitude', 'trailhawk'],
        'nissan': ['platinum', 'sl', 'sr'],
        'mazda': ['signature', 'carbon edition'],
        'subaru': ['touring', 'onyx edition xt'],
        'hyundai': ['calligraphy', 'ultimate'],
        'kia': ['sx', 'sx prestige', 'gt-line'],
        'volkswagen': ['sel premium', 'r-line'],
    }
    
    # Check high-end trims
    if make_lower in high_end_trims:
        for high_trim in high_end_trims[make_lower]:
            if high_trim in trim_lower:
                requires_premium = True
                break
    
    # ========================================================================
    # 5. EXCEPTIONS - Models that DON'T require premium despite brand/trim
    # ========================================================================
    regular_fuel_exceptions = {
        'acura': ['ilx 2.4l'],  # Base ILX uses regular
        'buick': ['encore', 'envision preferred'],  # Base trims
        'lincoln': ['mkz 2.0t'],  # Hybrid uses regular
        'volvo': ['s60 t5', 'xc60 t5'],  # Some base T5 engines
    }
    
    # Check exceptions
    if make_lower in regular_fuel_exceptions:
        for exception in regular_fuel_exceptions[make_lower]:
            if exception in model_lower or exception in trim_lower:
                requires_premium = False
                break
    
    # ========================================================================
    # 6. YEAR-BASED ADJUSTMENTS (Newer turbo engines)
    # ========================================================================
    if year >= 2018:
        # Modern turbocharged engines often require premium
        turbo_keywords = ['turbo', 't5', 't6', '2.0t', '3.0t', 'ecoboost']
        if any(keyword in trim_lower or keyword in model_lower for keyword in turbo_keywords):
            requires_premium = True
    
    # ========================================================================
    # 7. CALCULATE FINAL PRICE
    # ========================================================================
    if requires_premium:
        final_price = get_premium_fuel_price(regular_price)
        fuel_type = 'premium'
        price_info = f"Premium fuel required - ${final_price:.2f}/gal (${regular_price:.2f} regular + $0.40 premium)"
    else:
        final_price = regular_price
        fuel_type = 'regular'
        price_info = f"Regular fuel - ${final_price:.2f}/gal"
    
    return {
        'fuel_type': fuel_type,
        'fuel_price': final_price,
        'requires_premium': requires_premium,
        'regular_price': regular_price,
        'premium_price': get_premium_fuel_price(regular_price),
        'price_info': price_info
    }


# Helper function to get premium fuel price (if not already defined)
def get_premium_fuel_price(regular_price: float) -> float:
    """Calculate premium fuel price (typically $0.30-$0.50 more than regular)"""
    return regular_price + 0.40

def get_electricity_rate_from_location(zip_code: str = None, state: str = None) -> float:
    """Get electricity rate from ZIP code or state"""
    from utils.zip_code_utils import get_electricity_rate_estimate
    
    # Use the new function from zip_code_utils
    if zip_code and len(zip_code) == 5:
        return get_electricity_rate_estimate(zip_code, state)
    
    # Fall back to state rate
    if state:
        return get_electricity_rate_estimate('', state)
    
    # National average fallback
    return 0.15

def clean_maintenance_services(services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicates and false items from maintenance services"""
    if not services:
        return []
    
    valid_services = []
    seen_services = set()
    
    for service in services:
        if not isinstance(service, dict):
            continue
            
        service_name = service.get('service', '').strip()
        total_cost = service.get('total_cost', service.get('cost', 0))
        
        # Skip invalid services (false items)
        if not service_name or total_cost <= 0:
            continue
            
        # Skip duplicates (normalized name)
        normalized_name = service_name.lower().replace('(', '').replace(')', '').strip()
        if normalized_name in seen_services:
            continue
            
        seen_services.add(normalized_name)
        valid_services.append({
            'service': service_name,
            'frequency': service.get('frequency', 1),
            'total_cost': total_cost,
            'cost_per_service': service.get('cost_per_service', total_cost),
            'type': service.get('type', 'routine')
        })
    
    return valid_services

def calculate_blended_electricity_rate(base_rate: float, charging_preference: str) -> Dict[str, Any]:
    """
    Calculate the blended (weighted average) electricity rate based on charging pattern
    
    Args:
        base_rate: Home electricity rate ($/kWh)
        charging_preference: One of 'home_primary', 'mixed', 'public_heavy'
    
    Returns:
        Dictionary with blended rate and breakdown
    """
    
    # Cost multipliers for different charging types
    cost_multipliers = {
        'home': 1.0,           # Base residential rate
        'workplace': 0.5,      # Often subsidized or free
        'public_level2': 1.5,  # 50% premium for public Level 2
        'public_dc_fast': 2.5  # 150% premium for DC fast charging
    }
    
    # Charging patterns by preference
    charging_patterns = {
        'home_primary': {
            'home': 0.80,
            'workplace': 0.15,
            'public_level2': 0.03,
            'public_dc_fast': 0.02
        },
        'mixed': {
            'home': 0.60,
            'workplace': 0.20,
            'public_level2': 0.15,
            'public_dc_fast': 0.05
        },
        'public_heavy': {
            'home': 0.40,
            'workplace': 0.10,
            'public_level2': 0.35,
            'public_dc_fast': 0.15
        }
    }
    
    pattern = charging_patterns.get(charging_preference, charging_patterns['mixed'])
    
    # Calculate weighted average rate
    blended_rate = 0
    breakdown = {}
    
    for charging_type, percentage in pattern.items():
        effective_rate = base_rate * cost_multipliers[charging_type]
        weighted_contribution = effective_rate * percentage
        blended_rate += weighted_contribution
        
        breakdown[charging_type] = {
            'percentage': percentage * 100,
            'base_rate': base_rate,
            'multiplier': cost_multipliers[charging_type],
            'effective_rate': effective_rate,
            'contribution': weighted_contribution
        }
    
    return {
        'blended_rate': blended_rate,
        'base_rate': base_rate,
        'breakdown': breakdown,
        'charging_preference': charging_preference
    }


def display_charging_preference_form(electricity_rate: float = None, state: str = None) -> Dict[str, Any]:
    """
    Display charging preference form for electric vehicles with blended rate calculation
    
    Args:
        electricity_rate: Base home electricity rate (optional, will auto-detect if not provided)
        state: State for auto-detecting electricity rate
    """
    
    st.subheader("🔌 EV Charging Preferences")
    
    # Get base electricity rate if not provided
    if electricity_rate is None:
        electricity_rate = get_electricity_rate_from_location(None, state) if state else 0.12
    
    charging_options = {
        'home_primary': '🏠 Home Primary (80% home, 15% workplace, 5% public)',
        'mixed': '⚡ Mixed Charging (60% home, 20% workplace, 20% public)', 
        'public_heavy': '🏢 Public Heavy (40% home, 10% workplace, 50% public)'
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        charging_preference = st.selectbox(
            "Primary Charging Style:",
            options=list(charging_options.keys()),
            format_func=lambda x: charging_options[x],
            index=1,
            help="How you plan to charge your EV affects electricity costs significantly"
        )
    
    with col2:
        # Calculate blended rate for selected preference
        blended_info = calculate_blended_electricity_rate(electricity_rate, charging_preference)
        
        st.info("**💰 Blended Utility Rate:**")
        st.metric(
            "Weighted Avg Rate", 
            f"${blended_info['blended_rate']:.3f}/kWh",
            help="Weighted average of home and public charging costs"
        )
        st.caption(f"Base home rate: ${electricity_rate:.3f}/kWh")
    
    # Show detailed breakdown in expander
    with st.expander("📊 See Detailed Rate Breakdown"):
        st.markdown("**Charging Mix & Effective Rates:**")
        
        breakdown_data = []
        for charging_type, details in blended_info['breakdown'].items():
            if details['percentage'] > 0:
                charging_name = charging_type.replace('_', ' ').title()
                breakdown_data.append({
                    'Charging Type': charging_name,
                    'Usage %': f"{details['percentage']:.1f}%",
                    'Rate Multiplier': f"{details['multiplier']:.1f}x",
                    'Effective Rate': f"${details['effective_rate']:.3f}/kWh",
                    'Contribution': f"${details['contribution']:.4f}/kWh"
                })
        
        import pandas as pd
        df = pd.DataFrame(breakdown_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("**💡 Rate Explanation:**")
        st.write(f"• **Home:** ${electricity_rate:.3f}/kWh (your residential rate)")
        st.write(f"• **Workplace:** ${electricity_rate * 0.5:.3f}/kWh (typically subsidized)")
        st.write(f"• **Public Level 2:** ${electricity_rate * 1.5:.3f}/kWh (~50% premium)")
        st.write(f"• **DC Fast Charging:** ${electricity_rate * 2.5:.3f}/kWh (~150% premium)")
        
        st.info(f"🎯 **Your Blended Rate:** ${blended_info['blended_rate']:.3f}/kWh reflects the weighted average across all charging locations you'll use.")
    
    # Show estimated monthly costs with blended rate
    st.markdown("---")
    st.markdown("**📈 Estimated Monthly Energy Costs:**")
    
    col1, col2, col3 = st.columns(3)
    
    # Calculate monthly costs for each preference
    monthly_costs = {}
    # Calculate monthly costs for each preference using actual EV calculator
    from models.fuel.electric_vehicle_utils import EVCostCalculator
    ev_calc = EVCostCalculator()

    monthly_costs = {}
    for pref_key in charging_options.keys():
        # Use actual calculation with efficiency losses
        annual_cost = ev_calc.calculate_annual_electricity_cost(
            annual_mileage=12000,
            vehicle_efficiency=32,  # Average EV efficiency
            electricity_rate=electricity_rate,
            charging_preference=pref_key
        )
        monthly_costs[pref_key] = annual_cost / 12
    
    with col1:
        cost = monthly_costs['home_primary']
        is_selected = charging_preference == 'home_primary'
        if is_selected:
            st.success(f"**🏠 Home Primary**\n\n${cost:.0f}/month")
        else:
            st.metric("🏠 Home Primary", f"${cost:.0f}/mo")
    
    with col2:
        cost = monthly_costs['mixed']
        is_selected = charging_preference == 'mixed'
        if is_selected:
            st.success(f"**⚡ Mixed**\n\n${cost:.0f}/month")
        else:
            st.metric("⚡ Mixed", f"${cost:.0f}/mo")
    
    with col3:
        cost = monthly_costs['public_heavy']
        is_selected = charging_preference == 'public_heavy'
        if is_selected:
            st.success(f"**🏢 Public Heavy**\n\n${cost:.0f}/month")
        else:
            st.metric("🏢 Public Heavy", f"${cost:.0f}/mo")
    
    st.caption("*Estimate based on average EV efficiency (32 kWh/100mi, 12,000 miles/year). Actual costs calculated using your specific vehicle's efficiency.")
    
    return {
        'charging_preference': charging_preference,
        'blended_electricity_rate': blended_info['blended_rate'],
        'base_electricity_rate': electricity_rate
    }

def display_location_energy_info(zip_code: str = None, state: str = None, make: str = None, model: str = None, trim: str = None):
    """Display location and energy pricing info with EV detection"""
    
    is_electric = detect_electric_vehicle(make or '', model or '')
    energy_type = get_vehicle_energy_type(make or '', model or '')
    
    location_str = ""
    if zip_code and state:
        location_str = f"🗺️ Location: {zip_code}, {state}"
    elif state:
        location_str = f"🗺️ State: {state}"
    
    if is_electric:
        electricity_rate = get_electricity_rate_from_location(zip_code, state)
        st.info(f"{location_str} | 🔌 Electricity Rate: ${electricity_rate:.3f}/kWh | ⚡ Electric Vehicle")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Energy Type", "⚡ Electric")
        with col2:
            st.metric("Electricity Rate", f"${electricity_rate:.3f}/kWh")
        with col3:
            monthly_cost = electricity_rate * 300
            st.metric("Est. Monthly Energy", f"${monthly_cost:.0f}")
            
    elif energy_type == 'hybrid':
        fuel_price = get_fuel_price_from_location(zip_code, state)
        st.info(f"{location_str} | ⛽ Fuel Price: ${fuel_price:.2f}/gallon | 🔋 Hybrid Vehicle")
        
    else:
        fuel_price = get_fuel_price_from_location(zip_code, state)
        st.info(f"{location_str} | ⛽ Fuel Price: ${fuel_price:.2f}/gallon | 🚗 Gasoline Vehicle")

def display_maintenance_schedule_tab(results: Dict[str, Any], vehicle_data: Dict[str, Any]):
    """Display detailed maintenance schedule and activities for each year (from calculator_display_10AUG.py)"""
    
    st.subheader("🔧 Detailed Maintenance Schedule")
    
    maintenance_schedule = results.get('maintenance_schedule', [])
    annual_breakdown = results.get('annual_breakdown', [])
    
    if not maintenance_schedule:
        st.warning("Maintenance schedule not available.")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_maintenance_cost = sum(year['total_year_cost'] for year in maintenance_schedule)
    avg_annual_maintenance = total_maintenance_cost / len(maintenance_schedule) if maintenance_schedule else 0
    
    with col1:
        st.metric("Total Maintenance Cost", f"${total_maintenance_cost:,.0f}")
    
    with col2:
        st.metric("Average Annual", f"${avg_annual_maintenance:,.0f}")
    
    with col3:
        st.metric("Analysis Period", f"{len(maintenance_schedule)} years")
    
    with col4:
        shop_type = vehicle_data.get('shop_type', 'independent').title()
        st.metric("Service Type", shop_type)
    
    st.markdown("---")
    
    # Detailed year-by-year breakdown
    st.markdown("#### 📅 Year-by-Year Maintenance Activities")
    
    for year_data in maintenance_schedule:
        year_num = year_data['year']
        total_mileage = year_data['total_mileage']
        year_cost = year_data['total_year_cost']
        services = year_data.get('services', [])
        
        # Create expandable section for each year
        with st.expander(f"**Year {year_num}** ({total_mileage:,} miles) - ${year_cost:,.0f}", expanded=(year_num <= 2)):
            
            if not services:
                st.info("No maintenance activities scheduled for this year.")
                continue
            
            # Separate scheduled maintenance from wear/tear
            scheduled_services = [s for s in services if s.get('interval_based', True)]
            wear_services = [s for s in services if not s.get('interval_based', True)]
            
            # Display scheduled maintenance
            if scheduled_services:
                st.markdown("**🔧 Scheduled Maintenance:**")
                
                # Create a nice table for scheduled services
                service_data = []
                for service in scheduled_services:
                    service_data.append({
                        'Service': service['service'],
                        'Frequency': f"{service['frequency']}x",
                        'Cost Each': f"${service['cost_per_service']:,.0f}",
                        'Total Cost': f"${service['total_cost']:,.0f}",
                        'Type': service.get('shop_type', 'independent').title()
                    })
                
                if service_data:
                    df_services = pd.DataFrame(service_data)
                    st.dataframe(df_services, use_container_width=True, hide_index=True)
            
            # Display wear and tear items
            if wear_services:
                st.markdown("**⚙️ Wear & Tear / Repairs:**")
                
                for service in wear_services:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"• {service['service']}")
                    with col2:
                        st.write(f"${service['total_cost']:,.0f}")
            
            # Year summary
            scheduled_total = sum(s['total_cost'] for s in scheduled_services)
            wear_total = sum(s['total_cost'] for s in wear_services)
            
            if scheduled_total > 0 or wear_total > 0:
                st.markdown("**💰 Year Summary:**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Scheduled Maintenance", f"${scheduled_total:,.0f}")
                with col2:
                    st.metric("Wear & Repairs", f"${wear_total:,.0f}")
                with col3:
                    st.metric("Year Total", f"${year_cost:,.0f}")
            
            # Show warranty coverage for leases
            if vehicle_data.get('transaction_type', '').lower() == 'lease':
                warranty_discount = year_data.get('warranty_discount', 0)
                if warranty_discount > 0:
                    warranty_savings = scheduled_total / (1 - warranty_discount) * warranty_discount
                    st.success(f"🛡️ Warranty Coverage: ${warranty_savings:,.0f} covered ({warranty_discount*100:.0f}%)")
    
    # Maintenance insights and recommendations
    st.markdown("---")
    st.markdown("#### 💡 Maintenance Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Cost Analysis:**")
        
        # Peak years analysis
        peak_year = max(maintenance_schedule, key=lambda x: x['total_year_cost'])
        low_year = min(maintenance_schedule, key=lambda x: x['total_year_cost'])
        
        st.write(f"• **Highest cost year:** Year {peak_year['year']} (${peak_year['total_year_cost']:,.0f})")
        st.write(f"• **Lowest cost year:** Year {low_year['year']} (${low_year['total_year_cost']:,.0f})")
        
        # Calculate cost trend
        first_half_avg = sum(y['total_year_cost'] for y in maintenance_schedule[:len(maintenance_schedule)//2]) / (len(maintenance_schedule)//2)
        second_half_avg = sum(y['total_year_cost'] for y in maintenance_schedule[len(maintenance_schedule)//2:]) / (len(maintenance_schedule) - len(maintenance_schedule)//2)
        
        if second_half_avg > first_half_avg * 1.2:
            st.write("• **Trend:** Costs increase significantly in later years")
        elif second_half_avg < first_half_avg * 0.8:
            st.write("• **Trend:** Costs decrease in later years (unusual)")
        else:
            st.write("• **Trend:** Costs remain relatively stable over time")
    
    with col2:
        st.markdown("**💰 Cost Optimization Tips:**")
        
        shop_type = vehicle_data.get('shop_type', 'independent')
        if shop_type == 'dealership':
            st.write("• Consider independent shops for routine maintenance to save 15-20%")
        elif shop_type == 'independent':
            st.write("• You're already optimizing costs with independent shops")
        
        st.write("• Follow manufacturer's maintenance schedule to prevent major repairs")
        st.write("• Keep detailed maintenance records for warranty and resale value")
        
        if vehicle_data.get('transaction_type', '').lower() == 'lease':
            st.write("• For leases, use dealership service to maintain warranty coverage")
        else:
            st.write("• Regular maintenance can extend vehicle life beyond analysis period")

def display_calculator():
    """
    Enhanced calculator with all-visible forms
    Single vehicle TCO analysis with EV support
    """
    
    st.header("🔧 Single Vehicle Analysis")
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🗺️ **ZIP Code Pricing**\nAuto-detects fuel/electricity rates")
    with col2:
        st.info("⚡ **EV Support**\nCharging style selection")
    with col3:
        st.info("🔧 **All Forms Visible**\nComplete in any order")
    
    st.markdown("---")
    
    # Collect all form data - SINGLE CALL ONLY
    from ui.input_forms import display_all_forms_visible
    all_data, is_valid, validation_message = display_all_forms_visible()
    
    # Calculate button section
    st.markdown("---")
    
    if is_valid:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 Calculate Total Cost of Ownership", type="primary", use_container_width=True):
                with st.spinner("🔄 Calculating comprehensive TCO analysis..."):
                    try:
                        # Initialize prediction service
                        from services.prediction_service import PredictionService
                        prediction_service = PredictionService()
                        
                        # Calculate TCO using existing service
                        results = prediction_service.calculate_total_cost_of_ownership(all_data)
                        
                        # Store in session state
                        st.session_state.current_results = results
                        st.session_state.current_vehicle = all_data
                        st.session_state.calculation_complete = True
                        
                        st.success("✅ Calculation complete! Results displayed below.")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Calculation failed: {str(e)}")
                        st.error("Please check your inputs and try again.")
                        import traceback
                        st.error(traceback.format_exc())
          
        # ✅ ONLY SHOW "Add to Comparison" AFTER CALCULATION IS COMPLETE
        if st.session_state.get('calculation_complete', False):
            st.markdown("---")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown("### 📊 Multi-Vehicle Comparison")
                st.write("Compare this vehicle with others to make the best decision")
                
                if st.button("➕ Add to Comparison", type="secondary", use_container_width=True, key="add_to_comparison_main"):
                    try:
                        # Initialize comparison list if needed
                        if 'comparison_vehicles' not in st.session_state:
                            st.session_state.comparison_vehicles = []
                        
                        # Use the calculated vehicle data from session state
                        vehicle_data_to_add = st.session_state.current_vehicle.copy()
                        
                        # Check for duplicates
                        make = vehicle_data_to_add.get('make', '')
                        model = vehicle_data_to_add.get('model', '')
                        year = vehicle_data_to_add.get('year', '')
                        trim = vehicle_data_to_add.get('trim', '')
                        transaction_type = vehicle_data_to_add.get('transaction_type', '')
                        
                        vehicle_exists = any(
                            existing.get('make') == make and 
                            existing.get('model') == model and 
                            existing.get('year') == year and 
                            existing.get('trim') == trim and
                            existing.get('transaction_type') == transaction_type
                            for existing in st.session_state.comparison_vehicles
                        )
                        
                        if not vehicle_exists:
                            # Check maximum limit
                            max_vehicles = 5
                            if len(st.session_state.comparison_vehicles) >= max_vehicles:
                                st.error(f"❌ Maximum of {max_vehicles} vehicles allowed in comparison.")
                            else:
                                # Add vehicle to comparison (with results)
                                vehicle_entry = {
                                    'data': vehicle_data_to_add,
                                    'results': st.session_state.current_results,
                                    'name': f"{year} {make} {model} {trim}"
                                }
                                st.session_state.comparison_vehicles.append(vehicle_entry)
                                vehicle_count = len(st.session_state.comparison_vehicles)
                                
                                st.success(f"✅ Added {year} {make} {model} {trim} to comparison!")
                                st.balloons()
                                st.info(f"📊 Comparison list now has {vehicle_count} vehicle(s). Go to 'Multi-Vehicle Comparison' to compare.")
                                
                                # Show quick link to comparison
                                st.markdown("👉 **Go to Multi-Vehicle Comparison in the sidebar to see your comparison**")
                        else:
                            st.warning("⚠️ This exact vehicle configuration is already in your comparison list!")
                            
                    except Exception as e:
                        st.error(f"❌ Error adding to comparison: {str(e)}")
                        import traceback
                        st.error(traceback.format_exc())
        
        else:
            st.warning(f"⚠️ {validation_message}")
            st.info("💡 Please complete all required fields above to proceed with calculation")
    
    # Display results if calculation is complete (uses existing function)
    if st.session_state.get('calculation_complete', False) and 'current_results' in st.session_state:
        st.markdown("---")
        st.markdown("---")
        
        # Use existing results display function
        display_detailed_results_with_maintenance()

def display_enhanced_basic_calculator():
    """Enhanced calculator with simplified form but missing some advanced services"""
    
    st.subheader("🚗 Vehicle Cost Calculator")
    st.warning("⚠️ Some advanced services unavailable - using simplified calculator. Install dependencies for advanced analysis.")
    
    # Enhanced form with all features
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🚗 Vehicle Information**")
        make = st.selectbox("Make:", ["Tesla", "Toyota", "Honda", "Chevrolet", "Ford", "Hyundai", "BMW", "Nissan"])
        model = st.text_input("Model:", value="Model 3" if make == "Tesla" else "Camry")
        year = st.number_input("Year:", min_value=2015, max_value=2025, value=2024)
        
        # Add trim input BEFORE using it
        trim = st.text_input("Trim:", value="Base", help="Vehicle trim level (e.g., Base, LX, Sport)")
        
        is_electric = detect_electric_vehicle(make, model)
        
        if is_electric:
            st.success(f"⚡ Electric Vehicle Detected: {make} {model}")
            price = st.number_input("Purchase Price ($):", min_value=20000, max_value=200000, value=45000, step=1000)
        else:
            price = st.number_input("Purchase Price ($):", min_value=10000, max_value=200000, value=30000, step=1000)
        
        # Display MPG information if vehicle is selected
        if make and model and year and MPG_DATABASE_AVAILABLE:
            try:
                mpg_data = display_vehicle_mpg_info(make, model, year, trim)
            except Exception as e:
                # Silently fail if MPG data not available
                pass
    
    with col2:
        st.markdown("**📍 Location & Usage**")
        zip_code = st.text_input("ZIP Code (5 digits):", value="90210", help="Auto-populates fuel/electricity pricing")
        
        if zip_code and len(zip_code) == 5 and zip_code.isdigit():
            zip_to_state = {
                '90210': 'CA', '10001': 'NY', '60601': 'IL', '77001': 'TX', '33101': 'FL',
                '98101': 'WA', '97201': 'OR', '80201': 'CO', '30301': 'GA', '48201': 'MI'
            }
            state = zip_to_state.get(zip_code, 'CA')
        else:
            state = st.selectbox("State:", ['CA', 'TX', 'FL', 'NY', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI'], index=0)
        
        annual_mileage = st.number_input("Annual Mileage:", min_value=5000, max_value=50000, value=12000, step=1000)
        analysis_years = st.number_input("Analysis Years:", min_value=1, max_value=15, value=5)
    
    # Display location and energy info
    display_location_energy_info(zip_code, state, make, model, trim)
    
    # EV-specific charging preferences
    charging_data = {}
    if is_electric:
        st.markdown("---")
        # Pass electricity rate and state for blended rate calculation
        electricity_rate = get_electricity_rate_from_location(zip_code, state)
        charging_data = display_charging_preference_form(electricity_rate, state)
    
    # Calculate button
    if st.button("🚀 Calculate Enhanced TCO", type="primary", use_container_width=True):
        
        if is_electric:
            electricity_rate = get_electricity_rate_from_location(zip_code, state)
            if 'blended_electricity_rate' in charging_data:
                electricity_rate = charging_data['blended_electricity_rate']
            charging_preference = charging_data.get('charging_preference', 'mixed')  # NEW LINE
            fuel_price = 0
        else:
            fuel_price = get_fuel_price_from_location(zip_code, state)
            electricity_rate = 0
            charging_preference = 'mixed'  # NEW LINE
        
        results = calculate_enhanced_tco(
            make=make,
            model=model,
            year=year,
            price=price,
            annual_mileage=annual_mileage,
            years=analysis_years,
            fuel_price=fuel_price,
            electricity_rate=electricity_rate,
            is_electric=is_electric,
            charging_preference=charging_data.get('charging_preference', 'mixed'),
            zip_code=zip_code,
            state=state,
            trim=trim
        )
    
        display_enhanced_results(results, make, model, year, is_electric)

def calculate_enhanced_tco(make: str, model: str, year: int, price: float, annual_mileage: int, 
                          years: int, fuel_price: float, electricity_rate: float, is_electric: bool,
                          charging_preference: str, zip_code: str, state: str, 
                          current_mileage: int = 0) -> Dict[str, Any]:
    """
    Enhanced TCO calculation with all features.
    FIXED: Added the missing calculation logic before displaying results.
    """
    
    try:
        # FIXED: ADD THE MISSING CALCULATION LOGIC FIRST
        from datetime import datetime
        current_year = datetime.now().year
        purchase_year = current_year
        
        # Create input data for PredictionService (same pattern as your working code)
        enhanced_form_data = {
            'make': make,
            'model': model,
            'year': year,
            'price': price,
            'trim_msrp': price,
            'current_mileage': current_mileage,
            'annual_mileage': annual_mileage,
            'analysis_years': years,
            'zip_code': zip_code,
            'state': state,
            'transaction_type': 'purchase',
            'is_electric': is_electric,
            'charging_preference': charging_preference,
            'electricity_rate': electricity_rate,
            'fuel_price': fuel_price
        }
        
        # FIXED: USE PredictionService TO ACTUALLY CALCULATE THE RESULTS
        from services.prediction_service import PredictionService
        prediction_service = PredictionService()
        # Calculate full TCO with enhanced features
        raw_results = prediction_service.calculate_total_cost_of_ownership(enhanced_form_data)  
     
    except Exception as e:
        # Enhanced error handling 
        st.error(f"❌ Calculation failed: {str(e)}")
        st.error("Please check your inputs and try again.")
        
        # Return basic fallback result
        return {
            'summary': {'total_ownership_cost': 0, 'average_annual_cost': 0},
            'category_totals': {},
            'annual_breakdown': [],
            'maintenance_schedule': []
        }

def display_full_featured_calculator():
    """Full calculator with all services available"""
    
    st.subheader("🚗 Advanced Vehicle Calculator")
    st.success("✅ All services available - full functionality enabled")
    
    # Create two columns: form and results
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        form_data, is_valid, message = collect_all_form_data()
        
        # Add EV charging preference if electric vehicle detected
        if is_valid and detect_electric_vehicle(form_data.get('make', ''), form_data.get('model', '')):
            st.markdown("---")
            # Pass electricity rate and state for blended rate calculation
            electricity_rate = form_data.get('electricity_rate', 0.12)
            state = form_data.get('state', '')
            charging_data = display_charging_preference_form(electricity_rate, state)
            form_data.update(charging_data)
        
        if not is_valid:
            st.warning(f"⚠️ {message}")
            return
        
        # Enhanced location display with reactive fuel pricing
        zip_code = form_data.get('zip_code', '')
        state = form_data.get('state', '')
        make = form_data.get('make', '')
        model = form_data.get('model', '')
        trim = form_data.get('trim', '')
        
        # Show current fuel pricing based on selections
        if make and model and state:
            st.markdown("---")
            st.subheader("📍 Current Pricing Information")
            
            vehicle_is_electric = detect_electric_vehicle(make, model)
            
            if vehicle_is_electric:
                electricity_rate = get_electricity_rate_from_location(zip_code, state)
                st.info(f"⚡ **Electric Vehicle**: {make} {model} - Electricity: ${electricity_rate:.3f}/kWh")
            else:
                fuel_price = get_fuel_price_from_location(zip_code, state)
                st.info(f"⛽ **Gas Vehicle**: {make} {model} - Fuel: ${fuel_price:.2f}/gal")
        
        st.markdown("---")
        
        # Calculate button
        if st.button("🧮 Calculate Enhanced TCO", type="primary", use_container_width=True):
            try:
                with st.spinner('🔄 Calculating comprehensive TCO analysis...'):
                    prediction_service = PredictionService()
                    results = prediction_service.calculate_total_cost_of_ownership(form_data)
                    
                    # Store results in session state
                    st.session_state.current_results = results
                    st.session_state.current_vehicle = form_data
                    st.session_state.calculation_complete = True
                    
                    st.success("✅ Calculation Complete! Results displayed below.")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Calculation failed: {str(e)}")
                st.error("Please check your inputs and try again.")
        

        
        # ✅ ONLY SHOW "Add to Comparison" AFTER CALCULATION IS COMPLETE
        if st.session_state.get('calculation_complete', False):
            st.markdown("---")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown("### 📊 Multi-Vehicle Comparison")
                st.write("Compare this vehicle with others to make the best decision")
                
                if st.button("➕ Add to Comparison", type="secondary", use_container_width=True, key="add_to_comparison_main"):
                    try:
                        # Initialize comparison list if needed
                        if 'comparison_vehicles' not in st.session_state:
                            st.session_state.comparison_vehicles = []
                        
                        # Use the calculated vehicle data from session state
                        vehicle_data_to_add = st.session_state.current_vehicle.copy()
                        
                        # Check for duplicates
                        make = vehicle_data_to_add.get('make', '')
                        model = vehicle_data_to_add.get('model', '')
                        year = vehicle_data_to_add.get('year', '')
                        trim = vehicle_data_to_add.get('trim', '')
                        transaction_type = vehicle_data_to_add.get('transaction_type', '')
                        
                        vehicle_exists = any(
                            existing.get('make') == make and 
                            existing.get('model') == model and 
                            existing.get('year') == year and 
                            existing.get('trim') == trim and
                            existing.get('transaction_type') == transaction_type
                            for existing in st.session_state.comparison_vehicles
                        )
                        
                        if not vehicle_exists:
                            # Check maximum limit
                            max_vehicles = 5
                            if len(st.session_state.comparison_vehicles) >= max_vehicles:
                                st.error(f"❌ Maximum of {max_vehicles} vehicles allowed in comparison.")
                            else:
                                # Add vehicle to comparison (with results)
                                vehicle_entry = {
                                    'data': vehicle_data_to_add,
                                    'results': st.session_state.current_results,
                                    'name': f"{year} {make} {model} {trim}"
                                }
                                st.session_state.comparison_vehicles.append(vehicle_entry)
                                vehicle_count = len(st.session_state.comparison_vehicles)
                                
                                st.success(f"✅ Added {year} {make} {model} {trim} to comparison!")
                                st.balloons()
                                st.info(f"📊 Comparison list now has {vehicle_count} vehicle(s). Go to 'Multi-Vehicle Comparison' to compare.")
                                
                                # Show quick link to comparison
                                st.markdown("👉 **Go to Multi-Vehicle Comparison in the sidebar to see your comparison**")
                        else:
                            st.warning("⚠️ This exact vehicle configuration is already in your comparison list!")
                            
                    except Exception as e:
                        st.error(f"❌ Error adding to comparison: {str(e)}")
                        import traceback
                        st.error(traceback.format_exc())
        
    with col2:
        # Display enhanced quick summary if available
        if st.session_state.get('calculation_complete', False):
            st.subheader("📊 Quick Summary")
            
            results = st.session_state.current_results
            vehicle_data = st.session_state.current_vehicle
            
            # Vehicle info
            make = vehicle_data.get('make', '')
            model = vehicle_data.get('model', '')
            year = vehicle_data.get('year', '')
            
            is_electric = detect_electric_vehicle(make, model)
            energy_icon = "⚡" if is_electric else "⛽"
            
            st.markdown(f"**{year} {make} {model} {energy_icon}**")
            
            # Key metrics
            if vehicle_data.get('transaction_type') == 'Purchase':
                total_cost = results['summary']['total_ownership_cost']
                annual_cost = results['summary']['average_annual_cost']
                
                st.metric("Total Cost", f"${total_cost:,.0f}")
                st.metric("Annual Cost", f"${annual_cost:,.0f}")
            
            # REMOVED: The duplicate "Add to Comparison" button that was here
        else:
            st.info("👈 Complete the form and click 'Calculate Enhanced TCO' to see results")
    
    # Display detailed results if calculation is complete
    if st.session_state.get('calculation_complete', False):
        st.markdown("---")
        display_detailed_results_with_maintenance()

def display_quick_summary():
    """Display a quick summary card of the calculation"""
    
    if not st.session_state.get('current_results'):
        return
    
    results = st.session_state.current_results
    vehicle_data = st.session_state.current_vehicle
    
    st.subheader("📊 Quick Summary")
    
    # Vehicle info
    make = vehicle_data.get('make', '')
    model = vehicle_data.get('model', '')
    year = vehicle_data.get('year', '')
    
    is_electric = detect_electric_vehicle(make, model)
    energy_icon = "⚡" if is_electric else "⛽"
    
    st.markdown(f"**{year} {make} {model} {energy_icon}**")
    
    # Key metrics
    if vehicle_data.get('transaction_type') == 'Purchase':
                # FIXED: Force out-of-pocket calculation
        category_totals = results.get('category_totals', {})
        out_of_pocket_total = (
            category_totals.get('maintenance', 0) +
            category_totals.get('insurance', 0) +
            category_totals.get('fuel_energy', 0) +
            category_totals.get('financing', 0)
        )
        total_cost = out_of_pocket_total
        annual_cost = out_of_pocket_total / vehicle_data.get('analysis_years', 5)
        annual_cost = results['summary']['average_annual_cost']
        
        st.metric("Total Cost", f"${total_cost:,.0f}")
        st.metric("Annual Cost", f"${annual_cost:,.0f}")

def display_detailed_results_with_maintenance():
    """Display comprehensive analysis results with enhanced maintenance tab"""
    
    results = st.session_state.current_results
    vehicle_data = st.session_state.current_vehicle
    
    # Tabs for organized display - NOW INCLUDING DETAILED MAINTENANCE
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Summary", 
        "🔧 Detailed Maintenance",  # Enhanced maintenance tab
        "📈 Visualizations", 
        "💰 Cost Breakdown",
        "🎯 Recommendations"
    ])
    
    with tab1:
        display_summary_tab(results, vehicle_data)
    
    with tab2:
        # NEW: Use the detailed maintenance schedule function
        display_maintenance_schedule_tab(results, vehicle_data)
    
    with tab3:
        display_visualizations(results, vehicle_data)
    
    with tab4:
        display_cost_breakdown(results, vehicle_data)
    
    with tab5:
        display_recommendations_tab(results, vehicle_data)

def display_summary_tab(results: Dict[str, Any], vehicle_data: Dict[str, Any]):
    """Display summary information"""
    
    st.subheader("📊 Cost Summary")
    
    # Summary metrics based on transaction type
    if vehicle_data.get('transaction_type') == 'Purchase':
        summary = results['summary']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # FIXED: Force out-of-pocket calculation  
            category_totals = results.get('category_totals', {})
            out_of_pocket_total = (
                category_totals.get('maintenance', 0) +
                category_totals.get('insurance', 0) +
                category_totals.get('fuel_energy', 0) +
                category_totals.get('financing', 0)
            )
            st.metric("Total Cost", f"${out_of_pocket_total:,.0f}")
        with col2:
            st.metric("Annual Average", f"${summary['average_annual_cost']:,.0f}")
        with col3:
            st.metric("Cost per Mile", f"${summary['cost_per_mile']:.3f}")
        with col4:
            st.metric("Final Value", f"${summary.get('final_vehicle_value', 0):,.0f}")
    
    else:  # Lease
        summary = results['summary']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Lease Cost", f"${summary['total_lease_cost']:,.0f}")
        with col2:
            st.metric("Monthly Average", f"${summary['average_monthly_cost']:,.0f}")
        with col3:
            st.metric("Cost per Mile", f"${summary['cost_per_mile']:.3f}")
        with col4:
            down_payment = summary.get('down_payment', 0)
            st.metric("Down Payment", f"${down_payment:,.0f}")
    
    # Category breakdown
    st.markdown("#### Cost Categories")
    category_totals = results.get('category_totals', {})
    
    if category_totals:
        categories = list(category_totals.keys())
        mid_point = len(categories) // 2
        
        col1, col2 = st.columns(2)
        
        with col1:
            for category in categories[:mid_point]:
                st.metric(
                    category.replace('_', ' ').title(),
                    f"${category_totals[category]:,.0f}"
                )
        
        with col2:
            for category in categories[mid_point:]:
                st.metric(
                    category.replace('_', ' ').title(),
                    f"${category_totals[category]:,.0f}"
                )

def display_visualizations(results: Dict[str, Any], vehicle_data: Dict[str, Any]):
    """Display charts and visualizations"""
    
    st.subheader("📊 Cost Visualizations")
    
    # Annual costs over time
    breakdown_data = results.get('annual_breakdown', [])
    if breakdown_data:
        df = pd.DataFrame(breakdown_data)
        
        # Line chart of annual costs
        fig_line = go.Figure()
        
        cost_categories = [col for col in df.columns if col not in ['ownership_year', 'year_of_ownership', 'vehicle_age', 'vehicle_model_year', 'total_mileage', 'total_annual_operating_cost', 'total_annual_cost_with_depreciation']]
        colors = px.colors.qualitative.Set3
        
        for i, category in enumerate(cost_categories):
            if category in df.columns:
                fig_line.add_trace(go.Scatter(
                x=df['ownership_year'] if 'ownership_year' in df.columns else list(range(1, len(df)+1)),
                y=df[category],
                mode='lines+markers',
                name=category.replace('_', ' ').title(),
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=6)
                ))
        
        fig_line.update_layout(
            title="Annual Costs by Category",
            xaxis_title="Calendar Year",
            yaxis_title="Annual Cost ($)",
            height=400,
            hovermode='x unified'
        )
        
        # FIXED: Add unique suffix using timestamp or counter to prevent duplicate keys
        import time
        unique_suffix = str(int(time.time() * 1000))  # millisecond timestamp
        st.plotly_chart(fig_line, use_container_width=True, key=f"viz_line_chart_{unique_suffix}")
        
        # Pie chart of total costs by category
        category_totals = results.get('category_totals', {})
        if category_totals:
            fig_pie = go.Figure(data=[go.Pie(
                labels=[cat.replace('_', ' ').title() for cat in category_totals.keys()],
                values=list(category_totals.values()),
                hole=0.3
            )])
            
            fig_pie.update_layout(
                title="Total Cost Distribution",
                height=400
            )
            
            # FIXED: Add unique suffix to pie chart key as well
            st.plotly_chart(fig_pie, use_container_width=True, key=f"viz_pie_chart_{unique_suffix}")

def display_cost_breakdown(results: Dict[str, Any], vehicle_data: Dict[str, Any]):
    """Display detailed cost breakdown - OPERATING COSTS ONLY with 15-year maximum bound"""
    
    st.subheader("💰 Annual Operating Cost Breakdown")
    st.info("💡 **Direct expenses only** - Depreciation tracked separately as opportunity cost")
    
    annual_breakdown = results.get('annual_breakdown', [])
    
    if annual_breakdown:
        # Get vehicle data
        current_mileage = vehicle_data.get('current_mileage', 0)
        annual_mileage = vehicle_data.get('annual_mileage', 12000)
        analysis_years = vehicle_data.get('analysis_years', 5)
        
        # BOUND THE ANALYSIS WINDOW: Maximum 15 years
        max_years = min(analysis_years, 15)
        
        # Limit the breakdown data to the bounded window
        bounded_breakdown = annual_breakdown[:max_years]
        
        st.write(f"Debug: Starting mileage = {current_mileage:,}, Annual mileage = {annual_mileage:,}")
        st.write(f"Debug: Analysis period bounded to {max_years} years (max 15)")
        
        # Create detailed breakdown table
        breakdown_data = []
        
        for year_index, year_data in enumerate(bounded_breakdown):
        # ADD THIS DEBUG
            if year_index == 0:  # Only print for first year
                print(f"\n=== DISPLAY DEBUG - First Year Data ===")
                print(f"year_data keys: {year_data.keys()}")
                print(f"fuel_energy value: {year_data.get('fuel_energy')}")
                print(f"annual_energy value: {year_data.get('annual_energy')}")
                print(f"===================================\n")

            year_of_ownership = year_index + 1
            
            # Ensure we don't exceed the bounded period
            if year_of_ownership > max_years:
                break
            
            # FIXED: Calculate correct total mileage including starting mileage
            calculated_total_mileage = current_mileage + (annual_mileage * year_of_ownership)
            
            # Use calculated mileage (always reliable)
            display_mileage = calculated_total_mileage
            
            # Calculate the year (from 2025 forward)
            ownership_year = 2025 + year_index
            
            row = {
                'Year': ownership_year,
                'Mileage': f"{display_mileage:,}",
            }
            
            # Add cost categories - REMOVE DEPRECIATION
            if vehicle_data.get('transaction_type', 'Purchase') == 'Purchase':
                row.update({
                    'Maintenance': f"${year_data.get('annual_maintenance', year_data.get('maintenance', 0)):,.0f}",
                    'Insurance': f"${year_data.get('annual_insurance', year_data.get('insurance', 0)):,.0f}",
                    'Fuel/Energy': f"${year_data.get('annual_energy', year_data.get('fuel_energy', 0)):,.0f}",
                    'Financing': f"${year_data.get('financing', 0):,.0f}",
                })
                
                # Calculate operating total
                maintenance = year_data.get('annual_maintenance', year_data.get('maintenance', 0))
                insurance = year_data.get('annual_insurance', year_data.get('insurance', 0))
                fuel_energy = year_data.get('fuel_energy', year_data.get('annual_energy', 0))
                financing = year_data.get('financing', 0)
                operating_total = maintenance + insurance + fuel_energy + financing
                
            else:  # Lease
                row.update({
                    'Lease Payment': f"${year_data.get('lease_payment', 0):,.0f}",
                    'Maintenance': f"${year_data.get('annual_maintenance', year_data.get('maintenance', 0)):,.0f}",
                    'Insurance': f"${year_data.get('annual_insurance', year_data.get('insurance', 0)):,.0f}",
                    'Fuel/Energy': f"${year_data.get('annual_energy', year_data.get('fuel_energy', 0)):,.0f}",
                    'Excess Fees': f"${year_data.get('excess_fees', 0):,.0f}",
                })
                
                # Calculate operating total
                lease_payment = year_data.get('lease_payment', 0)
                maintenance = year_data.get('annual_maintenance', year_data.get('maintenance', 0))
                insurance = year_data.get('annual_insurance', year_data.get('insurance', 0))
                fuel_energy = year_data.get('fuel_energy', year_data.get('annual_energy', 0))
                excess_fees = year_data.get('excess_fees', 0)
                operating_total = lease_payment + maintenance + insurance + fuel_energy + excess_fees
            
            row['Operating Total'] = f"${operating_total:,.0f}"
            breakdown_data.append(row)
        
        # Display the bounded table
        df_breakdown = pd.DataFrame(breakdown_data)
        st.dataframe(df_breakdown, use_container_width=True, hide_index=True)
        
        # Add info about the analysis period
        if current_mileage > 0:
            final_mileage = current_mileage + (annual_mileage * max_years)
            st.info(f"📊 **Used Vehicle Analysis:** Starting at {current_mileage:,} miles, ending at {final_mileage:,} miles over {max_years} years")
        else:
            final_mileage = annual_mileage * max_years
            st.info(f"📊 **New Vehicle Analysis:** {final_mileage:,} total miles over {max_years} years")
        
        # Add depreciation summary separately (only for purchases)
        if vehicle_data.get('transaction_type', 'Purchase') == 'Purchase':
            st.markdown("---")
            st.subheader("📈 Depreciation Summary")
            st.info("💡 **Opportunity cost** - Not a direct annual expense")
            
            if bounded_breakdown:
                total_depreciation = sum(year_data.get('annual_depreciation', year_data.get('depreciation', 0)) for year_data in bounded_breakdown)
                st.metric("Total Depreciation", f"${total_depreciation:,.0f}", 
                         help=f"Total value loss over {max_years}-year period")


# Alternative: Even cleaner version that handles bounds in the calculation itself
def display_cost_breakdown_clean(results: Dict[str, Any], vehicle_data: Dict[str, Any]):
    """Clean version with built-in bounds and error handling"""
    
    st.subheader("💰 Annual Operating Cost Breakdown")
    st.info("💡 **Direct expenses only** - Depreciation tracked separately as opportunity cost")
    
    # Get vehicle data with defaults
    current_mileage = vehicle_data.get('current_mileage', 0)
    annual_mileage = vehicle_data.get('annual_mileage', 12000)
    analysis_years = vehicle_data.get('analysis_years', 5)
    transaction_type = vehicle_data.get('transaction_type', 'Purchase')
    
    # ENFORCE BOUNDS: 1-15 years maximum
    bounded_years = max(1, min(analysis_years, 15))
    
    annual_breakdown = results.get('annual_breakdown', [])
    
    # Create reliable breakdown data
    breakdown_data = []
    
    for year_num in range(1, bounded_years + 1):
        # Calculate reliable values
        ownership_year = 2024 + year_num  # 2025, 2026, etc.
        total_mileage = current_mileage + (annual_mileage * year_num)
        
        # Get data from breakdown if available, otherwise use defaults
        if year_num <= len(annual_breakdown):
            year_data = annual_breakdown[year_num - 1]
        else:
            # Create default data if breakdown is incomplete
            year_data = {
                'annual_maintenance': 500 + (year_num * 100),  # Increasing maintenance
                'annual_insurance': 1200,  # Stable insurance
                'annual_energy': 2500,     # Default fuel/energy
                'financing': 0,            # Default no financing
                'annual_depreciation': 0   # Default no depreciation
            }
        
        row = {
            'Year': ownership_year,
            'Mileage': f"{total_mileage:,}",
        }
        
        # Add cost categories based on transaction type
        if transaction_type == 'Purchase':
            maintenance = year_data.get('annual_maintenance', year_data.get('maintenance', 500))
            insurance = year_data.get('annual_insurance', year_data.get('insurance', 1200))
            fuel_energy = year_data.get('fuel_energy', year_data.get('annual_energy', 0))
            financing = year_data.get('financing', 0)
            
            row.update({
                'Maintenance': f"${maintenance:,.0f}",
                'Insurance': f"${insurance:,.0f}",
                'Fuel/Energy': f"${fuel_energy:,.0f}",
                'Financing': f"${financing:,.0f}",
            })
            
            operating_total = maintenance + insurance + fuel_energy + financing
            
        else:  # Lease
            lease_payment = year_data.get('lease_payment', 400)
            maintenance = year_data.get('annual_maintenance', year_data.get('maintenance', 200))
            insurance = year_data.get('annual_insurance', year_data.get('insurance', 1200))
            fuel_energy = year_data.get('fuel_energy', year_data.get('annual_energy', 0))
            excess_fees = year_data.get('excess_fees', 0)
            
            row.update({
                'Lease Payment': f"${lease_payment:,.0f}",
                'Maintenance': f"${maintenance:,.0f}",
                'Insurance': f"${insurance:,.0f}",
                'Fuel/Energy': f"${fuel_energy:,.0f}",
                'Excess Fees': f"${excess_fees:,.0f}",
            })
            
            operating_total = lease_payment + maintenance + insurance + fuel_energy + excess_fees
        
        row['Operating Total'] = f"${operating_total:,.0f}"
        breakdown_data.append(row)
    
    # Display table
    df_breakdown = pd.DataFrame(breakdown_data)
    st.dataframe(df_breakdown, use_container_width=True, hide_index=True)
    
    # Summary info
    final_mileage = current_mileage + (annual_mileage * bounded_years)
    st.success(f"✅ **Analysis Period:** {bounded_years} years | **Mileage:** {current_mileage:,} → {final_mileage:,} miles")
    
    # Depreciation summary for purchases
    if transaction_type == 'Purchase' and annual_breakdown:
        st.markdown("---")
        st.subheader("📈 Depreciation Summary")
        st.info("💡 **Opportunity cost** - Not a direct annual expense")
        
        # Only sum depreciation for the bounded period
        bounded_depreciation = sum(
            annual_breakdown[i].get('annual_depreciation', annual_breakdown[i].get('depreciation', 0)) 
            for i in range(min(bounded_years, len(annual_breakdown)))
        )
        st.metric("Total Depreciation", f"${bounded_depreciation:,.0f}", 
                 help=f"Total value loss over {bounded_years}-year period")

def display_recommendations_tab(results: Dict[str, Any], vehicle_data: Dict[str, Any]):
    """Display recommendations and insights"""
    
    st.subheader("🎯 Recommendations & Insights")
    
    # Affordability assessment
    affordability = results.get('affordability', {})
    
    if affordability:
        income_percentage = affordability.get('percentage_of_income', 0)
        is_affordable = affordability.get('is_affordable', False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if is_affordable:
                st.success(f"✅ **Budget Friendly**")
                st.write(f"This vehicle represents {income_percentage:.1f}% of your income, which is within recommended guidelines.")
            else:
                st.warning(f"⚠️ **Budget Consideration**")
                st.write(f"This vehicle represents {income_percentage:.1f}% of your income, which may strain your budget.")
        
        with col2:
            monthly_impact = affordability.get('monthly_budget_impact', 0)
            st.metric("Monthly Budget Impact", f"${monthly_impact:,.0f}")
    
    # Cost optimization suggestions
    st.markdown("#### 💰 Cost Optimization Tips")
    
    suggestions = []
    
    # Generic suggestions based on transaction type
    if vehicle_data.get('transaction_type') == 'Purchase':
        suggestions.extend([
            "🔧 **Maintenance**: Use independent shops for routine maintenance to save 20-30%",
            "⛽ **Fuel**: Consider fuel-efficient driving techniques to improve MPG by 10-15%",
            "🛡️ **Insurance**: Shop around annually - savings of $200-500 possible",
            "📅 **Timing**: Proper maintenance timing can prevent costly repairs"
        ])
    else:  # Lease
        suggestions.extend([
            "📏 **Mileage**: Monitor mileage closely to avoid overage fees",
            "🔧 **Maintenance**: Keep all service records for lease return",
            "🛡️ **Protection**: Consider gap insurance for lease coverage",
            "⏰ **Early Return**: Understand early termination costs before making changes"
        ])
    
    for suggestion in suggestions:
        st.markdown(suggestion)
    
    # Comparison recommendation
    st.markdown("#### 🔄 Next Steps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Consider Comparing:**")
        st.write("• Similar vehicles from other manufacturers")
        st.write("• Different trim levels of the same model")
        st.write("• Lease vs purchase for this vehicle")
    
    with col2:
        st.markdown("**Before You Decide:**")
        st.write("• Test drive the vehicle")
        st.write("• Get insurance quotes")
        st.write("• Negotiate purchase/lease terms")
        st.write("• Consider certified pre-owned options")
