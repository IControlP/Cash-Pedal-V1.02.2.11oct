# utils/used_vehicle_estimator.py

from datetime import datetime
from typing import Dict, Any, Optional
import streamlit as st
from models.depreciation.enhanced_depreciation import EnhancedDepreciationModel

# Import function-based database access (not class-based)
try:
    from data.vehicle_database import get_trims_for_vehicle, get_vehicle_trim_price
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    def get_trims_for_vehicle(make, model, year):
        return {}
    def get_vehicle_trim_price(make, model, year, trim):
        return None

# utils/used_vehicle_estimator.py

from datetime import datetime
from typing import Dict, Any, Optional
import streamlit as st
from models.depreciation.enhanced_depreciation import EnhancedDepreciationModel

# Import function-based database access (not class-based)
try:
    from data.vehicle_database import get_trims_for_vehicle, get_vehicle_trim_price
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    def get_trims_for_vehicle(make, model, year):
        return {}
    def get_vehicle_trim_price(make, model, year, trim):
        return None

class UsedVehicleEstimator:
    """
    Estimates current market value for used vehicles based on depreciation calculations
    """
    
    def __init__(self):
        self.depreciation_model = EnhancedDepreciationModel()
        self.current_year = datetime.now().year
    
    def is_used_vehicle(self, year: int, current_mileage: int) -> bool:
        """
        Determine if a vehicle is considered used based on year and mileage
        
        Args:
            year: Model year of the vehicle
            current_mileage: Current odometer reading
            
        Returns:
            bool: True if vehicle is considered used
        """
        # Vehicle is used if:
        # 1. It's from a previous model year, OR
        # 2. It's a current year vehicle with significant mileage (> 1000 miles)
        
        if year < self.current_year:
            return True
        elif year == self.current_year and current_mileage > 1000:
            return True
        else:
            return False
    
    def estimate_current_value(self, make: str, model: str, year: int, 
                              trim: str, current_mileage: int) -> Optional[float]:
        """
        Estimate the current market value of a used vehicle
        
        Args:
            make: Vehicle manufacturer
            model: Vehicle model
            year: Model year
            trim: Trim level
            current_mileage: Current odometer reading
            
        Returns:
            float: Estimated current value or None if cannot estimate
        """
        try:
            # Get original MSRP from database
            original_msrp = self._get_original_msrp(make, model, year, trim)
            
            if not original_msrp or original_msrp <= 0:
                return None
            
            # Calculate vehicle age
            vehicle_age = self.current_year - year
            
            # For current year vehicles with low mileage, apply minimal depreciation
            if vehicle_age == 0 and current_mileage <= 1000:
                # Very light depreciation for nearly new vehicles
                return original_msrp * 0.95
            
            # Use depreciation model to calculate current value
            estimated_value = self.depreciation_model.estimate_current_value(
                initial_value=original_msrp,
                vehicle_make=make,
                vehicle_model=model,
                vehicle_age=vehicle_age,
                current_mileage=current_mileage
            )
            
            # Apply reasonable bounds
            # Minimum value: 10% of original MSRP
            min_value = original_msrp * 0.10
            if estimated_value < min_value:
                estimated_value = min_value
            
            # Ensure maximum reasonable value (no more than original MSRP)
            if estimated_value > original_msrp:
                estimated_value = original_msrp
            
            return round(estimated_value, 0)
            
        except Exception as e:
            st.warning(f"Could not estimate vehicle value: {str(e)}")
            return None

    def _get_original_msrp(self, make: str, model: str, year: int, trim: str) -> Optional[float]:
        """
        Get original MSRP for the vehicle from the database
        
        Args:
            make: Vehicle manufacturer
            model: Vehicle model  
            year: Model year
            trim: Trim level
            
        Returns:
            float: Original MSRP or None if not found
        """
        try:
            if not DATABASE_AVAILABLE:
                return None
            
            # Get all trims for this vehicle
            trims = get_trims_for_vehicle(make, model, year)
            
            if not trims:
                return None
            
            # Try exact trim match first
            if trim in trims:
                return trims[trim]
            
            # Try case-insensitive match
            for available_trim, price in trims.items():
                if available_trim.lower() == trim.lower():
                    return price
            
            # If no exact match, return base trim price (typically the lowest)
            if trims:
                return min(trims.values())
            
            return None
            
        except Exception as e:
            return None
    
    def get_depreciation_insights(self, make: str, model: str, year: int, 
                                current_mileage: int, estimated_value: float,
                                original_msrp: float = None) -> Dict[str, Any]:
        """
        Generate insights about the vehicle's depreciation and value
        
        Args:
            make: Vehicle manufacturer
            model: Vehicle model
            year: Model year  
            current_mileage: Current odometer reading
            estimated_value: Estimated current market value
            original_msrp: Original MSRP (optional, will look up if not provided)
            
        Returns:
            Dict containing depreciation insights
        """
        try:
            # Get original MSRP if not provided
            if original_msrp is None:
                original_msrp = self._get_original_msrp(make, model, year, "Base")
            
            if not original_msrp:
                return {}
            
            vehicle_age = self.current_year - year
            total_depreciation = original_msrp - estimated_value
            depreciation_percent = (total_depreciation / original_msrp) * 100
            
            return {
                'vehicle_age': vehicle_age,
                'original_msrp': original_msrp,
                'estimated_value': estimated_value,
                'total_depreciation': total_depreciation,
                'depreciation_percent': depreciation_percent,
                'annual_depreciation': total_depreciation / max(vehicle_age, 1),
                'mileage_assessment': self._assess_mileage(vehicle_age, current_mileage),
                'value_retention_rating': self._get_value_retention_rating(make),
                'depreciation_assessment': self._assess_depreciation(depreciation_percent, vehicle_age),
                'market_position': self._assess_market_position(estimated_value, make, model, year)
            }
            
        except Exception as e:
            return {}
    
    def _assess_mileage(self, vehicle_age: int, current_mileage: int) -> str:
        """Assess if mileage is low, average, or high for vehicle age"""
        if vehicle_age == 0:
            if current_mileage < 500:
                return "Very low mileage"
            elif current_mileage < 2000:
                return "Low mileage for current year"
            else:
                return "Higher mileage for current year"
        
        average_annual = current_mileage / vehicle_age if vehicle_age > 0 else 0
        
        if average_annual < 10000:
            return "Low mileage (below average)"
        elif average_annual < 15000:
            return "Average mileage"
        elif average_annual < 20000:
            return "Above average mileage"
        else:
            return "High mileage vehicle"
    
    def _get_value_retention_rating(self, make: str) -> str:
        """Get brand-based value retention rating"""
        # Based on brand multipliers from depreciation model
        brand_ratings = {
            'Toyota': 'Excellent', 'Lexus': 'Excellent', 'Honda': 'Excellent',
            'Porsche': 'Excellent', 'Subaru': 'Good', 'Mazda': 'Good',
            'Tesla': 'Good', 'Hyundai': 'Average', 'Kia': 'Average',
            'Ford': 'Average', 'Chevrolet': 'Below Average', 
            'Chrysler': 'Poor', 'Dodge': 'Poor'
        }
        
        return brand_ratings.get(make, 'Average')
    
    def _assess_depreciation(self, depreciation_percent: float, vehicle_age: int) -> str:
        """Assess if depreciation is better or worse than typical"""
        # Typical depreciation rates
        typical_rates = {
            1: 20, 2: 30, 3: 40, 4: 46, 5: 52
        }
        
        if vehicle_age == 0:
            if depreciation_percent < 5:
                return "Minimal depreciation (expected for new vehicle)"
            else:
                return "Higher than expected for new vehicle"
        
        expected_rate = typical_rates.get(vehicle_age, 50 + (vehicle_age - 5) * 5)
        
        if depreciation_percent < expected_rate - 10:
            return "Excellent value retention (better than average)"
        elif depreciation_percent < expected_rate + 5:
            return "Normal depreciation (on par with market)"
        else:
            return "Higher than average depreciation"
    
    def _assess_market_position(self, estimated_value: float, make: str, 
                              model: str, year: int) -> str:
        """Assess the vehicle's market position"""
        if estimated_value < 10000:
            return "Budget-friendly option"
        elif estimated_value < 25000:
            return "Mid-market value"
        elif estimated_value < 50000:
            return "Premium segment"
        else:
            return "Luxury/High-end market"

def integrate_used_vehicle_estimation():
    """
    Integration function to be called from the vehicle selection interface
    This should be added to the vehicle selection form where price input occurs
    """
    
    # Initialize the estimator
    estimator = UsedVehicleEstimator()
    
    # This would be integrated into the existing vehicle selection form
    # Example integration points:
    
    def on_vehicle_details_change(make, model, year, trim, current_mileage):
        """
        Callback function to execute when vehicle details change
        """
        if make and model and year and trim and current_mileage is not None:
            
            # Check if this is a used vehicle
            if estimator.is_used_vehicle(year, current_mileage):
                
                # Estimate current value
                estimated_value = estimator.estimate_current_value(
                    make, model, year, trim, current_mileage
                )
                
                if estimated_value:
                    # Auto-populate the purchase price field
                    st.session_state.estimated_price = estimated_value
                    
                    # Show estimation info to user
                    st.info(f"""
                    🔍 **Used Vehicle Detected**
                    
                    Estimated current market value: **${estimated_value:,.0f}**
                    
                    This estimate is based on:
                    - Vehicle age: {estimator.current_year - year} years
                    - Current mileage: {current_mileage:,} miles
                    - {make} {model} depreciation patterns
                    
                    💡 *This value has been automatically entered in the purchase price field*
                    """)
                    
                    # Get and display insights
                    insights = estimator.get_depreciation_insights(
                        make, model, year, current_mileage, estimated_value
                    )
                    
                    if insights:
                        with st.expander("📊 View Depreciation Analysis"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric("Vehicle Age", f"{insights['vehicle_age']} years")
                                st.write(f"**Mileage Assessment:** {insights['mileage_assessment']}")
                            
                            with col2:
                                st.write(f"**Value Retention:** {insights['value_retention_rating']}")
                                st.write(f"**Depreciation:** {insights['depreciation_assessment']}")
                            
                            st.write(f"**Market Position:** {insights['market_position']}")
                
                else:
                    st.warning("⚠️ Unable to estimate current value - vehicle data not found in database")
            
            else:
                # Clear any previous estimation
                if 'estimated_price' in st.session_state:
                    del st.session_state.estimated_price
    
    return on_vehicle_details_change

def enhanced_vehicle_selection_with_price_estimation():
    """
    Enhanced vehicle selection form that includes automatic price estimation
    This would replace or enhance the existing vehicle selection interface
    """
    
    estimator = UsedVehicleEstimator()
    
    st.subheader("🚗 Vehicle Selection")
    
    # Vehicle selection inputs (simplified example)
    col1, col2 = st.columns(2)
    
    with col1:
        make = st.selectbox("Make", ["Tesla", "Toyota", "Honda", "Ford", "Chevrolet"])
        year = st.selectbox("Year", list(range(2024, 2015, -1)))
    
    with col2:
        model = st.selectbox("Model", ["Model 3", "Camry", "Civic", "F-150", "Silverado"])
        trim = st.selectbox("Trim", ["Base", "Performance", "LX", "EX"])
    
    # Mileage input
    current_mileage = st.number_input(
        "Current Mileage:",
        min_value=0,
        max_value=300000,
        value=0,
        step=1000,
        help="Current odometer reading"
    )
    
    # Purchase price with auto-estimation
    purchase_price = st.number_input(
        "Purchase Price ($):",
        min_value=1000,
        max_value=200000,
        value=st.session_state.get('estimated_price', 30000),
        step=500,
        help="Actual purchase price (auto-estimated for used vehicles)"
    )
    
    # Check for used vehicle and estimate price
    if make and model and year and trim and current_mileage is not None:
        
        if estimator.is_used_vehicle(year, current_mileage):
            
            estimated_value = estimator.estimate_current_value(
                make, model, year, trim, current_mileage
            )
            
            if estimated_value:
                # Update session state for price
                st.session_state.estimated_price = estimated_value
                
                # Rerun to update the input field
                if abs(purchase_price - estimated_value) > 1000:
                    st.rerun()
                
                # Show estimation details
                st.success(f"""
                ✅ **Used Vehicle Price Estimated**
                
                Current market value: **${estimated_value:,.0f}**
                
                You can adjust this price if you have a different offer or market data.
                """)
    
    return {
        'make': make,
        'model': model, 
        'year': year,
        'trim': trim,
        'current_mileage': current_mileage,
        'purchase_price': purchase_price
    }