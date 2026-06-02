import streamlit as st
import pandas as pd
import math
import io
import json

# =============================================================================
# 0. SESSION STATE INITIALIZATION (For Save/Load Scenarios)
# =============================================================================
default_params = {
    'age': 30, 'max_age': 60, 'house_price': 5000000, 'house_infl': 5.0,
    'tx_cost': 7.0, 'cash_buf': 1000000, 'buf_infl': 6.0, 'income_0': 100000,
    'net_0': 80000, 'inc_growth': 8.0, 'tax_regime': "new", 'basic_m': 50000,
    'hra_m': 20000, 'metro': True, 'bonus_0': 0, 'bonus_mode': 'fixed',
    'bonus_gross': False, 'bonus_gr': 5.0, 'bonus_sav_pct': 100.0,
    'other_80c': 50000, 'nps_ann': 0, 'nps_pct': 0.0, 'slab_infl': 0.0,
    'exp_mode': "fraction", 'exp_frac': 50.0, 'exp_abs': 50000, 'exp_infl': 6.0,
    'rent_0': 20000, 'rent_infl': 8.0, 'loan_enabled': True, 'loan_rate': 8.5,
    'loan_tenure': 20, 'bank_mult': 60, 'emi_mode': "fraction", 'emi_frac': 40.0,
    'emi_fixed': 50000, 'emi_buf': 0.0, 'user_max_loan': 0
}

# Initialize session state for standard inputs
for key, val in default_params.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Initialize session state for Asset table
if 'assets_data' not in st.session_state:
    st.session_state['assets_data'] = [{
        "Asset_Class": "Savings/Equity", "Opening_Value": 0.0, "monthly_contribution": 0.0,
        "Annual Return": 10.0, "Stepup_type": "Percentage", "Stepup_Value": 0.0, 
        "Surplus_Allocation_Percentage": 100.0, "Invest_above_Surplus_Cash": False,
        "Tax_Treatment": "Exempt", "Fixed_Tax_Pct": 0.0
    }]

def handle_scenario_upload():
    uploaded_file = st.session_state.get("scenario_uploader")
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            for k, v in data.get("params", {}).items():
                if k in st.session_state:
                    st.session_state[k] = v
            if "assets" in data:
                st.session_state['assets_data'] = data["assets"]
            st.success("Scenario loaded successfully!")
        except Exception as e:
            st.error(f"Error loading scenario: {e}")

# =============================================================================
# 1. FINANCIAL MATH & TAX MODULE
# =============================================================================

NEW_REGIME_SLABS = [(400_000, 0.00), (800_000, 0.05), (1_200_000, 0.10), (1_600_000, 0.15), (2_000_000, 0.20), (2_400_000, 0.25), (float('inf'), 0.30)]
OLD_REGIME_SLABS = [(250_000, 0.00), (500_000, 0.05), (1_000_000, 0.20), (float('inf'), 0.30)]
SURCHARGE_THRESHOLDS_NEW = [(5_000_000, 0.00), (10_000_000, 0.10), (20_000_000, 0.15), (float('inf'), 0.25)]
SURCHARGE_THRESHOLDS_OLD = [(5_000_000, 0.00), (10_000_000, 0.10), (20_000_000, 0.15), (50_000_000, 0.25), (float('inf'), 0.37)]

HEALTH_EDUCATION_CESS = 0.04
STANDARD_DEDUCTION_OLD = 50_000
STANDARD_DEDUCTION_NEW = 75_000

def emi_monthly(principal, annual_interest_rate, years):
    if principal <= 0 or years <= 0: return 0.0
    n = years * 12
    if annual_interest_rate == 0: return principal / n
    r = annual_interest_rate / 12
    return principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)

def max_loan_from_emi(emi_amount, annual_interest_rate, years):
    if emi_amount <= 0 or years <= 0: return 0.0
    n = years * 12
    if annual_interest_rate == 0: return emi_amount * n
    r = annual_interest_rate / 12
    return emi_amount * (((1 + r) ** n) - 1) / (r * ((1 + r) ** n))

def _scale_slabs(slabs, factor): return [(limit * factor if limit != float('inf') else float('inf'), rate) for limit, rate in slabs]
def _slab_tax(annual_income, slabs):
    tax, prev = 0.0, 0.0
    for limit, rate in slabs:
        if annual_income <= prev: break
        tax += (min(annual_income, limit) - prev) * rate
        prev = limit
    return tax

def _surcharge_rate(annual_income, regime):
    thresholds = SURCHARGE_THRESHOLDS_NEW if regime == "new" else SURCHARGE_THRESHOLDS_OLD
    for limit, rate in thresholds:
        if annual_income <= limit: return rate
    return thresholds[-1][1]

def compute_annual_tax(annual_gross, tax_regime, home_loan_interest_paid=0.0, home_loan_principal_paid=0.0, other_80c_investments=0.0, basic_monthly=0.0, hra_received_monthly=0.0, rent_paid_monthly=0.0, metro_city=True, employer_nps_annual=0.0, nps_pct_of_basic=0.0, slab_scale_factor=1.0):
    nps_deduction = employer_nps_annual if employer_nps_annual > 0 else (basic_monthly * 12 * (nps_pct_of_basic / 100.0) if basic_monthly > 0 else 0.0)
    nps_deduction = min(nps_deduction, basic_monthly * 12 * 0.10 if basic_monthly > 0 else float('inf'))

    if tax_regime == "old":
        hra_ex = 0.0
        if basic_monthly > 0 and hra_received_monthly > 0 and rent_paid_monthly > 0:
            hra_ex = min(hra_received_monthly * 12, (basic_monthly * 12) * (0.50 if metro_city else 0.40), max(0.0, (rent_paid_monthly * 12) - 0.10 * (basic_monthly * 12)))
        total_deductions = STANDARD_DEDUCTION_OLD + hra_ex + min(home_loan_interest_paid, 200_000) + min(home_loan_principal_paid + other_80c_investments, 150_000) + nps_deduction
        taxable_income = max(0.0, annual_gross - total_deductions)
        base_tax = _slab_tax(taxable_income, _scale_slabs(OLD_REGIME_SLABS, slab_scale_factor))
        if taxable_income <= 500_000 * slab_scale_factor: base_tax = max(0.0, base_tax - 12_500)
    else:
        total_deductions = STANDARD_DEDUCTION_NEW + nps_deduction
        taxable_income = max(0.0, annual_gross - total_deductions)
        base_tax = _slab_tax(taxable_income, _scale_slabs(NEW_REGIME_SLABS, slab_scale_factor))
        if taxable_income <= 1_200_000 * slab_scale_factor: base_tax = 0.0
        elif taxable_income <= 1_275_000 * slab_scale_factor: base_tax = min(base_tax, taxable_income - 1_200_000 * slab_scale_factor)

    surcharge = base_tax * _surcharge_rate(taxable_income, tax_regime)
    cess = (base_tax + surcharge) * HEALTH_EDUCATION_CESS
    total_tax = base_tax + surcharge + cess

    return {
        'gross_income': annual_gross, 'taxable_income': taxable_income, 'total_tax': total_tax,
        'take_home_annual': annual_gross - total_tax, 'take_home_monthly': (annual_gross - total_tax) / 12,
        'effective_rate': (total_tax / annual_gross) if annual_gross > 0 else 0.0
    }

# =============================================================================
# 2. PORTFOLIO & AFFORDABILITY ENGINE
# =============================================================================
TIMING_FACTORS = {'start': lambda r: (1 + r), 'mid': lambda r: (1 + r) ** 0.5, 'end': lambda r: 1.0, 'monthly': lambda r: (1 + r) ** 0.5}

def simulate_portfolio(params, asset_classes):
    series, n = [], len(asset_classes)
    asset_balances = [ac["initial_value"] for ac in asset_classes]
    cash_accumulated = 0.0  

    for t in range(params['max_years'] + 1):
        gross_monthly = params['income_0'] * ((1 + params['inc_growth']) ** t)
        gross_annual = gross_monthly * 12
        rent_monthly = params['rent_0'] * ((1 + params['rent_infl']) ** t)
        slab_scale = (1 + params['slab_infl']) ** t
        
        # Standard Salary Tax
        tax_info = compute_annual_tax(
            annual_gross=gross_annual, tax_regime=params['tax_regime'], other_80c_investments=params['other_80c'],
            basic_monthly=params['basic_m'], hra_received_monthly=params['hra_m'], rent_paid_monthly=rent_monthly,
            metro_city=params['metro'], employer_nps_annual=params['nps_ann'], nps_pct_of_basic=params['nps_pct'], slab_scale_factor=slab_scale
        )
        
        # Dynamic Asset Tax Blending (Recalculate Effective Rate with Slab Assets)
        slab_asset_income = sum((asset_balances[i] * ac['annual_return']) for i, ac in enumerate(asset_classes) if ac['tax_treatment'] == 'Taxed at slab rate')
        
        if slab_asset_income > 0:
            revised_tax_info = compute_annual_tax(gross_annual + slab_asset_income, tax_regime=params['tax_regime'], other_80c_investments=params['other_80c'], basic_monthly=params['basic_m'], hra_received_monthly=params['hra_m'], rent_paid_monthly=rent_monthly, metro_city=params['metro'], employer_nps_annual=params['nps_ann'], nps_pct_of_basic=params['nps_pct'], slab_scale_factor=slab_scale)
            revised_eff_rate = revised_tax_info['effective_rate']
        else:
            revised_eff_rate = tax_info['effective_rate']

        th_monthly = params['net_0'] * ((1 + params['inc_growth']) ** t) if params['net_0'] > 0 else tax_info["take_home_monthly"]
        exp_monthly = th_monthly * params['exp_frac'] if params['exp_mode'] == 'fraction' else params['exp_abs'] * ((1 + params['exp_infl']) ** t)
        
        bonus_gross = params['bonus_0'] * ((1 + params['bonus_gr']) ** t) if params['bonus_mode'] == 'fixed' else gross_annual * (params['bonus_0'] / 100.0) * ((1 + params['bonus_gr']) ** t)
        bonus_net = bonus_gross * (1.0 - tax_info['effective_rate']) if params['bonus_gross'] else bonus_gross
        bonus_savings = bonus_net * (params['bonus_sav_pct'] / 100.0)
        
        surplus_yr = max(0.0, th_monthly * 12 - exp_monthly * 12 - rent_monthly * 12) + bonus_savings
        req_liquid = params['cash_buf'] * ((1 + params['buf_infl']) ** t)
        
        sip_yr = []
        sip_subject_to_limit = 0.0
        
        for ac in asset_classes:
            monthly_base = ac.get("monthly_contribution", 0.0)
            monthly_current = monthly_base * ((1 + ac.get("stepup_value", 0.0) / 100.0) ** t) if ac.get("stepup_type", "pct") == "pct" else monthly_base + ac.get("stepup_value", 0.0) * t
            annual_sip = max(0.0, monthly_current * 12)
            sip_yr.append(annual_sip)
            if not ac.get("invest_above_surplus", False):
                sip_subject_to_limit += annual_sip
                
        shortfall_amt = max(0.0, sip_subject_to_limit - surplus_yr)
        excess_amt = max(0.0, surplus_yr - sip_subject_to_limit)
        
        surplus_alloc_in = [0.0] * n
        if excess_amt > 0:
            alloc_pcts = [max(0.0, ac.get("surplus_alloc_pct", 0.0)) for ac in asset_classes]
            total_alloc = sum(alloc_pcts)
            if total_alloc > 0:
                surplus_alloc_in = [(excess_amt * (p / total_alloc)) for p in alloc_pcts]
            else:
                cash_accumulated += excess_amt

        opening_portfolio = sum(asset_balances)
        new_bals = []
        total_added_to_assets = 0.0
        breakdown_lines = []
        
        for i, ac in enumerate(asset_classes):
            gross_r = ac["annual_return"]
            
            # Net Return calculation
            if ac['tax_treatment'] == 'Exempt':
                net_r = gross_r
            elif ac['tax_treatment'] == 'Taxed at fixed rate':
                net_r = gross_r * (1 - ac['fixed_tax_pct'])
            else:
                net_r = gross_r * (1 - revised_eff_rate)

            tf = TIMING_FACTORS.get(ac.get("contribution_timing", "monthly"), TIMING_FACTORS["monthly"])
            total_added = sip_yr[i] + surplus_alloc_in[i]
            total_added_to_assets += total_added
            
            # Compound with Net Return
            new_bal = asset_balances[i] * (1 + net_r) + (total_added) * tf(net_r)
            new_bals.append(new_bal)
            breakdown_lines.append(f"{ac['name']}: ₹{new_bal:,.0f}")
            
        if cash_accumulated > 0:
            breakdown_lines.append(f"Static Cash: ₹{cash_accumulated:,.0f}")
            
        breakdown_str = " \n ".join(breakdown_lines)

        # Effective Return Rate Calculation (Modified Dietz)
        invested_closing = sum(new_bals)
        asset_gains = invested_closing - opening_portfolio - total_added_to_assets
        invested_base = opening_portfolio + (total_added_to_assets / 2)
        eff_return_rate = (asset_gains / invested_base) if invested_base > 0 else 0.0
        
        asset_balances = new_bals
        total_portfolio_value = sum(asset_balances) + cash_accumulated
        
        series.append({
            'year': t, 'portfolio_value': total_portfolio_value, 'opening_portfolio': opening_portfolio,
            'gross_monthly': gross_monthly, 'take_home_monthly': th_monthly, 'expense_monthly': exp_monthly,
            'rent_monthly': rent_monthly, 'surplus_yr': surplus_yr, 'req_liquid': req_liquid,
            'tax_info': tax_info, 'slab_scale': slab_scale, 
            'shortfall_amt': shortfall_amt, 'excess_amt': excess_amt, 'eff_return_rate': eff_return_rate,
            'Breakdown': breakdown_str
        })
    return series

def run_affordability(params, asset_classes):
    series = simulate_portfolio(params, asset_classes)
    res = []
    over_details, under_details = [], []
    
    # Check if Surplus Allocation covers 100% of excess to suppress warning
    total_alloc = sum([ac.get('surplus_alloc_pct', 0.0) for ac in asset_classes])
    perfect_allocation = abs(total_alloc - 100.0) < 0.001

    for t, ps in enumerate(series):
        age = params['age'] + t
        h_t = params['house_price'] * ((1 + params['house_infl']) ** t)
        v_t = ps['portfolio_value']
        outlay = h_t * (1 + params['tx_cost'])
        
        if ps['shortfall_amt'] > 0: over_details.append((age, ps['shortfall_amt']))
        # Only trigger under_details if allocation isn't handled perfectly
        if ps['excess_amt'] > 0 and not perfect_allocation: under_details.append((age, ps['excess_amt']))
        
        max_loan_t, emi_aff_net = 0.0, 0.0
        if params['loan_enabled']:
            emi_aff = ps['take_home_monthly'] * params['emi_frac'] if params['emi_mode'] == 'fraction' else params['emi_fixed']
            emi_aff_net = emi_aff * (1 - params['emi_buf'])
            max_loan_t = min(max_loan_from_emi(emi_aff_net, params['loan_rate'], params['loan_tenure']),
                             ps['gross_monthly'] * params['bank_mult'])
            if params['user_max_loan'] > 0:
                max_loan_t = min(max_loan_t, params['user_max_loan'] * ((1 + params['house_infl']) ** t))
        
        actual_loan = min(max_loan_t, outlay) if params['loan_enabled'] else 0.0
        down_payment = max(0.0, outlay - actual_loan)
        cash_rem = v_t - down_payment
        
        cond_finance = (v_t + max_loan_t) >= outlay
        cond_liquidity = cash_rem >= ps['req_liquid']
        actual_emi = emi_monthly(actual_loan, params['loan_rate'], params['loan_tenure']) if params['loan_enabled'] and actual_loan > 0 else 0.0
        cond_emi = actual_emi <= emi_aff_net if params['loan_enabled'] else True
        
        affordable = cond_finance and cond_liquidity and cond_emi
        
        res.append({
            'Age': age, 'TakeHome/mo': ps['take_home_monthly'], 'Surplus/yr': ps['surplus_yr'],
            'Portfolio': v_t, 'HousePrice': h_t, 'MaxLoan': max_loan_t, 'CashLeft': cash_rem, 
            'EffEMI': actual_emi, 'AffEMI': emi_aff_net, 'Tax%': ps['tax_info']['effective_rate'] * 100, 
            'Eff_Return%': ps['eff_return_rate'] * 100,
            'Affordable': "YES ✓" if affordable else "No",
            'Breakdown': ps['Breakdown']
        })
        
    return res, over_details, under_details

# =============================================================================
# 3. STREAMLIT USER INTERFACE
# =============================================================================

st.set_page_config(page_title="House Affordability Simulator", layout="wide")
st.title("🏠 House Affordability Simulator")

# --- Scenario Save/Load Section ---
with st.expander("💾 Load / Save Scenarios"):
    col_load, col_save = st.columns(2)
    with col_load:
        st.subheader("Load Scenario")
        st.file_uploader("Upload a saved .json file", type="json", key="scenario_uploader", on_change=handle_scenario_upload, help="What: Restores your previously saved inputs.\nHow: Drag and drop a .json scenario file here.\nExample: Drop 'my_house_scenario.json'")
    
    with col_save:
        st.subheader("Export Current Scenario")
        st.write("Save your current inputs below to a file so you can reload them later.")
        
        export_data = {
            "params": {k: st.session_state[k] for k in default_params.keys()},
            "assets": st.session_state['assets_data']
        }
        json_string = json.dumps(export_data, indent=2)
        st.download_button(
            label="📤 Download Current Setup",
            data=json_string,
            file_name="my_house_scenario.json",
            mime="application/json",
            help="What: Saves your current layout.\nHow: Click to download.\nExample: Saves a file to your PC."
        )

tab1, tab2, tab3, tab4 = st.tabs(["👤 Personal & Housing", "💰 Income & Expenses", "📈 Assets & Loan", "📊 Results"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Your Details")
        st.number_input("Current Age", min_value=18, max_value=80, key="age", help="What: Your current age.\nHow: Enter your age in years.\nExample: 30")
        st.number_input("Simulate up to age", min_value=19, key="max_age", help="What: How far into the future to calculate.\nHow: Enter an age greater than your current age.\nExample: 60")
        
    with col2:
        st.subheader("Target Property")
        st.number_input("House Price Today (₹)", step=500_000, key="house_price", help="What: Current cost of your target property.\nHow: Enter the value in Rupees.\nExample: 5000000")
        st.number_input("Annual Price Inflation (%)", key="house_infl", help="What: Expected annual increase in property prices.\nHow: Enter as a percentage.\nExample: 5.0")
        st.number_input("Transaction Costs (%)", key="tx_cost", help="What: Registration, stamp duty, and brokerage fees.\nHow: Enter as a percentage of property value.\nExample: 7.0")
        st.number_input("Required Cash Buffer (₹)", step=100_000, key="cash_buf", help="What: Emergency cash you want left over after buying the house.\nHow: Enter amount in Rupees.\nExample: 1000000")
        st.number_input("Buffer Inflation (%)", key="buf_infl", help="What: Annual increase in your required emergency cash.\nHow: Enter as a percentage.\nExample: 6.0")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Income & Taxes")
        st.number_input("Monthly Gross Income (₹)", step=10_000, key="income_0", help="What: Total monthly salary before deductions.\nHow: Enter amount in Rupees.\nExample: 100000")
        st.number_input("Monthly Net Take-Home (₹)", step=10_000, key="net_0", help="What: Actual monthly in-hand salary.\nHow: Enter amount in Rupees.\nExample: 80000")
        st.number_input("Income Growth Rate (%)", key="inc_growth", help="What: Expected annual salary increment.\nHow: Enter as a percentage.\nExample: 8.0")
        st.selectbox("Tax Regime", options=["new", "old"], format_func=lambda x: "New Regime" if x == "new" else "Old Regime", key="tax_regime", help="What: The income tax regime you file under.\nHow: Select New or Old.\nExample: New Regime")
        
        with st.expander("Advanced Tax Settings"):
            st.number_input("Basic Salary (₹/mo)", key="basic_m", help="What: Basic component of your salary.\nHow: Enter amount in Rupees.\nExample: 50000")
            st.number_input("HRA Received (₹/mo)", key="hra_m", help="What: House Rent Allowance received.\nHow: Enter amount in Rupees.\nExample: 20000")
            st.checkbox("Metro City?", key="metro", help="What: Determines 50% vs 40% HRA exemption.\nHow: Check if you live in a Metro.\nExample: Checked for Mumbai")
            st.number_input("Annual Bonus (₹)", key="bonus_0", help="What: Expected yearly bonus amount.\nHow: Enter amount in Rupees.\nExample: 150000")
            st.number_input("Bonus Growth (%)", key="bonus_gr", help="What: Annual increment of your bonus.\nHow: Enter as a percentage.\nExample: 5.0")
            st.number_input("Bonus Savings (%)", key="bonus_sav_pct", help="What: How much of your bonus you save vs spend.\nHow: Enter as a percentage.\nExample: 100.0 means you save all of it.")
            st.number_input("Other 80C (₹/yr)", key="other_80c", help="What: Deductions like ELSS or LIC.\nHow: Enter yearly amount.\nExample: 50000")
            st.number_input("Employer NPS (₹/yr)", key="nps_ann", help="What: Corporate NPS contribution.\nHow: Enter yearly amount.\nExample: 50000")
            st.number_input("NPS % of Basic", key="nps_pct", help="What: NPS contribution as % of basic salary.\nHow: Enter as percentage.\nExample: 10.0")
            st.number_input("Slab Inflation (%)", key="slab_infl", help="What: Annual increase in tax slab limits.\nHow: Enter as percentage. (Usually 0)\nExample: 0.0")

    with col2:
        st.subheader("Expenses")
        st.radio("Expense Mode", ["fraction", "absolute"], format_func=lambda x: "% of Take-Home" if x=="fraction" else "Fixed ₹ Amount", key="exp_mode", help="What: How to calculate living expenses.\nHow: Choose percentage or fixed amount.\nExample: % of Take-Home")
        st.number_input("Expenses (% of Take-Home)", key="exp_frac", help="What: Living costs as a percentage of your salary.\nHow: Enter percentage.\nExample: 50.0")
        st.number_input("Fixed Expenses (₹/mo)", key="exp_abs", help="What: Absolute fixed monthly living costs.\nHow: Enter amount in Rupees.\nExample: 40000")
        st.number_input("Expense Inflation (%)", key="exp_infl", help="What: Inflation rate on your fixed expenses.\nHow: Enter as percentage.\nExample: 6.0")
        st.number_input("Current Rent (₹/mo)", key="rent_0", help="What: Current monthly house rent.\nHow: Enter amount in Rupees.\nExample: 25000")
        st.number_input("Rent Inflation (%)", key="rent_infl", help="What: Expected annual rent increase.\nHow: Enter as percentage.\nExample: 8.0")

with tab3:
    st.subheader("Investment Accounts / Assets")
    
    edited_assets_df = st.data_editor(
        pd.DataFrame(st.session_state['assets_data']), 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "Stepup_type": st.column_config.SelectboxColumn("Stepup_type", options=["Percentage", "Fixed"], required=True, help="How your SIP increases yearly."),
            "Invest_above_Surplus_Cash": st.column_config.CheckboxColumn("Invest above Surplus Cash", help="Check if funding comes from external sources (e.g. Employer)."),
            "Tax_Treatment": st.column_config.SelectboxColumn("Tax Treatment", options=["Exempt", "Taxed at slab rate", "Taxed at fixed rate"], required=True, help="How the asset's returns are taxed."),
            "Fixed_Tax_Pct": st.column_config.NumberColumn("Fixed Tax %", min_value=0.0, max_value=100.0, help="Only applies if 'Taxed at fixed rate' is selected.")
        }
    )
    
    tot_open = sum(row.get("Opening_Value", 0.0) for _, row in edited_assets_df.iterrows())
    tot_sip = sum(row.get("monthly_contribution", 0.0) for _, row in edited_assets_df.iterrows())
    col_t1, col_t2 = st.columns(2)
    col_t1.metric("Total Opening Balance", f"₹ {tot_open:,.0f}", help="Sum of all initial values above.")
    col_t2.metric("Total Monthly SIPs", f"₹ {tot_sip:,.0f}", help="Sum of all scheduled monthly contributions.")
    
    st.session_state['assets_data'] = edited_assets_df.to_dict(orient="records")
    
    asset_classes = []
    for _, row in edited_assets_df.iterrows():
        asset_classes.append({
            "name": row.get("Asset_Class", "Asset"),
            "initial_value": row.get("Opening_Value", 0.0),
            "monthly_contribution": row.get("monthly_contribution", 0.0),
            "annual_return": row.get("Annual Return", 0.0) / 100.0,
            "stepup_type": "pct" if row.get("Stepup_type") == "Percentage" else "fixed",
            "stepup_value": row.get("Stepup_Value", 0.0),
            "surplus_alloc_pct": row.get("Surplus_Allocation_Percentage", 0.0),
            "invest_above_surplus": row.get("Invest_above_Surplus_Cash", False),
            "tax_treatment": row.get("Tax_Treatment", "Exempt"),
            "fixed_tax_pct": row.get("Fixed_Tax_Pct", 0.0) / 100.0
        })

    st.markdown("---")
    st.subheader("Home Loan Constraints")
    st.checkbox("Enable Home Loan Financing", key="loan_enabled", help="What: Determines if a loan is used to buy the house.\nHow: Check to enable.\nExample: Checked")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.number_input("Loan Interest Rate (%)", key="loan_rate", help="What: Expected home loan interest rate.\nHow: Enter as percentage.\nExample: 8.5")
    with col2:
        st.number_input("Loan Tenure (Years)", key="loan_tenure", help="What: Duration of the home loan.\nHow: Enter in years.\nExample: 20")
    with col3:
        st.number_input("Bank Eligibility Multiplier", key="bank_mult", help="What: Maximum loan bank gives based on gross salary.\nHow: Enter a multiplier.\nExample: 60 times gross monthly salary.")
        
    st.radio("EMI Limit Mode", ["fraction", "fixed"], key="emi_mode", help="What: How you limit your maximum comfortable EMI.\nHow: Choose percentage or absolute value.\nExample: % of Take-Home")
    st.number_input("Max EMI (% of Take-Home)", key="emi_frac", help="What: Maximum EMI you can pay as % of salary.\nHow: Enter as percentage.\nExample: 40.0")
    st.number_input("Fixed EMI Limit (₹/mo)", key="emi_fixed", help="What: Absolute max EMI you are willing to pay.\nHow: Enter amount in Rupees.\nExample: 50000")
    st.number_input("EMI Safety Buffer (%)", key="emi_buf", help="What: Conservative buffer applied against your EMI limit.\nHow: Enter as percentage.\nExample: 10.0")
    st.number_input("Max Loan I Want (₹) [0 for no cap]", key="user_max_loan", help="What: Hard cap on total loan amount regardless of eligibility.\nHow: Enter amount in Rupees.\nExample: 20000000")

with tab4:
    st.subheader("Simulation Results")
    
    params = {
        'age': st.session_state.age, 'max_years': st.session_state.max_age - st.session_state.age, 
        'house_price': st.session_state.house_price, 'house_infl': st.session_state.house_infl / 100.0,
        'tx_cost': st.session_state.tx_cost / 100.0, 'cash_buf': st.session_
