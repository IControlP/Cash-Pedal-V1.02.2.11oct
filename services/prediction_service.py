
"""
Main Prediction Service
Orchestrates all TCO calculations and coordinates between different models
Enhanced with detailed maintenance scheduling and FIXED EV efficiency handling
"""

from typing import Dict, Any, List
import math

from models.depreciation.enhanced_depreciation import EnhancedDepreciationModel
from models.maintenance.maintenance_utils import MaintenanceCalculator
from models.insurance.advanced_insurance import AdvancedInsuranceCalculator
from models.fuel.fuel_utils import FuelCostCalculator
from models.fuel.electric_vehicle_utils import EVCostCalculator
from services.financial_analysis import FinancialAnalysisService
from data.vehicle_database import get_vehicle_characteristics
from utils.zip_code_utils import get_regional_cost_multiplier

class PredictionService:
    """Main service for orchestrating TCO predictions"""
    
    def __init__(self):
        self.depreciation_model = EnhancedDepreciationModel()
        self.maintenance_calculator = MaintenanceCalculator()
        self.insurance_calculator = AdvancedInsuranceCalculator()
        self.fuel_calculator = FuelCostCalculator()
        self.ev_calculator = EVCostCalculator()
        self.financial_service = FinancialAnalysisService()
    
    def calculate_total_cost_of_ownership(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive TCO with proper cost separation
        FIXED: Returns corrected cost structure with out-of-pocket vs TCO separation
        """
        
        # Get vehicle characteristics
        vehicle_characteristics = get_vehicle_characteristics(
            input_data['make'], 
            input_data['model'], 
            input_data['year'],
            input_data.get('trim', None)  # Add trim parameter
        )
        
        # Get regional cost adjustments
        regional_multiplier = get_regional_cost_multiplier(
            input_data.get('zip_code', ''),
            input_data.get('state', '')
        )
        
        analysis_years = input_data.get('analysis_years', 5)
        
        # Route to appropriate calculation method
        if input_data.get('transaction_type', 'purchase').lower() == 'lease':
            return self._calculate_lease_tco(input_data, vehicle_characteristics, regional_multiplier)
        else:
            return self._calculate_purchase_tco(input_data, vehicle_characteristics, regional_multiplier)
    
    def _calculate_realistic_used_vehicle_depreciation(self, input_data: Dict[str, Any], 
                                                    initial_value: float, 
                                                    analysis_years: int) -> List[Dict[str, Any]]:
        """Calculate realistic depreciation for used vehicles starting from current value"""
        
        from datetime import datetime
        current_year = datetime.now().year
        vehicle_age_at_purchase = current_year - input_data['year']
        
        # Used vehicles depreciate differently than new vehicles
        # They follow a more gradual, linear depreciation pattern
        
        schedule = []
        current_value = initial_value  # Start with actual purchase price, not original MSRP
        
        # Used vehicle depreciation rates (much lower than new vehicles)
        if vehicle_age_at_purchase <= 3:
            # Recently used (1-3 years) - still depreciates moderately
            annual_rates = [0.08, 0.07, 0.06, 0.05, 0.04]  # 8%, 7%, 6%, 5%, 4%
        elif vehicle_age_at_purchase <= 7:
            # Mid-age used (4-7 years) - slower depreciation
            annual_rates = [0.05, 0.04, 0.04, 0.03, 0.03]  # 5%, 4%, 4%, 3%, 3%
        else:
            # Older used (8+ years) - minimal depreciation
            annual_rates = [0.03, 0.02, 0.02, 0.02, 0.02]  # 3%, 2%, 2%, 2%, 2%
        
        # Apply brand multipliers
        brand_multipliers = {
            'Toyota': 0.8, 'Honda': 0.8, 'Lexus': 0.7,  # Better retention
            'BMW': 1.2, 'Mercedes-Benz': 1.2, 'Audi': 1.1,  # Faster depreciation
            'Chevrolet': 1.0, 'Ford': 1.0, 'Hyundai': 0.9
        }
        brand_multiplier = brand_multipliers.get(input_data['make'], 1.0)
        
        for year in range(1, analysis_years + 1):
            # Use flatter depreciation curve for used vehicles
            base_rate = annual_rates[min(year - 1, len(annual_rates) - 1)]
            adjusted_rate = base_rate * brand_multiplier
            
            # Calculate depreciation for this year
            annual_depreciation = current_value * adjusted_rate
            new_value = current_value - annual_depreciation
            
            # Ensure minimum value (used vehicles retain some value)
            min_value = initial_value * 0.15  # Minimum 15% of purchase price
            new_value = max(new_value, min_value)
            annual_depreciation = current_value - new_value  # Recalculate if min value applied
            
            ownership_year = current_year + year - 1
            
            schedule.append({
                'year': year,
                'ownership_year': ownership_year,
                'vehicle_age': ownership_year - input_data['year'],
                'vehicle_value': new_value,
                'annual_depreciation': annual_depreciation,
                'depreciation_rate': adjusted_rate
            })
            
            current_value = new_value
        
        return schedule

    def _calculate_purchase_tco(self, input_data: Dict[str, Any], 
                                vehicle_characteristics: Dict[str, Any],
                                regional_multiplier: float) -> Dict[str, Any]:
        """Calculate TCO for purchase scenario with FIXED EV efficiency"""
                # DEBUG: Print what we're getting
        print(f"\n=== DEBUG PURCHASE TCO ===")
        print(f"Make: {input_data.get('make')}")
        print(f"Model: {input_data.get('model')}")
        print(f"is_electric from input_data: {input_data.get('is_electric')}")
        print(f"is_electric from vehicle_characteristics: {vehicle_characteristics.get('is_electric')}")
        print(f"electricity_rate: {input_data.get('electricity_rate')}")
        print(f"charging_preference: {input_data.get('charging_preference')}")
        print(f"fuel_price: {input_data.get('fuel_price')}")
        print(f"========================\n")
        purchase_price = input_data.get('price', input_data.get('trim_msrp', 30000))
        analysis_years = input_data.get('analysis_years', 5)
        current_mileage = input_data.get('current_mileage', 0)
        
        # Initialize category totals
        category_totals = {
            'depreciation': 0,
            'maintenance': 0,
            'insurance': 0,
            'fuel_energy': 0,
            'financing': 0
        }
        
        # Calculate depreciation schedule
        depreciation_schedule = self.depreciation_model.calculate_depreciation_schedule(
            purchase_price,                    # initial_value
            input_data['make'],                # vehicle_make
            input_data['model'],               # vehicle_model
            input_data['year'],                # model_year
            input_data['annual_mileage'],      # annual_mileage
            analysis_years                     # years
        )
        
        # Calculate maintenance schedule
        maintenance_schedule = self.maintenance_calculator.get_maintenance_schedule(
            annual_mileage=input_data['annual_mileage'],
            years=analysis_years,
            starting_mileage=current_mileage,
            vehicle_make=input_data['make'],
            driving_style=input_data.get('driving_style', 'normal'),
            vehicle_model=input_data['model']
        )
        
        # Calculate financing if applicable - FIXED to check multiple conditions
        financing_schedule = None
        # Check if financing is needed
        is_financed = (
            input_data.get('financing_enabled', False) or
            input_data.get('financing_option') == 'finance' or
            input_data.get('payment_method') == 'loan' or
            input_data.get('financing_type') == 'loan' or
            input_data.get('loan_amount', 0) > 0
        )

        if is_financed:
            loan_amount = input_data.get('loan_amount', purchase_price * 0.8)
            if loan_amount > 0:
                financing_schedule = self.financial_service.calculate_loan_payments(
                    loan_amount=loan_amount,
                    interest_rate=input_data.get('interest_rate', 5.0),
                    loan_term_years=input_data.get('loan_term', 5),
                    analysis_years=analysis_years
                )
        
        # Year-by-year breakdown
        annual_breakdown = []
        
        for year in range(1, analysis_years + 1):
            ownership_year = 2025 + (year - 1)
            
            # Depreciation
            if year == 1:
                annual_depreciation = purchase_price - depreciation_schedule[year-1]['vehicle_value']
            else:
                annual_depreciation = depreciation_schedule[year-2]['vehicle_value'] - depreciation_schedule[year-1]['vehicle_value']
            
            # Maintenance
            annual_maintenance = 0
            maintenance_activities = []
            if year <= len(maintenance_schedule):
                annual_maintenance = maintenance_schedule[year-1]['total_year_cost']
                maintenance_activities = maintenance_schedule[year-1].get('services', [])
            
            # Insurance
            annual_insurance = self.insurance_calculator.calculate_annual_premium(
                vehicle_value=depreciation_schedule[year-1]['vehicle_value'] if year <= len(depreciation_schedule) else purchase_price * 0.5,
                vehicle_make=input_data['make'],
                vehicle_year=input_data['year'],
                driver_age=input_data.get('driver_age', 35),
                state=input_data['state'],
                coverage_type=input_data.get('coverage_type', 'comprehensive'),
                annual_mileage=input_data['annual_mileage'],
                num_vehicles=input_data.get('num_household_vehicles', 2),
                regional_multiplier=regional_multiplier,
                vehicle_model=input_data['model']
            )
            
            # FIXED: Fuel/Energy costs - check both input_data AND vehicle_characteristics for is_electric
            is_electric = input_data.get('is_electric') or vehicle_characteristics.get('is_electric', False)

            # Get driving parameters
            driving_style = input_data.get('driving_style', 'normal')
            terrain = input_data.get('terrain', 'flat')

            # Driving style efficiency multipliers
            driving_style_multipliers = {
                'gentle': 1.15,     # 15% better efficiency
                'normal': 1.0,      # Baseline
                'aggressive': 0.85  # 15% worse efficiency
            }

            # Terrain efficiency multipliers
            terrain_multipliers = {
                'flat': 1.05,       # 5% better efficiency
                'hilly': 0.95       # 5% worse efficiency
            }

            # Calculate combined multiplier
            style_multiplier = driving_style_multipliers.get(driving_style, 1.0)
            terrain_multiplier = terrain_multipliers.get(terrain, 1.0)
            combined_multiplier = style_multiplier * terrain_multiplier

            if is_electric:
                # Get EV efficiency in kWh per 100 miles
                ev_efficiency = self.ev_calculator.estimate_ev_efficiency(
                    input_data['make'],
                    input_data['model'],
                    input_data['year']
                )
                
                # Apply driving adjustments to EV efficiency
                # For EVs: worse driving = MORE kWh needed, so DIVIDE by multiplier
                adjusted_ev_efficiency = ev_efficiency / combined_multiplier
                
                annual_fuel = self.ev_calculator.calculate_annual_electricity_cost(
                    annual_mileage=input_data['annual_mileage'],
                    vehicle_efficiency=adjusted_ev_efficiency,  # Use adjusted efficiency
                    electricity_rate=input_data.get('electricity_rate', 0.12),
                    charging_preference=input_data.get('charging_preference', 'mixed')
                )
            else:
                # Gas vehicle with driving adjustments
                annual_fuel = self.fuel_calculator.calculate_annual_fuel_cost(
                    annual_mileage=input_data['annual_mileage'],
                    mpg=vehicle_characteristics.get('mpg', 25),
                    fuel_price=input_data.get('fuel_price', 3.50),
                    driving_style=driving_style,
                    terrain=terrain
                )


            # Financing costs
            annual_financing = 0
            if financing_schedule and year <= len(financing_schedule):
                annual_financing = financing_schedule[year-1].get('annual_payment', 0)
            
            # Total annual cost
            total_annual = annual_depreciation + annual_maintenance + annual_insurance + annual_fuel + annual_financing
            
            # Store breakdown
            annual_breakdown.append({
                'year': year,
                'ownership_year': ownership_year,
                'vehicle_age': ownership_year - input_data['year'],
                'vehicle_model_year': input_data['year'],
                'cumulative_mileage': current_mileage + (input_data['annual_mileage'] * year),
                'depreciation': annual_depreciation,
                'maintenance': annual_maintenance,
                'maintenance_activities': maintenance_activities,
                'insurance': annual_insurance,
                'fuel_energy': annual_fuel,
                'financing': annual_financing,
                'total_annual_cost': total_annual
            })
            
            # Add to totals
            category_totals['depreciation'] += annual_depreciation
            category_totals['maintenance'] += annual_maintenance
            category_totals['insurance'] += annual_insurance
            category_totals['fuel_energy'] += annual_fuel
            category_totals['financing'] += annual_financing
        
        # Calculate final metrics
        total_tco = sum(category_totals.values())
        out_of_pocket_total = (
            category_totals['maintenance'] +
            category_totals['insurance'] +
            category_totals['fuel_energy'] +
            category_totals['financing']
        )
        
        average_annual_tco = total_tco / analysis_years
        average_annual_out_of_pocket = out_of_pocket_total / analysis_years
        
        total_miles = input_data['annual_mileage'] * analysis_years
        cost_per_mile = out_of_pocket_total / total_miles if total_miles > 0 else 0
        
        final_vehicle_value = depreciation_schedule[-1]['vehicle_value'] if depreciation_schedule else purchase_price * 0.5
        
        # Calculate affordability
        affordability = self._calculate_affordability(
            annual_cost=average_annual_out_of_pocket,
            gross_income=input_data.get('gross_income', 60000),
            transaction_type='purchase'
        )
        
        return {
            'summary': {
                'total_tco': total_tco,
                'total_ownership_cost': out_of_pocket_total,
                'average_annual_cost': average_annual_out_of_pocket,
                'cost_per_mile': cost_per_mile,
                'final_vehicle_value': final_vehicle_value,
                'total_depreciation': category_totals['depreciation']
            },
            'annual_breakdown': annual_breakdown,
            'category_totals': category_totals,
            'depreciation_schedule': depreciation_schedule,
            'maintenance_schedule': maintenance_schedule,
            'financing_schedule': financing_schedule,
            'vehicle_characteristics': vehicle_characteristics,
            'affordability': affordability,
            'analysis_parameters': {
                'analysis_years': analysis_years,
                'annual_mileage': input_data['annual_mileage'],
                'starting_mileage': current_mileage,
                'purchase_price': purchase_price
            }
        }

    def _adjust_maintenance_schedule(self, base_schedule: List[Dict[str, Any]], 
                                vehicle_make: str, shop_type: str, 
                                regional_multiplier: float) -> List[Dict[str, Any]]:
        """Apply brand, shop, and regional adjustments to maintenance schedule - FIXED"""
        
        # FIXED: Reduce multiplier impact since enhanced maintenance_utils already has realistic costs
        brand_multiplier = self.maintenance_calculator.brand_multipliers.get(vehicle_make, 1.0)
        
        # FIXED: Reduce shop multiplier impact - the base costs are already reasonable
        shop_multipliers = {
            'dealership': 1.15,      # REDUCED from 1.3 to 1.15 (15% premium)
            'independent': 1.0,      # Baseline
            'chain': 1.05,          # REDUCED from 1.1 to 1.05 (5% premium)  
            'specialty': 1.1,       # REDUCED from 1.2 to 1.1 (10% premium)
            'diy': 0.5             # Parts only
        }
        shop_multiplier = shop_multipliers.get(shop_type, 1.0)
        
        # FIXED: Cap regional multiplier to prevent excessive inflation
        regional_multiplier = max(0.8, min(1.3, regional_multiplier))
        
        adjusted_schedule = []
        
        for year_data in base_schedule:
            adjusted_services = []
            adjusted_total_cost = 0
            
            for service in year_data['services']:
                # FIXED: Apply reasonable multipliers instead of excessive ones
                base_cost = service['cost_per_service']
                
                # Apply brand adjustment (smaller impact)
                if brand_multiplier < 0.95:
                    # Reliable brands get small discount
                    adjusted_cost = base_cost * brand_multiplier
                elif brand_multiplier > 1.25:
                    # Luxury brands get moderate premium
                    adjusted_cost = base_cost * min(brand_multiplier, 1.4)  # Cap at 40% premium
                else:
                    # Most brands get minimal adjustment
                    adjusted_cost = base_cost * brand_multiplier
                
                # Apply shop and regional adjustments
                final_cost_per_service = adjusted_cost * shop_multiplier * regional_multiplier
                
                total_cost_for_service = final_cost_per_service * service['frequency']
                
                adjusted_services.append({
                    'service': service['service'],
                    'frequency': service['frequency'],
                    'cost_per_service': final_cost_per_service,
                    'total_cost': total_cost_for_service,
                    'shop_type': shop_type,
                    'interval_based': True
                })
                
                adjusted_total_cost += total_cost_for_service
            
            # FIXED: Reduce wear-based maintenance - the enhanced system already includes wear items
            vehicle_age = year_data['year']
            if vehicle_age > 3:
                # REDUCED wear cost since enhanced maintenance_utils includes detailed wear items
                wear_cost = self._calculate_year_specific_wear_maintenance(
                    vehicle_age, vehicle_make, shop_type, regional_multiplier
                )
                
                # FIXED: Only add wear cost if it's meaningful and not already covered
                if wear_cost > 100:  # Only add if significant
                    adjusted_services.append({
                        'service': 'Additional Wear & Tear',
                        'frequency': 1,
                        'cost_per_service': wear_cost,
                        'total_cost': wear_cost,
                        'shop_type': shop_type,
                        'interval_based': False
                    })
                    adjusted_total_cost += wear_cost
            
            adjusted_schedule.append({
                'year': year_data['year'],
                'total_mileage': year_data['total_mileage'],
                'starting_year_mileage': year_data.get('starting_year_mileage', 0),
                'ending_year_mileage': year_data.get('ending_year_mileage', 0),
                'services': adjusted_services,
                'total_year_cost': adjusted_total_cost,
                'brand_multiplier': brand_multiplier,
                'shop_multiplier': shop_multiplier,
                'regional_multiplier': regional_multiplier
            })
        
        return adjusted_schedule

    def _calculate_year_specific_wear_maintenance(self, vehicle_age: int, vehicle_make: str, 
                                                shop_type: str, regional_multiplier: float) -> float:
        """Calculate wear-based maintenance for a specific year - FIXED to reduce double-counting"""
        
        # FIXED: Reduced base wear costs since enhanced maintenance_utils includes detailed wear items
        base_wear_costs = {
            4: 100,   # REDUCED from 200 - Year 4: Minor additional repairs
            5: 150,   # REDUCED from 350 - Year 5: Some additional issues  
            6: 200,   # REDUCED from 500 - Year 6: Moderate additional wear
            7: 300,   # REDUCED from 750 - Year 7: Some additional repairs
            8: 400,   # REDUCED from 1000 - Year 8: More additional repairs
            9: 500,   # REDUCED from 1250 - Year 9: Increased maintenance
            10: 600   # REDUCED from 1500 - Year 10+: Higher maintenance
        }
        
        base_cost = base_wear_costs.get(min(vehicle_age, 10), 600)
        
        # Apply moderate multipliers
        brand_multiplier = self.maintenance_calculator.brand_multipliers.get(vehicle_make, 1.0)
        
        shop_multipliers = {
            'dealership': 1.15,
            'independent': 1.0,
            'chain': 1.05,
            'specialty': 1.1
        }
        shop_multiplier = shop_multipliers.get(shop_type, 1.0)
        
        # FIXED: Calculate reasonable wear cost
        wear_cost = base_cost * brand_multiplier * shop_multiplier * regional_multiplier
        
        return wear_cost

    def _calculate_lease_tco(self, input_data: Dict[str, Any],
                            vehicle_characteristics: Dict[str, Any],
                            regional_multiplier: float) -> Dict[str, Any]:
        """Calculate TCO for lease scenario - FIXED: All required defaults added"""
        
        # FIXED: Provide safe defaults for all fields
        lease_term = input_data.get('lease_term', input_data.get('analysis_years', 3))
        monthly_payment = input_data.get('monthly_payment', 400)
        down_payment = input_data.get('down_payment', 0)
        annual_mileage_limit = input_data.get('annual_mileage_limit', 12000)
        
        # FIXED: Safe access to driving parameters
        driving_style = input_data.get('driving_style', 'normal')
        terrain = input_data.get('terrain', 'flat')
        fuel_price = input_data.get('fuel_price', 3.50)
        
        category_totals = {
            'lease_payments': 0,
            'maintenance': 0,
            'insurance': 0,
            'fuel_energy': 0,
            'fees_penalties': 0
        }
        
        # Calculate lease maintenance schedule with safe defaults
        lease_maintenance_schedule = self.maintenance_calculator.get_maintenance_schedule(
            annual_mileage=annual_mileage_limit,
            years=lease_term,
            starting_mileage=0,
            vehicle_make=input_data.get('make', 'Unknown'),
            driving_style=driving_style,
            vehicle_model=input_data.get('model', 'Unknown')
        )
        
        annual_breakdown = []
        
        for year in range(1, lease_term + 1):
            ownership_year = 2025 + (year - 1)
            current_mileage = annual_mileage_limit * year
            
            # Lease payments
            annual_lease_payment = monthly_payment * 12
            
            # Maintenance
            if year <= len(lease_maintenance_schedule):
                annual_maintenance = lease_maintenance_schedule[year-1]['total_year_cost']
                maintenance_activities = lease_maintenance_schedule[year-1]['services']
            else:
                annual_maintenance = 0
                maintenance_activities = []
            
            # Insurance - with safe defaults
            vehicle_value = input_data.get('trim_msrp', input_data.get('purchase_price', 40000))
            annual_insurance = self.insurance_calculator.calculate_annual_premium(
                vehicle_value=vehicle_value,
                vehicle_make=input_data.get('make', 'Unknown'),
                vehicle_year=input_data.get('year', 2024),
                driver_age=input_data.get('user_age', 25),
                state=input_data.get('state', 'CA'),
                coverage_type='comprehensive',
                annual_mileage=annual_mileage_limit,
                num_vehicles=input_data.get('num_household_vehicles', 1),
                regional_multiplier=regional_multiplier
            )
            
            # ============================================================================
            # FIX FOR prediction_service.py
            # Add driving style and terrain adjustments to EV calculations
            # ============================================================================

            # Find this section in _calculate_purchase_tco method (around line 200-250):

            is_electric = input_data.get('is_electric') or vehicle_characteristics.get('is_electric', False)

            # Get driving parameters
            driving_style = input_data.get('driving_style', 'normal')
            terrain = input_data.get('terrain', 'flat')

            # Driving style efficiency multipliers
            driving_style_multipliers = {
                'gentle': 1.15,     # 15% better efficiency
                'normal': 1.0,      # Baseline
                'aggressive': 0.85  # 15% worse efficiency
            }

            # Terrain efficiency multipliers
            terrain_multipliers = {
                'flat': 1.05,       # 5% better efficiency
                'hilly': 0.95       # 5% worse efficiency
            }

            # Calculate combined multiplier
            style_multiplier = driving_style_multipliers.get(driving_style, 1.0)
            terrain_multiplier = terrain_multipliers.get(terrain, 1.0)
            combined_multiplier = style_multiplier * terrain_multiplier

            if is_electric:
                annual_fuel = self.ev_calculator.calculate_annual_electricity_cost(
                    annual_mileage=annual_mileage_limit,  # âœ… Use lease mileage limit
                    vehicle_efficiency=adjusted_ev_efficiency,
                    electricity_rate=input_data.get('electricity_rate', 0.12),
                    charging_preference=input_data.get('charging_preference', 'mixed')
                )
            else:
                annual_fuel = self.fuel_calculator.calculate_annual_fuel_cost(
                    annual_mileage=annual_mileage_limit,  # âœ… Use lease mileage limit
                    mpg=vehicle_characteristics.get('mpg', 25),
                    fuel_price=input_data.get('fuel_price', 3.50),
                    driving_style=driving_style,
                    terrain=terrain
                )


            
            # Calculate fees/penalties
            annual_fees = self._calculate_lease_fees_and_penalties(
                actual_mileage=input_data.get('annual_mileage', annual_mileage_limit),
                allowed_mileage=annual_mileage_limit,
                lease_year=year,
                vehicle_value=vehicle_value
            )
            
            # Total annual cost
            total_annual = annual_lease_payment + annual_maintenance + annual_insurance + annual_fuel + annual_fees
            
            # Store breakdown
            annual_breakdown.append({
                'year': year,
                'ownership_year': ownership_year,
                'lease_year': year,
                'vehicle_age': ownership_year - input_data.get('year', 2024),
                'vehicle_model_year': input_data.get('year', 2024),
                'lease_payment': annual_lease_payment,
                'maintenance': annual_maintenance,
                'maintenance_activities': maintenance_activities,
                'cumulative_mileage': current_mileage,
                'insurance': annual_insurance,
                'fuel_energy': annual_fuel,
                'fees_penalties': annual_fees,
                'total_annual_cost': total_annual
            })
            
            # Add to totals
            category_totals['lease_payments'] += annual_lease_payment
            category_totals['maintenance'] += annual_maintenance
            category_totals['insurance'] += annual_insurance
            category_totals['fuel_energy'] += annual_fuel
            category_totals['fees_penalties'] += annual_fees
        
        # Calculate summary metrics
        total_lease_cost = sum(category_totals.values()) + down_payment
        average_annual_cost = total_lease_cost / lease_term if lease_term > 0 else 0
        average_monthly_cost = total_lease_cost / (lease_term * 12) if lease_term > 0 else 0
        total_miles = annual_mileage_limit * lease_term
        cost_per_mile = total_lease_cost / total_miles if total_miles > 0 else 0
        
        # Affordability calculation with safe defaults
        affordability = self._calculate_affordability(
            annual_cost=average_annual_cost,
            gross_income=input_data.get('gross_income', 60000),
            transaction_type='lease'
        )
        
        return {
            'summary': {
                'total_lease_cost': total_lease_cost,
                'average_annual_cost': average_annual_cost,
                'average_monthly_cost': average_monthly_cost,
                'cost_per_mile': cost_per_mile,
                'down_payment': down_payment
            },
            'annual_breakdown': annual_breakdown,
            'category_totals': category_totals,
            'maintenance_schedule': lease_maintenance_schedule,
            'vehicle_characteristics': vehicle_characteristics,
            'affordability': affordability,
            'analysis_parameters': {
                'lease_term': lease_term,
                'monthly_payment': monthly_payment,
                'annual_mileage_limit': annual_mileage_limit,
                'driving_style': driving_style,
                'terrain': terrain
            }
        }

    def _adjust_lease_maintenance_schedule(self, base_schedule: List[Dict[str, Any]], 
                                            vehicle_make: str, regional_multiplier: float) -> List[Dict[str, Any]]:
        """Apply lease-specific adjustments to maintenance schedule (warranty coverage)"""
        
        brand_multiplier = self.maintenance_calculator.brand_multipliers.get(vehicle_make, 1.0)
        shop_multiplier = 1.2  # Dealership service for leases
        
        adjusted_schedule = []
        
        for year_data in base_schedule:
            lease_year = year_data['year']
            adjusted_services = []
            adjusted_total_cost = 0
            
            # Apply warranty discounts based on lease year
            if lease_year <= 2:
                warranty_discount = 0.6  # 60% covered by warranty
            elif lease_year <= 3:
                warranty_discount = 0.4  # 40% covered by warranty
            else:
                warranty_discount = 0.2  # 20% covered by extended warranty
            
            for service in year_data['services']:
                # Apply multipliers and warranty discount
                full_cost = (service['cost_per_service'] * 
                            brand_multiplier * 
                            shop_multiplier * 
                            regional_multiplier)
                
                out_of_pocket_cost = full_cost * (1 - warranty_discount)
                
                if out_of_pocket_cost > 5:  # Only include if cost is meaningful
                    adjusted_services.append({
                        'service': service['service'],
                        'frequency': service['frequency'],
                        'cost_per_service': out_of_pocket_cost,
                        'total_cost': out_of_pocket_cost * service['frequency'],
                        'warranty_covered': full_cost * warranty_discount * service['frequency'],
                        'shop_type': 'dealership',
                        'interval_based': True
                    })
                    adjusted_total_cost += out_of_pocket_cost * service['frequency']
            
            # Lease vehicles rarely need wear repairs in first few years
            if lease_year > 3:
                wear_cost = 100 * brand_multiplier * regional_multiplier  # Minimal wear
                adjusted_services.append({
                    'service': 'Minor Wear Items',
                    'frequency': 1,
                    'cost_per_service': wear_cost,
                    'total_cost': wear_cost,
                    'warranty_covered': 0,
                    'shop_type': 'dealership',
                    'interval_based': False
                })
                adjusted_total_cost += wear_cost
            
            adjusted_schedule.append({
                'year': lease_year,
                'total_mileage': year_data['total_mileage'],
                'services': adjusted_services,
                'total_year_cost': adjusted_total_cost,
                'warranty_discount': warranty_discount,
                'brand_multiplier': brand_multiplier,
                'shop_multiplier': shop_multiplier,
                'regional_multiplier': regional_multiplier
            })
        
        return adjusted_schedule

    def _calculate_lease_fees_and_penalties(self, actual_mileage: int, 
                                            allowed_mileage: int,
                                            lease_year: int, 
                                            vehicle_value: float) -> float:
        """Calculate lease overage fees and penalties"""
        
        mileage_overage = max(0, actual_mileage - allowed_mileage)
        overage_fee_per_mile = 0.25
        
        annual_fees = mileage_overage * overage_fee_per_mile
        
        return annual_fees

    def _calculate_affordability(self, annual_cost: float, gross_income: float, 
                                transaction_type: str) -> Dict[str, Any]:
        """Calculate affordability metrics"""
        
        monthly_cost = annual_cost / 12
        monthly_income = gross_income / 12
        
        percentage_of_income = (monthly_cost / monthly_income * 100) if monthly_income > 0 else 0
        
        # Determine affordability rating
        if percentage_of_income <= 10:
            affordability_rating = 'Excellent'
            is_affordable = True
        elif percentage_of_income <= 15:
            affordability_rating = 'Good'
            is_affordable = True
        elif percentage_of_income <= 20:
            affordability_rating = 'Fair'
            is_affordable = True
        else:
            affordability_rating = 'Stretched'
            is_affordable = False
        
        return {
            'monthly_cost': monthly_cost,
            'monthly_income': monthly_income,
            'percentage_of_income': percentage_of_income,
            'affordability_rating': affordability_rating,
            'is_affordable': is_affordable,
            'recommended_max_monthly': monthly_income * 0.15,  # 15% guideline
            'over_budget': percentage_of_income > 15
        }

    def _get_calculation_assumptions(self, input_data: Dict[str, Any], 
                                    vehicle_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Get assumptions used in calculations"""
        
        return {
            'depreciation_method': 'Enhanced market-based model',
            'maintenance_source': 'Manufacturer schedules + historical data',
            'insurance_basis': 'State-specific rates with driver profile',
            'fuel_prices': 'Current regional averages',
            'regional_adjustments': f"{input_data['geography_type']} geography in {input_data['state']}",
            'reliability_score': vehicle_characteristics.get('reliability_score', 3.5),
            'market_segment': vehicle_characteristics.get('market_segment', 'standard'),
            'calculation_date': '2025-08-08',
            'data_sources': [
                'Manufacturer MSRP data',
                'Regional fuel price databases', 
                'State insurance regulations',
                'Historical depreciation curves'
            ]
        }
    def _update_results_structure_for_display(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update results structure to match display expectations
        FIXED: Ensures proper cost separation for display functions
        """
        
        summary = results.get('summary', {})
        category_totals = results.get('category_totals', {})
        
        # Calculate out-of-pocket costs (excluding depreciation)
        out_of_pocket_total = (
            category_totals.get('maintenance', 0) +
            category_totals.get('insurance', 0) +
            category_totals.get('fuel_energy', 0) +
            category_totals.get('financing', 0)
        )
        
        # Update results structure for backward compatibility with display code
        display_results = results.copy()
        display_results.update({
            'total_cost': out_of_pocket_total,  # Main "total cost" is now out-of-pocket only
            'annual_cost': summary.get('average_annual_cost', 0),  # Already based on out-of-pocket
            'cost_per_mile': summary.get('cost_per_mile', 0),  # Already based on out-of-pocket
            'final_value': summary.get('final_vehicle_value', 0),
            'depreciation': category_totals.get('depreciation', 0),
            'maintenance': category_totals.get('maintenance', 0),
            'insurance': category_totals.get('insurance', 0),
            'energy': category_totals.get('fuel_energy', 0),
            'financing': category_totals.get('financing', 0),
            'total_tco': summary.get('total_tco', out_of_pocket_total + category_totals.get('depreciation', 0)),  # Complete TCO for reference
            'annual_operating_cost': out_of_pocket_total,  # For compatibility
            'is_electric': results.get('vehicle_characteristics', {}).get('is_electric', False)
        })
        
        return display_results