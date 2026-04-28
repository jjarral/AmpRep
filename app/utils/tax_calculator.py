def calculate_pakistan_income_tax(annual_income):
    """Calculate Pakistan Income Tax for 2025-26"""
    if annual_income <= 600000:
        return 0, {'taxable_income': 0, 'tax': 0, 'surcharge': 0, 'total': 0}
    
    tax = 0
    breakdown = {'slabs': [], 'taxable_income': annual_income - 600000}
    
    slabs = [
        {'min': 600000, 'max': 1200000, 'rate': 0.025, 'fixed': 0},
        {'min': 1200000, 'max': 2200000, 'rate': 0.125, 'fixed': 15000},
        {'min': 2200000, 'max': 3200000, 'rate': 0.20, 'fixed': 140000},
        {'min': 3200000, 'max': 4100000, 'rate': 0.25, 'fixed': 340000},
        {'min': 4100000, 'max': 10000000, 'rate': 0.35, 'fixed': 616000},
        {'min': 10000000, 'max': float('inf'), 'rate': 0.35, 'fixed': 616000, 'surcharge': 0.09}
    ]
    
    for slab in slabs:
        if annual_income > slab['min']:
            taxable_in_slab = min(annual_income, slab['max']) - slab['min']
            if taxable_in_slab > 0:
                slab_tax = slab['fixed'] + (taxable_in_slab * slab['rate'])
                breakdown['slabs'].append({
                    'range': f"{slab['min']:,} - {slab['max']:, if slab['max'] != float('inf') else 'Above'}",
                    'rate': f"{slab['rate']*100}%",
                    'taxable': taxable_in_slab,
                    'tax': slab_tax
                })
                if slab['max'] == float('inf') or annual_income <= slab['max']:
                    tax = slab_tax
                    break
    
    surcharge = tax * 0.09 if annual_income > 10000000 else 0
    breakdown['surcharge'] = surcharge
    breakdown['tax'] = tax
    breakdown['total'] = tax + surcharge
    
    return tax + surcharge, breakdown


def calculate_monthly_tax_deduction(annual_salary):
    """Calculate monthly tax deduction based on projected annual income"""
    annual_tax, breakdown = calculate_pakistan_income_tax(annual_salary)
    return annual_tax / 12, breakdown