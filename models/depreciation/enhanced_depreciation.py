# models/depreciation/enhanced_depreciation.py

"""
Enhanced Depreciation Model - Market-Realistic Version
Based on actual market data from KBB, Edmunds, and iSeeCars depreciation studies
Updated for 2024-2025 with proper Tesla/EV handling
"""

from typing import List, Dict, Any
import math

class EnhancedDepreciationModel:
    """Enhanced depreciation model with market-validated rates and EV support"""
    
    def __init__(self):
        # UPDATED: Brand depreciation multipliers with Tesla
        self.brand_multipliers = {
            # Premium Value Retention (0.75-0.85)
            'Toyota': 0.78,
            'Honda': 0.80,
            'Lexus': 0.75,
            'Porsche': 0.82,
            
            # Good Value Retention (0.85-0.95)  
            'Subaru': 0.88,
            'Mazda': 0.90,
            'Hyundai': 0.92,
            'Kia': 0.94,
            'Acura': 0.85,
            
            # Tesla - Moderate EV retention (0.90)
            'Tesla': 0.90,  # Better than luxury, accounts for tech updates
            
            # Average Retention (0.95-1.05)
            'Ford': 1.00,
            'Chevrolet': 1.02,
            'GMC': 1.00,
            'Buick': 0.98,
            'Nissan': 1.03,
            'Infiniti': 1.08,
            'Volvo': 1.05,
            
            # Below Average Retention (1.05-1.20)
            'Volkswagen': 1.12,
            'Mini': 1.15,
            'Jaguar': 1.18,
            'Land Rover': 1.20,
            
            # Poor Retention - Luxury (1.15-1.30)
            'BMW': 1.22,
            'Mercedes-Benz': 1.25,
            'Audi': 1.18,
            'Cadillac': 1.20,
            'Lincoln': 1.25,
            'Genesis': 1.15,
            
            # Poor Retention - Others (1.20-1.35)
            'Chrysler': 1.30,
            'Dodge': 1.28,
            'Jeep': 1.10,
            'Ram': 1.05,
            'Fiat': 1.35,
            'Alfa Romeo': 1.32,
            
            # Other EV Brands
            'Rivian': 1.25,
            'Lucid': 1.30,
        }
        
        # UPDATED: Segment-specific depreciation curves with electric and hybrid segments
        self.segment_curves = {
            # NEW: Electric vehicles segment (includes Tesla)
            'electric': {
                1: 0.18,   2: 0.30,   3: 0.38,   4: 0.44,   5: 0.50,
                6: 0.55,   7: 0.59,   8: 0.63,   9: 0.66,   10: 0.69,
                11: 0.71,  12: 0.73,  13: 0.74,  14: 0.75,  15: 0.76
            },
            
            # NEW: Hybrid vehicles segment (Prius, Accord Hybrid, etc.)
            # Hybrids hold value better than gas but worse than pure EVs initially
            'hybrid': {
                1: 0.14,   2: 0.24,   3: 0.32,   4: 0.38,   5: 0.44,
                6: 0.49,   7: 0.53,   8: 0.57,   9: 0.60,   10: 0.63,
                11: 0.65,  12: 0.67,  13: 0.68,  14: 0.69,  15: 0.70
            },
            
            # Luxury vehicles
            'luxury': {
                1: 0.18,   2: 0.31,   3: 0.40,   4: 0.47,   5: 0.53,
                6: 0.58,   7: 0.62,   8: 0.66,   9: 0.69,   10: 0.72,
                11: 0.74,  12: 0.76,  13: 0.77,  14: 0.78,  15: 0.79
            },
            
            # Trucks - excellent retention
            'truck': {
                1: 0.10,   2: 0.18,   3: 0.25,   4: 0.31,   5: 0.36,
                6: 0.41,   7: 0.45,   8: 0.48,   9: 0.51,   10: 0.54,
                11: 0.56,  12: 0.58,  13: 0.59,  14: 0.60,  15: 0.61
            },
            
            # SUVs - good retention
            'suv': {
                1: 0.13,   2: 0.23,   3: 0.31,   4: 0.38,   5: 0.44,
                6: 0.49,   7: 0.53,   8: 0.57,   9: 0.60,   10: 0.63,
                11: 0.65,  12: 0.67,  13: 0.68,  14: 0.69,  15: 0.70
            },
            
            # Sports cars
            'sports': {
                1: 0.16,   2: 0.27,   3: 0.36,   4: 0.43,   5: 0.49,
                6: 0.54,   7: 0.58,   8: 0.62,   9: 0.65,   10: 0.68,
                11: 0.70,  12: 0.72,  13: 0.73,  14: 0.74,  15: 0.75
            },
            
            # Compact cars
            'compact': {
                1: 0.15,   2: 0.25,   3: 0.33,   4: 0.40,   5: 0.46,
                6: 0.51,   7: 0.55,   8: 0.59,   9: 0.62,   10: 0.65,
                11: 0.67,  12: 0.69,  13: 0.70,  14: 0.71,  15: 0.72
            },
            
            # Standard sedans
            'sedan': {
                1: 0.16,   2: 0.27,   3: 0.35,   4: 0.42,   5: 0.48,
                6: 0.53,   7: 0.57,   8: 0.61,   9: 0.64,   10: 0.67,
                11: 0.69,  12: 0.71,  13: 0.72,  14: 0.73,  15: 0.74
            },
            
            # Economy cars
            'economy': {
                1: 0.18,   2: 0.30,   3: 0.39,   4: 0.47,   5: 0.54,
                6: 0.60,   7: 0.64,   8: 0.68,   9: 0.71,   10: 0.74,
                11: 0.76,  12: 0.78,  13: 0.79,  14: 0.80,  15: 0.81
            }
        }
        
        # Model-specific adjustments
        self.high_retention_models = {
            'Toyota': ['4Runner', 'Tacoma', 'Tundra', 'Land Cruiser', 'Sequoia'],
            'Honda': ['Pilot', 'Ridgeline', 'Odyssey'],
            'Subaru': ['Outback', 'Forester', 'Crosstrek'],
            'Jeep': ['Wrangler', 'Gladiator'],
            'Ford': ['F-150', 'Bronco'],
            'Chevrolet': ['Silverado', 'Corvette'],
            'Porsche': ['911', 'Cayenne']
        }
        
        self.poor_retention_models = {
            'BMW': ['7 Series', 'X7', 'i3'],
            'Mercedes-Benz': ['S-Class', 'E-Class', 'GLS'],
            'Audi': ['A8', 'Q7', 'Q8'],
            'Cadillac': ['Escalade', 'CT6'],
            'Lincoln': ['Navigator', 'Aviator'],
            'Jaguar': ['XJ', 'F-Type'],
            'Land Rover': ['Range Rover', 'Discovery']
        }

    def _classify_vehicle_segment(self, vehicle_make: str, vehicle_model: str) -> str:
        """COMPREHENSIVE: Classify vehicle segment with ALL EV and HYBRID detection from database"""
        model_lower = vehicle_model.lower()
        make_lower = vehicle_make.lower()
        
        # PRIORITY 1: FULL ELECTRIC VEHICLES (BEV)
        # Tesla - all models are electric
        if make_lower == 'tesla':
            return 'electric'
        
        # All-electric brands
        if make_lower in ['rivian', 'lucid', 'polestar', 'fisker']:
            return 'electric'
        
        # Electric models by keyword detection (comprehensive list from all database files)
        electric_keywords = [
            # Tesla models
            'model s', 'model 3', 'model x', 'model y', 'cybertruck',
            # Nissan
            'leaf', 'ariya',
            # Chevrolet/GM
            'bolt ev', 'bolt euv', 'equinox ev', 'blazer ev', 'silverado ev', 'lyriq', 'hummer ev',
            # Hyundai/Kia/Genesis
            'ioniq electric', 'ioniq 5', 'ioniq 6', 'kona electric', 'niro ev', 'soul ev', 
            'ev6', 'ev9', 'gv60', 'gv70 electric', 'g80 electric',
            # BMW
            'i3', 'i4', 'i5', 'i7', 'ix', 'ix1', 'ix2', 'ix3', 'ixm60',
            # Audi
            'e-tron', 'e-tron gt', 'q4 e-tron', 'q5 e-tron', 'q6 e-tron', 'q8 e-tron',
            # Porsche
            'taycan',
            # Volkswagen
            'id.3', 'id.4', 'id.5', 'id.6', 'id.7', 'id.buzz',
            # Ford
            'mustang mach-e', 'mach-e', 'f-150 lightning', 'lightning', 'e-transit',
            # Mercedes-Benz
            'eqb', 'eqc', 'eqe', 'eqs', 'eqv',
            # Volvo
            'c40 recharge', 'xc40 recharge',
            # Honda/Acura
            'prologue', 'zdx',
            # Toyota/Lexus
            'bz4x', 'rz',
            # Subaru
            'solterra',
            # Mazda
            'mx-30',
            # Jaguar
            'i-pace',
            # Mini
            'cooper se', 'mini electric',
            # Cadillac
            'lyriq', 'escalade iq',
            # Rivian
            'r1t', 'r1s',
            # Lucid
            'air', 'gravity',
            # Fisker
            'ocean',
            # Genesis
            'electrified g80', 'electrified gv70',
            # General keywords
            ' electric', ' ev ', 'bev'
        ]
        
        if any(keyword in model_lower for keyword in electric_keywords):
            return 'electric'
        
        # PRIORITY 2: HYBRID VEHICLES (HEV, PHEV, Mild Hybrid)
        # Comprehensive hybrid detection from all database files
        
        # Models that are ALWAYS hybrid (no gas version)
        always_hybrid_models = [
            'prius',  # All Prius except Prime (which is still hybrid)
            'insight',  # Honda Insight
            'sienna',  # Toyota Sienna (hybrid-only since 2021)
            'maverick',  # Ford Maverick (hybrid standard on base)
        ]
        
        if any(model in model_lower for model in always_hybrid_models):
            return 'hybrid'
        
        # Hybrid keyword detection - comprehensive from all databases
        if 'hybrid' in model_lower:
            return 'hybrid'
        
        # Specific hybrid models from database files
        hybrid_models = [
            # Toyota
            'prius prime', 'prius plug-in', 'camry hybrid', 'corolla hybrid', 
            'rav4 hybrid', 'rav4 prime', 'highlander hybrid', 'venza', 
            'crown hybrid', 'avalon hybrid', 'sienna hybrid',
            # Lexus
            'rx hybrid', 'nx hybrid', 'es hybrid', 'ls hybrid', 'ux hybrid',
            'lc hybrid', 'gx hybrid', 'rx450h', 'nx450h', 'es300h', 'ls500h',
            # Honda
            'accord hybrid', 'cr-v hybrid', 'pilot hybrid', 'insight', 'clarity',
            # Hyundai
            'sonata hybrid', 'elantra hybrid', 'tucson hybrid', 'santa fe hybrid',
            'ioniq hybrid', 'kona hybrid',
            # Kia
            'niro hybrid', 'sorento hybrid', 'sportage hybrid', 'optima hybrid',
            'k5 hybrid', 'carnival hybrid',
            # Ford
            'fusion hybrid', 'escape hybrid', 'explorer hybrid', 'maverick hybrid',
            'f-150 hybrid', 'c-max', 'fusion energi',
            # Lincoln
            'aviator hybrid', 'corsair hybrid', 'nautilus hybrid', 'mkz hybrid',
            # Chevrolet
            'malibu hybrid', 'volt',
            # Buick
            'lacrosse hybrid',
            # Nissan
            'rogue hybrid', 'pathfinder hybrid', 'altima hybrid',
            # Chrysler/Dodge/Jeep
            'pacifica hybrid', 'wrangler 4xe', 'grand cherokee 4xe', 'compass 4xe',
            # Acura
            'mdx hybrid', 'nsx', 'rlx hybrid', 'ilx hybrid',
            # BMW
            '330e', '530e', '740e', 'x3 xdrive30e', 'x5 xdrive45e', 
            '225xe', 'i8', '745e',
            # Mercedes-Benz
            'c300 hybrid', 'e300 hybrid', 's500 hybrid', 'gle hybrid',
            'glc hybrid', 'gls hybrid',
            # Audi
            'a3 e-tron', 'a8 hybrid', 'q5 hybrid', 'q7 e-tron',
            # Porsche
            'cayenne hybrid', 'cayenne e-hybrid', 'panamera hybrid', 
            'panamera e-hybrid', '918',
            # Volkswagen
            'jetta hybrid', 'touareg hybrid',
            # Volvo
            'xc60 recharge', 'xc90 recharge', 's60 recharge', 's90 recharge',
            'v60 recharge', 'v90 recharge',
            # Mini
            'countryman phev', 'cooper s e',
            # Land Rover
            'range rover hybrid', 'range rover sport hybrid', 'discovery hybrid',
            # Subaru
            'crosstrek hybrid',
            # General keywords
            'plug-in hybrid', 'phev', 'e-hybrid', 'recharge', 'energi', '4xe'
        ]
        
        if any(hybrid_model in model_lower for hybrid_model in hybrid_models):
            return 'hybrid'
        
        # PRIORITY 3: Check luxury brands (but not if already classified as EV/Hybrid)
        if make_lower in ['bmw', 'mercedes-benz', 'audi', 'lexus', 'acura', 
                          'infiniti', 'cadillac', 'lincoln', 'jaguar', 'land rover',
                          'porsche', 'maserati', 'alfa romeo', 'genesis']:
            return 'luxury'
        
        # PRIORITY 4: Check trucks
        if any(term in model_lower for term in [
            'f-150', 'f-250', 'f-350', 'silverado', 'sierra', 'ram 1500', 'ram 2500',
            'tundra', 'tacoma', 'frontier', 'ridgeline', 'gladiator', 'ranger',
            'colorado', 'canyon', 'titan'
        ]):
            return 'truck'
        
        # PRIORITY 5: Check SUVs
        if any(term in model_lower for term in [
            'suburban', 'tahoe', 'yukon', 'escalade', 'navigator',
            'pilot', 'highlander', 'rav4', 'cr-v', 'explorer', 'expedition',
            'escape', 'equinox', 'traverse', 'pathfinder', 'armada',
            'palisade', 'telluride', 'sorento', 'santa fe', 'tucson',
            'cx-5', 'cx-9', 'outback', 'forester', 'ascent',
            'wrangler', 'grand cherokee', 'durango', 'atlas', 'tiguan'
        ]):
            return 'suv'
        
        # PRIORITY 6: Check sports cars
        if any(term in model_lower for term in [
            'corvette', 'mustang', 'camaro', 'challenger', 'charger',
            '911', 'cayman', 'boxster', 'z4', 'supra', 'miata', 'mx-5',
            'gt-r', '370z', '400z', 'brz', 'gr86'
        ]):
            return 'sports'
        
        # PRIORITY 7: Check compact cars
        if any(term in model_lower for term in [
            'civic', 'corolla', 'elantra', 'sentra', 'forte', 'jetta',
            'golf', 'mazda3', 'impreza', 'crosstrek'
        ]):
            return 'compact'
        
        # PRIORITY 8: Check economy cars
        if any(term in model_lower for term in [
            'spark', 'mirage', 'rio', 'versa', 'accent', 'yaris', 'fit'
        ]):
            return 'economy'
        
        # Default: sedan
        return 'sedan'

    def _get_cumulative_depreciation_rate(self, year: int, segment: str) -> float:
        """Get cumulative depreciation rate for a given year and segment"""
        curve = self.segment_curves.get(segment, self.segment_curves['sedan'])
        
        if year <= 15:
            return curve.get(year, curve[15])
        else:
            # Beyond 15 years, minimal additional depreciation
            return min(0.96, curve[15] + ((year - 15) * 0.005))

    def _calculate_mileage_impact(self, annual_mileage: int) -> float:
        """Calculate mileage impact on depreciation"""
        standard_mileage = 12000
        
        if annual_mileage <= 100:
            return 0.70  # Very low mileage bonus
        elif annual_mileage < 8000:
            # Low mileage: 70% to 90%
            ratio = (annual_mileage - 100) / 7900
            return 0.70 + (ratio * 0.20)
        elif annual_mileage <= standard_mileage:
            # Below average to standard: 90% to 100%
            ratio = (annual_mileage - 8000) / 4000
            return 0.90 + (ratio * 0.10)
        elif annual_mileage <= 15000:
            # Slightly above average: 100% to 110%
            ratio = (annual_mileage - standard_mileage) / 3000
            return 1.00 + (ratio * 0.10)
        elif annual_mileage <= 20000:
            # High mileage: 110% to 125%
            ratio = (annual_mileage - 15000) / 5000
            return 1.10 + (ratio * 0.15)
        else:
            # Very high mileage: capped at 140%
            return min(1.40, 1.25 + ((annual_mileage - 20000) / 20000 * 0.15))

    def _apply_model_specific_adjustments(self, make: str, model: str, base_multiplier: float) -> float:
        """Apply model-specific adjustments"""
        # Check high retention models
        if make in self.high_retention_models:
            if any(model_name.lower() in model.lower() for model_name in self.high_retention_models[make]):
                return base_multiplier * 0.88  # 12% better retention
        
        # Check poor retention models
        if make in self.poor_retention_models:
            if any(model_name.lower() in model.lower() for model_name in self.poor_retention_models[make]):
                return base_multiplier * 1.12  # 12% worse retention
        
        return base_multiplier

    def calculate_depreciation_schedule(self, initial_value: float, vehicle_make: str, 
                                    vehicle_model: str, model_year: int, 
                                    annual_mileage: int, years: int) -> List[Dict[str, Any]]:
        """
        Calculate depreciation schedule with refined rates
        FIXED: Now handles current year vehicles with existing mileage properly
        """
        from datetime import datetime
        current_year = datetime.now().year
        vehicle_age_at_start = current_year - model_year
        
        segment = self._classify_vehicle_segment(vehicle_make, vehicle_model)
        brand_multiplier = self.brand_multipliers.get(vehicle_make, 1.0)
        adjusted_brand_multiplier = self._apply_model_specific_adjustments(
            vehicle_make, vehicle_model, brand_multiplier
        )
        mileage_multiplier = self._calculate_mileage_impact(annual_mileage)
        
        schedule = []
        
        # CRITICAL FIX: Calculate starting value for current year vehicles with mileage
        if vehicle_age_at_start == 0:
            # This is a current year vehicle - check if it has existing mileage
            # We need to estimate what the current mileage is based on time into the year
            
            # Assume mileage accumulates proportionally through the year
            # For a brand new purchase, starting mileage would be ~0-100 (delivery miles)
            # For a current year used vehicle, it could have significant mileage
            
            # If annual_mileage is given, we can estimate current mileage on a current year vehicle
            # However, for the depreciation schedule, we're looking at FUTURE depreciation
            # So the "initial_value" passed in should already account for any current depreciation
            
            # The schedule will show depreciation going forward from this point
            starting_value = initial_value
        else:
            # For used vehicles purchased in a later year, the initial_value is already
            # the purchase price (current market value), not the original MSRP
            starting_value = initial_value
        
        # Calculate year-by-year depreciation
        for year in range(1, years + 1):
            # Determine the vehicle's age at this point in ownership
            vehicle_age_at_this_year = vehicle_age_at_start + year
            
            # Get cumulative depreciation rate from original MSRP for this vehicle age
            base_cumulative_rate = self._get_cumulative_depreciation_rate(
                vehicle_age_at_this_year, segment
            )
            adjusted_rate = base_cumulative_rate * adjusted_brand_multiplier * mileage_multiplier
            
            # Apply caps
            max_depreciation = {
                'luxury': 0.90, 'electric': 0.92, 'hybrid': 0.82, 'economy': 0.88,
                'sedan': 0.85, 'compact': 0.85, 'suv': 0.82,
                'truck': 0.80, 'sports': 0.88
            }
            cap = max_depreciation.get(segment, 0.85)
            adjusted_rate = min(adjusted_rate, cap)
            
            # CRITICAL FIX: For current year vehicles, we need to handle year 1 specially
            if vehicle_age_at_start == 0 and year == 1:
                # This is the first year of ownership for a current year vehicle
                # The vehicle will age from 0 to 1 year old during this year
                
                # Value at end of year 1 (when vehicle is 1 year old)
                new_value = starting_value * (1 - adjusted_rate)
                
                # Annual depreciation is the drop during this year
                annual_depreciation = starting_value - new_value
                
            else:
                # Standard calculation for year 2+ or for vehicles that started used
                if year == 1:
                    # First year of ownership (but vehicle may already be used)
                    # Depreciate from starting value based on the full cumulative rate
                    new_value = starting_value * (1 - adjusted_rate)
                    annual_depreciation = starting_value - new_value
                else:
                    # Subsequent years - calculate incremental depreciation
                    previous_value = schedule[-1]['vehicle_value']
                    
                    # Get previous year's cumulative rate
                    prev_vehicle_age = vehicle_age_at_start + (year - 1)
                    prev_cumulative_rate = self._get_cumulative_depreciation_rate(
                        prev_vehicle_age, segment
                    )
                    prev_adjusted_rate = prev_cumulative_rate * adjusted_brand_multiplier * mileage_multiplier
                    prev_adjusted_rate = min(prev_adjusted_rate, cap)
                    
                    # Calculate new value and annual depreciation
                    # We're moving from one cumulative rate to the next
                    new_value = starting_value * (1 - adjusted_rate)
                    annual_depreciation = previous_value - new_value
            
            schedule.append({
                'year': year,
                'vehicle_value': new_value,
                'annual_depreciation': annual_depreciation,
                'cumulative_depreciation': starting_value - new_value,
                'depreciation_rate': adjusted_rate,
                'vehicle_age': vehicle_age_at_this_year,
                'segment': segment,
                'brand_multiplier': adjusted_brand_multiplier,
                'mileage_multiplier': mileage_multiplier
            })
        
        return schedule
    
    def estimate_current_value(self, initial_value: float, vehicle_make: str, 
                            vehicle_model: str, vehicle_age: int, 
                            current_mileage: int) -> float:
        """
        Estimate current value of existing vehicle
        FIXED: Now properly handles current year vehicles with mileage
        """
        
        # Classify vehicle segment
        segment = self._classify_vehicle_segment(vehicle_make, vehicle_model)
        brand_multiplier = self.brand_multipliers.get(vehicle_make, 1.0)
        adjusted_brand_multiplier = self._apply_model_specific_adjustments(
            vehicle_make, vehicle_model, brand_multiplier
        )
        
        # CRITICAL FIX: Handle current year vehicles with mileage
        if vehicle_age == 0:
            # Current year vehicle - apply mileage-based depreciation
            
            if current_mileage <= 100:
                # Essentially brand new - minimal depreciation (delivery miles)
                return initial_value * 0.98
            
            # Get the 1-year baseline depreciation rate for this segment
            one_year_baseline = {
                'luxury': 0.15,
                'truck': 0.10,
                'suv': 0.13,
                'sports': 0.16,
                'compact': 0.14,
                'economy': 0.17,
                'sedan': 0.15,
                'electric': 0.18,
                'hybrid': 0.14
            }
            baseline_rate = one_year_baseline.get(segment, 0.15)
            
            # Calculate depreciation based on mileage progression to 1-year baseline
            # Uses a smooth curve that approaches but doesn't exceed the 1-year rate
            if current_mileage <= 1000:
                # 100-1,000 miles: 2-5% (demo/dealer transfer)
                mileage_factor = (current_mileage - 100) / 900
                depreciation_rate = 0.02 + (mileage_factor * 0.03)
                
            elif current_mileage <= 5000:
                # 1,001-5,000 miles: 5-8% (test drive/demo level)
                mileage_factor = (current_mileage - 1000) / 4000
                depreciation_rate = 0.05 + (mileage_factor * 0.03)
                
            elif current_mileage <= 12000:
                # 5,001-12,000 miles: Scale from 8% to 70% of 1-year baseline
                mileage_factor = (current_mileage - 5000) / 7000
                target_rate = baseline_rate * 0.70
                depreciation_rate = 0.08 + (mileage_factor * (target_rate - 0.08))
                
            elif current_mileage <= 20000:
                # 12,001-20,000 miles: Scale from 70% to 90% of 1-year baseline
                mileage_factor = (current_mileage - 12000) / 8000
                start_rate = baseline_rate * 0.70
                target_rate = baseline_rate * 0.90
                depreciation_rate = start_rate + (mileage_factor * (target_rate - start_rate))
                
            else:
                # 20,000+ miles: Approach but cap at 95% of 1-year baseline
                # This ensures graceful convergence to the 1-year rate
                excess_miles = min(current_mileage - 20000, 20000)
                mileage_factor = excess_miles / 20000
                start_rate = baseline_rate * 0.90
                cap_rate = baseline_rate * 0.95
                depreciation_rate = start_rate + (mileage_factor * (cap_rate - start_rate))
            
            # Apply brand multiplier
            final_rate = depreciation_rate * adjusted_brand_multiplier
            
            # Calculate and return current value
            current_value = initial_value * (1 - final_rate)
            return max(current_value, initial_value * 0.50)  # Floor at 50% of original
        
        # For vehicles 1+ years old, use the existing annual mileage-based logic
        if vehicle_age < 1:
            return initial_value
        
        # Calculate annual mileage for multi-year-old vehicles
        annual_mileage = current_mileage / vehicle_age
        mileage_multiplier = self._calculate_mileage_impact(annual_mileage)
        
        # Get cumulative depreciation rate for the vehicle's age
        base_rate = self._get_cumulative_depreciation_rate(vehicle_age, segment)
        final_rate = base_rate * adjusted_brand_multiplier * mileage_multiplier
        
        # Apply caps
        max_depreciation = {
            'luxury': 0.90, 'electric': 0.92, 'hybrid': 0.82, 'economy': 0.88,
            'sedan': 0.85, 'compact': 0.85, 'suv': 0.82,
            'truck': 0.80, 'sports': 0.88
        }
        cap = max_depreciation.get(segment, 0.85)
        final_rate = min(final_rate, cap)
        
        current_value = initial_value * (1 - final_rate)
        return max(current_value, initial_value * 0.10)  # Floor at 10% of original


    def _get_retention_rating(self, multiplier: float) -> str:
        """Get retention rating from multiplier"""
        if multiplier <= 0.85:
            return "Excellent"
        elif multiplier <= 0.95:
            return "Good"
        elif multiplier <= 1.05:
            return "Average"
        elif multiplier <= 1.15:
            return "Below Average"
        else:
            return "Poor"

    def get_depreciation_insights(self, vehicle_make: str, vehicle_model: str, 
                                 initial_value: float, years: int = 5) -> Dict[str, Any]:
        """Get depreciation insights for a vehicle"""
        
        segment = self._classify_vehicle_segment(vehicle_make, vehicle_model)
        brand_multiplier = self.brand_multipliers.get(vehicle_make, 1.0)
        adjusted_multiplier = self._apply_model_specific_adjustments(
            vehicle_make, vehicle_model, brand_multiplier
        )
        
        # Calculate scenarios
        scenarios = {}
        for desc, mileage in [('Low', 8000), ('Average', 12000), ('High', 18000)]:
            schedule = self.calculate_depreciation_schedule(
                initial_value, vehicle_make, vehicle_model, 2024, mileage, years
            )
            scenarios[desc.lower()] = schedule[-1]['vehicle_value'] if schedule else 0
        
        return {
            'market_segment': segment,
            'brand_adjustment': adjusted_multiplier,
            'scenarios': scenarios,
            'retention_rating': self._get_retention_rating(adjusted_multiplier),
            'key_insight': f"{vehicle_make} {vehicle_model} classified as {segment} with {self._get_retention_rating(adjusted_multiplier).lower()} value retention"
        }

    def _get_retention_rating(self, brand_multiplier: float) -> str:
        """Enhanced retention rating"""
        if brand_multiplier <= 0.80:
            return "Exceptional"
        elif brand_multiplier <= 0.90:
            return "Excellent" 
        elif brand_multiplier <= 1.00:
            return "Good"
        elif brand_multiplier <= 1.10:
            return "Average"
        elif brand_multiplier <= 1.20:
            return "Below Average"
        else:
            return "Poor"

    def _generate_enhanced_insights(self, make: str, model: str, segment: str, 
                                  brand_multiplier: float) -> List[str]:
        """Generate enhanced insights about depreciation"""
        insights = []
        
        # Brand insights
        if brand_multiplier <= 0.85:
            insights.append(f"{make} vehicles are known for exceptional value retention")
        elif brand_multiplier >= 1.20:
            insights.append(f"{make} vehicles typically experience faster depreciation, especially luxury models")
        
        # Segment insights  
        segment_advice = {
            'luxury': "Luxury vehicles depreciate rapidly in first 3-5 years, then stabilize",
            'electric': "Electric vehicles face technology obsolescence risk affecting resale value",
            'truck': "Trucks typically hold value very well, especially popular models like F-150",
            'suv': "SUVs generally maintain strong resale value due to continued popularity",
            'compact': "Compact cars offer predictable, moderate depreciation rates",
            'sports': "Sports cars vary widely - iconic models may appreciate, others depreciate quickly"
        }
        if segment in segment_advice:
            insights.append(segment_advice[segment])
        
        # Model-specific insights
        if make in self.high_retention_models:
            if any(model_name.lower() in model.lower() for model_name in self.high_retention_models[make]):
                insights.append(f"The {model} is a high-demand model with above-average value retention")
        
        # General insights
        insights.append("Mileage significantly impacts resale value - consider driving patterns carefully")
        insights.append("Well-maintained vehicles with service records depreciate more slowly")
        
        return insights