"""
Vehicle MPG Database
Comprehensive fuel economy data for vehicles by make, model, year, and trim
"""

# MPG Database - Organized by make/model with year ranges and trim variations
VEHICLE_MPG_DATABASE = {
    'Toyota': {
        'Camry': {
            'base_mpg': {'city': 28, 'highway': 39, 'combined': 32},
            'years': {
                (2018, 2025): {
                    'LE': {'city': 28, 'highway': 39, 'combined': 32},
                    'SE': {'city': 27, 'highway': 38, 'combined': 31},
                    'XLE': {'city': 28, 'highway': 39, 'combined': 32},
                    'XSE': {'city': 26, 'highway': 35, 'combined': 29},
                    'TRD': {'city': 24, 'highway': 34, 'combined': 28}
                },
                (2012, 2017): {
                    'L': {'city': 25, 'highway': 35, 'combined': 28},
                    'LE': {'city': 25, 'highway': 35, 'combined': 28},
                    'SE': {'city': 25, 'highway': 35, 'combined': 28},
                    'XLE': {'city': 25, 'highway': 35, 'combined': 28}
                }
            }
        },
        'Corolla': {
            'base_mpg': {'city': 31, 'highway': 40, 'combined': 34},
            'years': {
                (2020, 2025): {
                    'L': {'city': 31, 'highway': 40, 'combined': 34},
                    'LE': {'city': 31, 'highway': 40, 'combined': 34},
                    'SE': {'city': 30, 'highway': 38, 'combined': 33},
                    'XLE': {'city': 31, 'highway': 40, 'combined': 34}
                },
                (2014, 2019): {
                    'L': {'city': 30, 'highway': 40, 'combined': 34},
                    'LE': {'city': 30, 'highway': 40, 'combined': 34},
                    'S': {'city': 29, 'highway': 38, 'combined': 32}
                }
            }
        },
        'Prius': {
            'base_mpg': {'city': 58, 'highway': 53, 'combined': 56},
            'years': {
                (2016, 2025): {
                    'L Eco': {'city': 62, 'highway': 58, 'combined': 60},
                    'LE': {'city': 58, 'highway': 53, 'combined': 56},
                    'XLE': {'city': 58, 'highway': 53, 'combined': 56},
                    'Limited': {'city': 54, 'highway': 50, 'combined': 52}
                }
            }
        },
        'RAV4': {
            'base_mpg': {'city': 27, 'highway': 35, 'combined': 30},
            'years': {
                (2019, 2025): {
                    'LE': {'city': 27, 'highway': 35, 'combined': 30},
                    'XLE': {'city': 27, 'highway': 35, 'combined': 30},
                    'Adventure': {'city': 25, 'highway': 33, 'combined': 28},
                    'TRD Off-Road': {'city': 25, 'highway': 33, 'combined': 28},
                    'Limited': {'city': 27, 'highway': 35, 'combined': 30}
                }
            }
        },
        'Highlander': {
            'base_mpg': {'city': 21, 'highway': 29, 'combined': 24},
            'years': {
                (2020, 2025): {
                    'L': {'city': 21, 'highway': 29, 'combined': 24},
                    'LE': {'city': 21, 'highway': 29, 'combined': 24},
                    'XLE': {'city': 21, 'highway': 29, 'combined': 24},
                    'Limited': {'city': 21, 'highway': 29, 'combined': 24},
                    'Platinum': {'city': 20, 'highway': 27, 'combined': 23}
                }
            }
        }
    },
    'Honda': {
        'Civic': {
            'base_mpg': {'city': 32, 'highway': 42, 'combined': 36},
            'years': {
                (2016, 2025): {
                    'LX': {'city': 32, 'highway': 42, 'combined': 36},
                    'Sport': {'city': 30, 'highway': 38, 'combined': 33},
                    'EX': {'city': 32, 'highway': 42, 'combined': 36},
                    'EX-L': {'city': 32, 'highway': 42, 'combined': 36},
                    'Touring': {'city': 32, 'highway': 42, 'combined': 36},
                    'Type R': {'city': 22, 'highway': 28, 'combined': 25}
                }
            }
        },
        'Accord': {
            'base_mpg': {'city': 30, 'highway': 38, 'combined': 33},
            'years': {
                (2018, 2025): {
                    'LX': {'city': 30, 'highway': 38, 'combined': 33},
                    'Sport': {'city': 30, 'highway': 38, 'combined': 33},
                    'EX': {'city': 30, 'highway': 38, 'combined': 33},
                    'EX-L': {'city': 30, 'highway': 38, 'combined': 33},
                    'Touring': {'city': 30, 'highway': 38, 'combined': 33},
                    'Sport 2.0T': {'city': 22, 'highway': 32, 'combined': 26}
                }
            }
        },
        'CR-V': {
            'base_mpg': {'city': 28, 'highway': 34, 'combined': 30},
            'years': {
                (2017, 2025): {
                    'LX': {'city': 28, 'highway': 34, 'combined': 30},
                    'EX': {'city': 28, 'highway': 34, 'combined': 30},
                    'EX-L': {'city': 28, 'highway': 34, 'combined': 30},
                    'Touring': {'city': 27, 'highway': 33, 'combined': 29}
                }
            }
        },
        'Pilot': {
            'base_mpg': {'city': 20, 'highway': 27, 'combined': 23},
            'years': {
                (2016, 2025): {
                    'LX': {'city': 20, 'highway': 27, 'combined': 23},
                    'EX': {'city': 20, 'highway': 27, 'combined': 23},
                    'EX-L': {'city': 20, 'highway': 27, 'combined': 23},
                    'Touring': {'city': 20, 'highway': 27, 'combined': 23},
                    'Elite': {'city': 19, 'highway': 26, 'combined': 22}
                }
            }
        }
    },
    'Lincoln': {
        'Corsair': {
            'base_mpg': {'city': 21, 'highway': 28, 'combined': 24},
            'years': {
                (2020, 2025): {
                    'Corsair': {'city': 21, 'highway': 28, 'combined': 24},
                    'Corsair Reserve': {'city': 21, 'highway': 28, 'combined': 24},
                    'Corsair Grand Touring': {'city': 33, 'highway': 31, 'combined': 33}
                }
            }
        },
        'Aviator': {
            'base_mpg': {'city': 18, 'highway': 26, 'combined': 21},
            'years': {
                (2020, 2025): {
                    'Aviator': {'city': 18, 'highway': 26, 'combined': 21},
                    'Aviator Reserve': {'city': 18, 'highway': 26, 'combined': 21},
                    'Aviator Grand Touring': {'city': 23, 'highway': 26, 'combined': 24}
                }
            }
        },
        'Nautilus': {
            'base_mpg': {'city': 19, 'highway': 26, 'combined': 22},
            'years': {
                (2019, 2025): {
                    'Nautilus': {'city': 19, 'highway': 26, 'combined': 22},
                    'Nautilus Reserve': {'city': 19, 'highway': 26, 'combined': 22}
                }
            }
        },
        'Navigator': {
            'base_mpg': {'city': 16, 'highway': 23, 'combined': 19},
            'years': {
                (2018, 2025): {
                    'Navigator': {'city': 16, 'highway': 23, 'combined': 19},
                    'Navigator Reserve': {'city': 16, 'highway': 23, 'combined': 19},
                    'Navigator L': {'city': 16, 'highway': 22, 'combined': 18}
                }
            }
        }
    },
    'Chevrolet': {
        'Malibu': {
            'base_mpg': {'city': 29, 'highway': 36, 'combined': 32},
            'years': {
                (2016, 2025): {
                    'L': {'city': 29, 'highway': 36, 'combined': 32},
                    'LS': {'city': 29, 'highway': 36, 'combined': 32},
                    'LT': {'city': 29, 'highway': 36, 'combined': 32},
                    'Premier': {'city': 29, 'highway': 36, 'combined': 32}
                }
            }
        },
        'Equinox': {
            'base_mpg': {'city': 26, 'highway': 31, 'combined': 28},
            'years': {
                (2018, 2025): {
                    'L': {'city': 26, 'highway': 31, 'combined': 28},
                    'LS': {'city': 26, 'highway': 31, 'combined': 28},
                    'LT': {'city': 26, 'highway': 31, 'combined': 28},
                    'Premier': {'city': 26, 'highway': 31, 'combined': 28}
                }
            }
        },
        'Silverado 1500': {
            'base_mpg': {'city': 20, 'highway': 25, 'combined': 22},
            'years': {
                (2019, 2025): {
                    'Regular Cab WT': {'city': 20, 'highway': 25, 'combined': 22},
                    'Double Cab LT': {'city': 20, 'highway': 25, 'combined': 22},
                    'Crew Cab LT': {'city': 20, 'highway': 25, 'combined': 22},
                    'Crew Cab LTZ': {'city': 19, 'highway': 24, 'combined': 21},
                    'High Country': {'city': 19, 'highway': 24, 'combined': 21}
                }
            }
        },
        'Corvette': {
            'base_mpg': {'city': 15, 'highway': 27, 'combined': 19},
            'years': {
                (2020, 2025): {
                    'Stingray': {'city': 15, 'highway': 27, 'combined': 19},
                    'Z06': {'city': 12, 'highway': 21, 'combined': 15}
                }
            }
        }
    },
    'Ford': {
        'F-150': {
            'base_mpg': {'city': 19, 'highway': 24, 'combined': 21},
            'years': {
                (2015, 2025): {
                    'Regular Cab XL': {'city': 19, 'highway': 25, 'combined': 22},
                    'SuperCab XLT': {'city': 19, 'highway': 24, 'combined': 21},
                    'SuperCrew Lariat': {'city': 18, 'highway': 23, 'combined': 20},
                    'King Ranch': {'city': 17, 'highway': 23, 'combined': 19},
                    'Raptor': {'city': 15, 'highway': 18, 'combined': 16}
                }
            }
        },
        'Mustang': {
            'base_mpg': {'city': 21, 'highway': 32, 'combined': 25},
            'years': {
                (2015, 2025): {
                    'EcoBoost': {'city': 21, 'highway': 32, 'combined': 25},
                    'EcoBoost Premium': {'city': 21, 'highway': 32, 'combined': 25},
                    'GT': {'city': 16, 'highway': 25, 'combined': 19},
                    'GT Premium': {'city': 16, 'highway': 25, 'combined': 19},
                    'Shelby GT350': {'city': 14, 'highway': 21, 'combined': 17}
                }
            }
        },
        'Explorer': {
            'base_mpg': {'city': 21, 'highway': 28, 'combined': 24},
            'years': {
                (2020, 2025): {
                    'Base': {'city': 21, 'highway': 28, 'combined': 24},
                    'XLT': {'city': 21, 'highway': 28, 'combined': 24},
                    'Limited': {'city': 20, 'highway': 27, 'combined': 23},
                    'Platinum': {'city': 20, 'highway': 27, 'combined': 23},
                    'ST': {'city': 18, 'highway': 24, 'combined': 20}
                }
            }
        }
    },
    'BMW': {
        '3 Series': {
            'base_mpg': {'city': 26, 'highway': 36, 'combined': 30},
            'years': {
                (2019, 2025): {
                    '330i': {'city': 26, 'highway': 36, 'combined': 30},
                    '330i xDrive': {'city': 25, 'highway': 34, 'combined': 29},
                    'M340i': {'city': 22, 'highway': 30, 'combined': 25},
                    'M340i xDrive': {'city': 21, 'highway': 29, 'combined': 24}
                }
            }
        },
        '5 Series': {
            'base_mpg': {'city': 23, 'highway': 34, 'combined': 27},
            'years': {
                (2017, 2025): {
                    '530i': {'city': 24, 'highway': 34, 'combined': 28},
                    '530i xDrive': {'city': 23, 'highway': 33, 'combined': 27},
                    '540i': {'city': 21, 'highway': 30, 'combined': 25},
                    'M550i': {'city': 17, 'highway': 25, 'combined': 20}
                }
            }
        },
        'X3': {
            'base_mpg': {'city': 23, 'highway': 29, 'combined': 25},
            'years': {
                (2018, 2025): {
                    'sDrive30i': {'city': 24, 'highway': 31, 'combined': 27},
                    'xDrive30i': {'city': 23, 'highway': 29, 'combined': 25},
                    'M40i': {'city': 21, 'highway': 27, 'combined': 23}
                }
            }
        }
    },
    'Mercedes-Benz': {
        'C-Class': {
            'base_mpg': {'city': 24, 'highway': 35, 'combined': 28},
            'years': {
                (2015, 2025): {
                    'C 300': {'city': 24, 'highway': 35, 'combined': 28},
                    'C 300 4MATIC': {'city': 23, 'highway': 33, 'combined': 27},
                    'AMG C 43': {'city': 20, 'highway': 29, 'combined': 23},
                    'AMG C 63': {'city': 17, 'highway': 25, 'combined': 20}
                }
            }
        },
        'E-Class': {
            'base_mpg': {'city': 23, 'highway': 32, 'combined': 26},
            'years': {
                (2017, 2025): {
                    'E 350': {'city': 23, 'highway': 32, 'combined': 26},
                    'E 350 4MATIC': {'city': 22, 'highway': 30, 'combined': 25},
                    'AMG E 53': {'city': 20, 'highway': 28, 'combined': 23}
                }
            }
        }
    },
    'Audi': {
        'A4': {
            'base_mpg': {'city': 24, 'highway': 34, 'combined': 28},
            'years': {
                (2017, 2025): {
                    'Premium': {'city': 24, 'highway': 34, 'combined': 28},
                    'Premium Plus': {'city': 24, 'highway': 34, 'combined': 28},
                    'Prestige': {'city': 24, 'highway': 34, 'combined': 28},
                    'quattro Premium': {'city': 23, 'highway': 32, 'combined': 27}
                }
            }
        },
        'Q5': {
            'base_mpg': {'city': 23, 'highway': 28, 'combined': 25},
            'years': {
                (2018, 2025): {
                    'Premium': {'city': 23, 'highway': 28, 'combined': 25},
                    'Premium Plus': {'city': 23, 'highway': 28, 'combined': 25},
                    'Prestige': {'city': 23, 'highway': 28, 'combined': 25}
                }
            }
        }
    },
    'Tesla': {
        'Model 3': {
            'base_mpg': {'city': 0, 'highway': 0, 'combined': 0},  # Electric - use MPGe
            'mpge': {'city': 142, 'highway': 132, 'combined': 138},
            'years': {
                (2017, 2025): {
                    'Standard Range Plus': {'mpge_combined': 138},
                    'Long Range': {'mpge_combined': 134},
                    'Performance': {'mpge_combined': 115}
                }
            }
        },
        'Model S': {
            'base_mpg': {'city': 0, 'highway': 0, 'combined': 0},
            'mpge': {'city': 120, 'highway': 112, 'combined': 116},
            'years': {
                (2012, 2025): {
                    'Long Range': {'mpge_combined': 116},
                    'Plaid': {'mpge_combined': 108}
                }
            }
        },
        'Model X': {
            'base_mpg': {'city': 0, 'highway': 0, 'combined': 0},
            'mpge': {'city': 105, 'highway': 97, 'combined': 102},
            'years': {
                (2015, 2025): {
                    'Long Range': {'mpge_combined': 102},
                    'Plaid': {'mpge_combined': 96}
                }
            }
        },
        'Model Y': {
            'base_mpg': {'city': 0, 'highway': 0, 'combined': 0},
            'mpge': {'city': 129, 'highway': 112, 'combined': 122},
            'years': {
                (2020, 2025): {
                    'Long Range': {'mpge_combined': 122},
                    'Performance': {'mpge_combined': 111}
                }
            }
        }
    },
    'Lexus': {
        'ES': {
            'base_mpg': {'city': 28, 'highway': 39, 'combined': 32},
            'years': {
                (2019, 2025): {
                    'ES 250': {'city': 28, 'highway': 39, 'combined': 32},
                    'ES 300': {'city': 28, 'highway': 39, 'combined': 32},
                    'ES 350': {'city': 22, 'highway': 32, 'combined': 26},
                    'ES 300h': {'city': 43, 'highway': 44, 'combined': 44}
                }
            }
        },
        'RX': {
            'base_mpg': {'city': 20, 'highway': 27, 'combined': 23},
            'years': {
                (2016, 2025): {
                    'RX 350': {'city': 20, 'highway': 27, 'combined': 23},
                    'RX 350L': {'city': 19, 'highway': 26, 'combined': 22},
                    'RX 450h': {'city': 31, 'highway': 28, 'combined': 30}
                }
            }
        }
    },
    'Hyundai': {
        'Elantra': {
            'base_mpg': {'city': 33, 'highway': 43, 'combined': 37},
            'years': {
                (2017, 2025): {
                    'SE': {'city': 33, 'highway': 43, 'combined': 37},
                    'SEL': {'city': 33, 'highway': 43, 'combined': 37},
                    'Limited': {'city': 33, 'highway': 43, 'combined': 37},
                    'Sport': {'city': 25, 'highway': 33, 'combined': 28}
                }
            }
        },
        'Santa Fe': {
            'base_mpg': {'city': 22, 'highway': 25, 'combined': 23},
            'years': {
                (2019, 2025): {
                    'SE': {'city': 22, 'highway': 25, 'combined': 23},
                    'SEL': {'city': 22, 'highway': 25, 'combined': 23},
                    'Limited': {'city': 22, 'highway': 25, 'combined': 23},
                    'Calligraphy': {'city': 22, 'highway': 25, 'combined': 23}
                }
            }
        }
    },
    'Nissan': {
        'Altima': {
            'base_mpg': {'city': 28, 'highway': 39, 'combined': 32},
            'years': {
                (2019, 2025): {
                    'S': {'city': 28, 'highway': 39, 'combined': 32},
                    'SV': {'city': 28, 'highway': 39, 'combined': 32},
                    'SL': {'city': 28, 'highway': 39, 'combined': 32},
                    'Platinum': {'city': 25, 'highway': 34, 'combined': 29}
                }
            }
        },
        'Rogue': {
            'base_mpg': {'city': 26, 'highway': 33, 'combined': 29},
            'years': {
                (2021, 2025): {
                    'S': {'city': 26, 'highway': 33, 'combined': 29},
                    'SV': {'city': 26, 'highway': 33, 'combined': 29},
                    'SL': {'city': 26, 'highway': 33, 'combined': 29},
                    'Platinum': {'city': 26, 'highway': 33, 'combined': 29}
                }
            }
        }
    }
}

def get_vehicle_mpg(make: str, model: str, year: int, trim: str = None) -> dict:
    """
    Get MPG data for a specific vehicle
    Returns dict with city, highway, combined MPG and mpge for electric vehicles
    """
    
    # Default fallback MPG values
    default_mpg = {
        'city': 25,
        'highway': 32,
        'combined': 28,
        'mpge_combined': 0,
        'is_electric': False,
        'source': 'estimated'
    }
    
    # Normalize inputs
    make = make.strip()
    model = model.strip()
    
    # Check if make exists in database
    if make not in VEHICLE_MPG_DATABASE:
        return assign_default_mpg_by_category(make, model, trim)
    
    make_data = VEHICLE_MPG_DATABASE[make]
    
    # Check if model exists
    if model not in make_data:
        return assign_default_mpg_by_category(make, model, trim)
    
    model_data = make_data[model]
    
    # Get base MPG
    result = model_data.get('base_mpg', default_mpg).copy()
    result['source'] = 'database'
    
    # Check for electric vehicle
    if 'mpge' in model_data:
        result['mpge_city'] = model_data['mpge']['city']
        result['mpge_highway'] = model_data['mpge']['highway']
        result['mpge_combined'] = model_data['mpge']['combined']
        result['is_electric'] = True
        result['city'] = 0
        result['highway'] = 0
        result['combined'] = 0
    
    # Find year-specific data
    if 'years' in model_data:
        for year_range, trim_data in model_data['years'].items():
            start_year, end_year = year_range
            if start_year <= year <= end_year:
                
                # If trim is specified and exists, use trim-specific data
                if trim and trim in trim_data:
                    trim_mpg = trim_data[trim]
                    result.update(trim_mpg)
                    result['source'] = 'database_trim_specific'
                    break
                else:
                    # Use the first available trim as default
                    first_trim = list(trim_data.values())[0]
                    if isinstance(first_trim, dict):
                        result.update(first_trim)
                        result['source'] = 'database_default_trim'
                    break
    
    return result

def assign_default_mpg_by_category(make: str, model: str, trim: str = None) -> dict:
    """
    Assign default MPG based on vehicle category when not in database
    
    UNIVERSAL HYBRID DETECTION: Checks both model name AND trim name
    This ensures hybrids are caught regardless of where "Hybrid" appears:
    - Model name: "Prius", "Insight", "Accord Hybrid"
    - Trim name: "Hybrid LX", "Hybrid Limited", "Hybrid Touring"
    
    Works for ALL manufacturers: Toyota, Honda, Hyundai, Kia, Ford, Nissan, etc.
    """
    
    make_lower = make.lower()
    model_lower = model.lower()
    trim_lower = trim.lower() if trim else ''
    
    # Combine for comprehensive searching
    full_name = f"{model_lower} {trim_lower}".strip()
    
    # ==================== ELECTRIC VEHICLES ====================
    if make_lower == 'tesla' or any(kw in full_name for kw in [
        ' ev', 'leaf', 'bolt', 'ioniq 5', 'ioniq 6', 'bz4x', 'rz',
        'ariya', 'ev6', 'ev9', 'lyriq', 'id.4', 'mach-e', 'lightning']):
        return {
            'city': 0, 'highway': 0, 'combined': 0,
            'mpge_combined': 120, 'is_electric': True,
            'source': 'estimated_electric'
        }
    
    # ==================== HYBRID DETECTION ====================
    # Check if 'hybrid' appears in model OR trim
    has_hybrid_keyword = 'hybrid' in model_lower or 'hybrid' in trim_lower
    
    # Check for other hybrid indicators
    has_hybrid_model = any(kw in model_lower for kw in [
        'prius', 'insight', 'venza', '300h', '450h', '500h', '250h', '600h'
    ])
    
    # Check for PHEV indicators
    is_phev = any(kw in full_name for kw in [
        'prime', 'plug-in', 'phev', '4xe', 'energi', 'e-hybrid', 'recharge'
    ])
    
    # If hybrid detected by ANY method
    if has_hybrid_keyword or has_hybrid_model or is_phev:
        
        # ===== PLUG-IN HYBRIDS (PHEV) =====
        if is_phev:
            if any(kw in model_lower for kw in ['rav4', 'escape', 'tucson', 'sportage', 'niro', 'rogue']):
                return {'city': 94, 'highway': 83, 'combined': 38, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_phev_compact_suv'}
            elif any(kw in model_lower for kw in ['grand cherokee', 'wrangler', 'compass', 'aviator', 'corsair']):
                return {'city': 56, 'highway': 48, 'combined': 25, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_phev_midsize_suv'}
            elif any(kw in model_lower for kw in ['pacifica', 'carnival', 'sienna']):
                return {'city': 82, 'highway': 32, 'combined': 32, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_phev_minivan'}
            else:
                return {'city': 133, 'highway': 54, 'combined': 55, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_phev_sedan'}
        
        # ===== EXCEPTIONAL HYBRIDS =====
        if 'prius' in model_lower:
            return {'city': 58, 'highway': 53, 'combined': 56, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_hybrid_prius'}
        elif 'insight' in model_lower:
            return {'city': 55, 'highway': 49, 'combined': 52, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_hybrid_insight'}
        elif 'venza' in model_lower:
            return {'city': 40, 'highway': 37, 'combined': 39, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_hybrid_venza'}
        
        # ===== HYBRID SEDANS =====
        elif any(kw in model_lower for kw in ['corolla', 'elantra', 'civic', 'ioniq', 'sentra', 'forte']):
            return {'city': 53, 'highway': 52, 'combined': 52, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_hybrid_compact_sedan'}
        elif any(kw in model_lower for kw in ['camry', 'accord', 'sonata', 'altima', 'fusion', 'malibu', 'k5', 'optima']):
            return {'city': 51, 'highway': 53, 'combined': 52, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_hybrid_midsize_sedan'}
        elif any(kw in model_lower for kw in ['es', 'ls', 'is', 'rlx', 'ilx', 'mkz', '330e', '530e', '740e', 'a3', 'a8']) or make_lower in ['lexus', 'acura', 'lincoln']:
            return {'city': 43, 'highway': 44, 'combined': 44, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_hybrid_luxury_sedan'}
        
        # ===== HYBRID SUVs =====
        elif any(kw in model_lower for kw in ['rav4', 'cr-v', 'tucson', 'niro', 'escape', 'rogue', 'sportage', 'kona', 'crosstrek', 'seltos']):
            return {'city': 41, 'highway': 38, 'combined': 40, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_hybrid_compact_suv'}
        elif any(kw in model_lower for kw in ['highlander', 'pilot', 'santa fe', 'sorento', 'explorer', 'pathfinder', 'mdx', 'telluride', 'palisade']):
            return {'city': 36, 'highway': 35, 'combined': 36, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_hybrid_midsize_suv'}
        # Lexus hybrids ONLY (RX, NX, UX, etc. with h-suffix like 300h, 450h)
        elif any(kw in model_lower for kw in ['rx', 'nx', 'ux', 'gx', 'x3', 'x5', 'q5', 'q7', 'xc60', 'xc90']) or (make_lower == 'lexus'):
            return {'city': 36, 'highway': 35, 'combined': 36, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_hybrid_luxury_suv'}
        
        # ===== HYBRID MINIVANS =====
        elif any(kw in model_lower for kw in ['sienna', 'pacifica', 'carnival', 'odyssey']):
            return {'city': 36, 'highway': 36, 'combined': 36, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_hybrid_minivan'}
        
        # ===== HYBRID TRUCKS =====
        elif any(kw in model_lower for kw in ['f-150', 'silverado', 'tundra', 'ram', 'titan']):
            return {'city': 25, 'highway': 26, 'combined': 25, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_hybrid_fullsize_truck'}
        elif any(kw in model_lower for kw in ['maverick', 'ranger', 'colorado', 'tacoma', 'frontier', 'gladiator', 'ridgeline']):
            return {'city': 42, 'highway': 33, 'combined': 37, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_hybrid_midsize_truck'}
        
        # ===== DEFAULT HYBRID =====
        else:
            return {'city': 45, 'highway': 42, 'combined': 44, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_hybrid_default'}
    
    # ==================== NON-HYBRID GAS VEHICLES ====================
    
    # Truck detection
    if any(kw in model_lower for kw in ['silverado', 'f-150', 'ram', 'tundra', 'titan', 'ridgeline', 'frontier', 'tacoma', 'colorado', 'ranger', 'gladiator']):
        if any(kw in model_lower for kw in ['tacoma', 'colorado', 'ranger', 'frontier', 'gladiator']):
            return {'city': 20, 'highway': 24, 'combined': 22, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_midsize_truck'}
        else:
            return {'city': 18, 'highway': 24, 'combined': 20, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_fullsize_truck'}
    
    # SUV detection
    if any(kw in model_lower for kw in ['suv', 'explorer', 'pilot', 'highlander', 'suburban', 'tahoe', 'yukon', 'expedition', 'sequoia', 'armada', 'durango']):
        if any(kw in model_lower for kw in ['suburban', 'tahoe', 'yukon', 'expedition', 'sequoia', 'armada']):
            return {'city': 16, 'highway': 23, 'combined': 19, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_fullsize_suv'}
        else:
            return {'city': 20, 'highway': 28, 'combined': 23, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_midsize_suv'}
    
    # Luxury brand detection
    if make_lower in ['bmw', 'mercedes-benz', 'audi', 'lexus', 'acura', 'infiniti', 'cadillac', 'lincoln', 'genesis', 'porsche']:
        return {'city': 22, 'highway': 30, 'combined': 25, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_luxury'}
    
    # Sports car detection
    if any(kw in model_lower for kw in ['corvette', 'mustang', 'camaro', 'challenger', 'charger', '911', 'cayman', 'boxster', 'supra', 'z', '370z', '400z']):
        return {'city': 16, 'highway': 25, 'combined': 19, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_sports'}
    
    # Compact car detection
    if any(kw in model_lower for kw in ['civic', 'corolla', 'elantra', 'sentra', 'versa', 'forte', 'rio', 'accent', 'yaris', 'fit']):
        return {'city': 30, 'highway': 38, 'combined': 33, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_compact'}
    
    # Minivan detection
    if any(kw in model_lower for kw in ['odyssey', 'pacifica', 'carnival', 'sienna', 'caravan']):
        return {'city': 19, 'highway': 28, 'combined': 22, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_minivan'}
    
    # Default sedan
    return {'city': 25, 'highway': 32, 'combined': 28, 'mpge_combined': 0, 'is_electric': False, 'source': 'estimated_default'}

def get_mpg_display_text(mpg_data: dict) -> str:
    """Generate user-friendly MPG display text"""
    
    if mpg_data['is_electric']:
        mpge = mpg_data.get('mpge_combined', 0)
        return f"{mpge} MPGe (Electric)"
    else:
        combined = mpg_data.get('combined', 0)
        city = mpg_data.get('city', 0)
        highway = mpg_data.get('highway', 0)
        return f"{combined} MPG ({city} city / {highway} hwy)"
    
def estimate_annual_fuel_cost(mpg_data: dict, annual_mileage: int, fuel_price: float, 
                            electricity_rate: float = 0.12, charging_preference: str = 'mixed',
                            driving_style: str = 'normal', terrain: str = 'flat') -> float:
    """
    Estimate annual fuel cost based on MPG data with driving adjustments
    
    For electric vehicles:
    - Uses EVCostCalculator with MPGe-derived efficiency (kWh per 100 miles)
    - Accounts for charging preference and efficiency losses
    - Applies driving style and terrain adjustments to base efficiency
    
    For gasoline vehicles:
    - Applies driving style and terrain adjustments to MPG
    - Calculates annual gallons and cost
    
    Args:
        mpg_data: Dictionary containing vehicle efficiency data
        annual_mileage: Annual miles driven
        fuel_price: Price per gallon for gas vehicles
        electricity_rate: Base home electricity rate ($/kWh) for EVs
        charging_preference: 'home_primary', 'mixed', or 'public_heavy'
        driving_style: 'gentle', 'normal', or 'aggressive'
        terrain: 'flat' or 'hilly'
    
    Returns:
        Annual fuel/electricity cost in dollars
    """
    
    # Driving style efficiency multipliers (matches FuelCostCalculator)
    driving_style_multipliers = {
        'gentle': 1.15,     # 15% better efficiency
        'normal': 1.0,      # Baseline
        'aggressive': 0.85  # 15% worse efficiency
    }
    
    # Terrain efficiency multipliers (matches FuelCostCalculator)
    terrain_multipliers = {
        'flat': 1.05,       # 5% better efficiency
        'hilly': 0.95       # 5% worse efficiency
    }
    
    # Get multipliers
    style_multiplier = driving_style_multipliers.get(driving_style, 1.0)
    terrain_multiplier = terrain_multipliers.get(terrain, 1.0)
    combined_multiplier = style_multiplier * terrain_multiplier
    
    if mpg_data['is_electric']:
        # Electric vehicle calculation using EVCostCalculator
        mpge = mpg_data.get('mpge_combined', 120)
        if mpge > 0:
            # Apply driving adjustments to MPGe first
            adjusted_mpge = mpge * combined_multiplier
            
            # Convert adjusted MPGe to kWh per 100 miles
            # MPGe is based on 33.7 kWh = 1 gallon gasoline equivalent
            kwh_per_mile = 33.7 / adjusted_mpge
            vehicle_efficiency = kwh_per_mile * 100  # Convert to kWh per 100 miles
            
            # Use EVCostCalculator for realistic cost calculation
            try:
                from models.fuel.electric_vehicle_utils import EVCostCalculator
                ev_calc = EVCostCalculator()
                
                annual_cost = ev_calc.calculate_annual_electricity_cost(
                    annual_mileage=annual_mileage,
                    vehicle_efficiency=vehicle_efficiency,
                    electricity_rate=electricity_rate,
                    charging_preference=charging_preference
                )
                return annual_cost
            except ImportError:
                # Fallback to simple calculation if EVCostCalculator not available
                annual_kwh = annual_mileage * kwh_per_mile
                return annual_kwh * electricity_rate
        return 0
    else:
        # Gasoline vehicle calculation with driving adjustments
        combined_mpg = mpg_data.get('combined', 25)
        if combined_mpg > 0:
            # Apply driving style and terrain adjustments
            adjusted_mpg = combined_mpg * combined_multiplier
            annual_gallons = annual_mileage / adjusted_mpg
            return annual_gallons * fuel_price
        return 0

def get_fuel_efficiency_rating(mpg_data: dict) -> str:
    """Get fuel efficiency rating (Excellent, Good, Fair, Poor)"""
    
    if mpg_data['is_electric']:
        mpge = mpg_data.get('mpge_combined', 0)
        if mpge >= 130:
            return "Excellent"
        elif mpge >= 110:
            return "Good" 
        elif mpge >= 90:
            return "Fair"
        else:
            return "Poor"
    else:
        combined_mpg = mpg_data.get('combined', 0)
        if combined_mpg >= 35:
            return "Excellent"
        elif combined_mpg >= 28:
            return "Good"
        elif combined_mpg >= 22:
            return "Fair"
        else:
            return "Poor"

def compare_mpg_to_class_average(mpg_data: dict, make: str, model: str) -> dict:
    """Compare vehicle MPG to class average"""
    
    model_lower = model.lower()
    
    # Determine vehicle class
    if any(keyword in model_lower for keyword in ['civic', 'corolla', 'elantra', 'sentra']):
        class_name = "Compact Car"
        class_avg = 33
    elif any(keyword in model_lower for keyword in ['camry', 'accord', 'altima', 'malibu']):
        class_name = "Midsize Sedan"
        class_avg = 30
    elif any(keyword in model_lower for keyword in ['rav4', 'cr-v', 'rogue', 'equinox']):
        class_name = "Compact SUV"
        class_avg = 28
    elif any(keyword in model_lower for keyword in ['pilot', 'highlander', 'explorer']):
        class_name = "Midsize SUV"
        class_avg = 24
    elif any(keyword in model_lower for keyword in ['silverado', 'f-150', 'ram']):
        class_name = "Full-Size Truck"
        class_avg = 21
    elif make.lower() in ['bmw', 'mercedes-benz', 'audi', 'lexus']:
        class_name = "Luxury Vehicle"
        class_avg = 26
    else:
        class_name = "Overall Average"
        class_avg = 27
    
    vehicle_mpg = mpg_data.get('combined', 0) if not mpg_data['is_electric'] else mpg_data.get('mpge_combined', 0)
    
    if mpg_data['is_electric']:
        # For electric vehicles, compare MPGe
        difference = vehicle_mpg - (class_avg * 4)  # Rough conversion factor
        comparison = "above" if difference > 0 else "below"
    else:
        difference = vehicle_mpg - class_avg
        comparison = "above" if difference > 0 else "below"
    
    return {
        'class_name': class_name,
        'class_average': class_avg,
        'vehicle_mpg': vehicle_mpg,
        'difference': abs(difference),
        'comparison': comparison
    }

# Test the database
if __name__ == "__main__":
    print("=== Vehicle MPG Database Test ===\n")
    
    # Test various vehicles
    test_vehicles = [
        ("Toyota", "Camry", 2024, "LE"),
        ("Honda", "Civic", 2023, "Sport"),
        ("Tesla", "Model 3", 2024, "Long Range"),
        ("BMW", "3 Series", 2023, "330i"),
        ("Ford", "F-150", 2024, "SuperCrew Lariat"),
        ("Chevrolet", "Corvette", 2024, "Stingray"),
        ("Toyota", "Prius", 2024, "LE"),
        ("Unknown", "Unknown", 2024, "Base")  # Test fallback
    ]
    
    for make, model, year, trim in test_vehicles:
        mpg_data = get_vehicle_mpg(make, model, year, trim)
        display_text = get_mpg_display_text(mpg_data)
        efficiency_rating = get_fuel_efficiency_rating(mpg_data)
        comparison = compare_mpg_to_class_average(mpg_data, make, model)
        
        print(f"🚗 {year} {make} {model} {trim}")
        print(f"   MPG: {display_text}")
        print(f"   Rating: {efficiency_rating}")
        print(f"   Class: {comparison['class_name']} (avg: {comparison['class_average']} MPG)")
        print(f"   Comparison: {comparison['difference']:.1f} MPG {comparison['comparison']} class average")
        print(f"   Source: {mpg_data['source']}")
        
        # Estimate fuel cost
        annual_cost_gas = estimate_annual_fuel_cost(mpg_data, 12000, 3.50, 0.12)
        print(f"   Est. Annual Fuel Cost: ${annual_cost_gas:.0f}")
        print()
    
    print("✅ MPG Database ready for integration!")