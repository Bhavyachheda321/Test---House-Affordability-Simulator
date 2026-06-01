import streamlit as st
import pandas as pd
import math

# =============================================================================
# 1. FINANCIAL MATH & TAX MODULE (Preserved from original logic)
# =============================================================================

NEW_REGIME_SLABS = [
    (400_000, 0.00), (800_000, 0.05), (1_200_000, 0.10),
    (1_600_000, 0.15), (2_000_000, 0.20), (2_400_000, 0.25), (float('inf'), 0.30),
]
OLD_REGIME_SLABS = [(250_000, 0.00), (500_000, 0.05), (1_000_000, 0.20), (float('inf'), 0.30)]
SURCHARGE_THRESHOLDS_NEW = [(5_000_000, 0.00), (10_000_000, 0.10), (20_000_000, 0.15), (float('inf'), 0.25)]
SURCHARGE_THRESHOLDS_OLD = [(5_000_000, 0.00), (10_000_000, 0.10), (20_000_000, 0.15), (50_000_000, 0.25), (float('inf'), 0.37)]

HEALTH_EDUCATION_CESS = 0.04
STANDARD_DEDUCTION_OLD = 50_000
STANDARD_DEDUCTION_NEW = 75_000

def fv_lump_sum(pv: float, annual_return: float, years: int) -> float:
    return pv * ((1 + annual_return) ** max(0, years))

def house_price_in_year(current_price: float, housing_inflation: float, years_from_now: int) -> float:
    return current_price * ((1 + housing_inflation) ** years_from_now)

def emi_monthly(principal: float, annual_interest_rate: float, years: int) -> float:
    if principal <= 0 or years <= 0: return 0.0
    n = years * 12
    if annual_interest_rate == 0: return principal / n
    r = annual_interest_rate / 12
    return principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)

def max_loan_from_emi(emi_amount: float, annual_interest_rate: float, years: int) -> float:
    if emi_amount <= 0 or years <= 0: return 0.0
    n = years * 12
    if annual_interest_rate == 0: return emi_amount * n
    r = annual_interest_rate / 12
    return emi_amount * (((1 + r) ** n) - 1) / (r * ((1 + r) ** n))

def _scale_slabs(slabs, factor):
    return [(limit * factor if limit != float('inf') else float('inf'), rate) for limit, rate in slabs]

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

def _compute_hra_exemption(basic_monthly, hra_received_monthly, rent_paid_monthly, metro_city):
    if basic_monthly <= 0 or hra_received_monthly <= 0 or rent_paid_monthly <= 0: return 0.0
    basic_annual, hra_annual, rent_annual = basic_monthly * 12, hra_received_monthly * 12, rent_paid_monthly * 12
    return min(hra_annual, basic_annual * (0.50 if metro_city else 0.40), max(0.0, rent_annual - 0.10 * basic_annual))

def compute_annual_tax(annual_gross, tax_regime, home_loan_interest_paid=0.0, home_loan_principal_paid=0.0, 
                       other_80c_investments=0.0, basic_monthly=0.0, hra_received_monthly=0.0, rent_paid_monthly=0.0, 
                       metro_city=True, employer_nps_annual=0.0, nps_pct_of_basic=0.0, slab_scale_factor=1.0):
    
    nps_deduction = employer_nps_annual if employer_nps_annual > 0 else (basic_monthly * 12 * (nps_pct_of_basic / 100.0) if basic_monthly > 0 else 0.0)
    nps_deduction = min(nps_deduction, basic_monthly * 12 * 0.10 if basic_monthly > 0 else float('inf'))

    if tax_regime == "old":
        hra_exemption = _compute_hra_exemption(basic_monthly, hra_received_monthly, rent_paid_monthly, metro_city)
        total_deductions = STANDARD_DEDUCTION_OLD + hra_exemption + min(home_loan_interest_paid, 200_000) + min(home_loan_principal_paid + other_80c_investments, 150_000) + nps_deduction
        taxable_income = max(0.0, annual_gross - total_deductions)
        base_tax = _slab_tax(taxable_income, _scale_slabs(OLD_REGIME_SLABS, slab_scale_factor))
        if taxable_income <= 500_000 * slab_scale_factor: base_tax = max(0.0, base_tax - 12_500)
    else:
        hra_exemption = 0.0
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
        'effective_rate': (total_tax / annual_gross) if annual_gross > 0 else 0,
        'hra_exemption': hra_exemption, 'nps_deduction': nps_deduction
    }

def compute_asset_income_tax(gross_income, tax_mode, fixed_rate_pct, slab_effective_rate):
    if gross_income <= 0: return {'gross': 0.0, 'tax': 0.0, 'post_tax': 0.0}
    rate = max(0.0, min(1.0, fixed_rate_pct / 100.0)) if tax_mode == "fixed" else slab_effective_rate
    tax = gross_income * rate
    return {'gross': gross_income, 'tax': tax, 'post_tax': gross_income - tax}


# =============================================================================
# 2. PORTFOLIO & AFFORDABILITY ENGINE (Core untouched)
# =============================================================================
TIMING_FACTORS = {'start': lambda r: (1 + r), 'mid': lambda r: (1 + r) ** 0.5, 'end': lambda r: 1.0, 'monthly': lambda r: (1 + r) ** 0.5}

def simulate_portfolio(params, asset_classes):
    series, n = [], len(asset_classes)
    alloc_pcts = [max(0.0, ac.get("surplus_alloc_pct", 0.0)) for ac in asset_classes]
    total_alloc = sum(alloc_pcts)
    alloc_fracs = [p / total_alloc for p in alloc_pcts] if total_alloc > 0 else ([1.0 / n] * n if n > 0 else [])
    
    asset_balances = [ac["initial_value"] for ac in asset_classes]

    for t in range(params['max_years'] + 1):
        gross_monthly = params['income_0'] * ((1 + params['inc_growth']) ** t)
        rent_monthly = params['rent_0'] * ((1 + params['rent_infl']) ** t)
        slab_scale = (1 + params['slab_infl']) ** t
        
        tax_info = compute_annual_tax(
            annual_gross=gross_monthly * 12, tax_regime=params['tax_regime'], other_80c_investments=params['other_80c'],
            basic_monthly=params['basic_m'], hra_received_monthly=params['hra_m'], rent_paid_monthly=rent_monthly,
            metro_city=params['metro'], employer_nps_annual=params['nps_ann'], nps_pct_of_basic=params['nps_pct'], slab_scale_factor=slab_scale
        )
        
        th_monthly = params['net_0'] * ((1 + params['inc_growth']) ** t) if params['net_0'] > 0 else tax_info["take_home_monthly"]
        exp_monthly = th_monthly * params['exp_frac'] if params['exp_mode'] == 'fraction' else params['exp_abs'] * ((1 + params['exp_infl']) ** t)
        
        bonus_gross = params['bonus_0'] * ((1 + params['bonus_gr']) ** t) if params['bonus_mode'] == 'fixed' else (gross_monthly * 12) * (params['bonus_0'] / 100.0) * ((1 + params['bonus_gr']) ** t)
        bonus_net = bonus_gross * (1.0 - tax_info['effective_rate']) if params['bonus_gross'] else bonus_gross
        bonus_savings = bonus_net * (params['bonus_sav_pct'] / 100.0)
        
        surplus_yr = max(0.0, th_monthly * 12 - exp_monthly * 12 - rent_monthly * 12) + bonus_savings
        req_liquid = params['cash_buf'] * ((1 + params['buf_infl']) ** t)
        
        apt_income, ag_income = [], []
        for i, ac in enumerate(asset_classes):
            yld_pct = max(0.0, ac.get("income_yield_pct", 0.0)) / 100.0
            inc_tax = compute_asset_income_tax(asset_balances[i] * yld_pct, ac.get("income_tax_mode", "slab"), ac.get("income_tax_rate_pct", 0.0), tax_info["effective_rate"])
            ag_income.append(inc_tax["gross"])
            apt_income.append(inc_tax["post_tax"])
            
        reinvest_inflow = apt_income # Assuming 100% reinvest back to same asset for simplicity in web UI
        surplus_in = [surplus_yr * f for f in alloc_fracs]
        
        sip_yr = []
        for ac in asset_classes:
            bm = ac.get("annual_contribution", 0.0)
            mt = bm * ((1 + ac.get("stepup_value", 0.0) / 100.0) ** t) if ac.get("stepup_type", "pct") == "pct" else bm + ac.get("stepup_value", 0.0) * t
            sip_yr.append(max(0.0, mt * 12))

        tot_sip = sum(sip_yr)
        return_on_open = sum(asset_balances[i] * ac["annual_return"] for i, ac in enumerate(asset_classes))
        
        new_bals = []
        for i, ac in enumerate(asset_classes):
            cap_r = ac["annual_return"] - (max(0.0, ac.get("income_yield_pct", 0.0)) / 100.0)
            tf = TIMING_FACTORS.get(ac.get("contribution_timing", "monthly"), TIMING_FACTORS["monthly"])
            new_bals.append(asset_balances[i] * (1 + cap_r) + (sip_yr[i] + reinvest_inflow[i] + surplus_in[i]) * tf(cap_r))
            
        opening_portfolio = sum(asset_balances)
        asset_balances = new_bals
        
        series.append({
            'year': t, 'portfolio_value': sum(asset_balances), 'opening_portfolio': opening_portfolio,
            'gross_monthly': gross_monthly, 'take_home_monthly': th_monthly, 'expense_monthly': exp_monthly,
            'rent_monthly': rent_monthly, 'surplus_yr': surplus_yr, 'req_liquid': req_liquid,
            'tax_info': tax_info, 'slab_scale': slab_scale
        })
    return series

def run_affordability(params, asset_classes):
    series = simulate_portfolio(params, asset_classes)
    res = []
    
    for t, ps in enumerate(series):
        age = params['age'] + t
        h_t = house_price_in_year(params['house_price'], params['house_infl'], t)
        v_t = ps['portfolio_value']
        outlay = h_t * (1 + params['tx_cost'])
        
        max_loan_t = 0.0
        emi_aff_net = 0.0
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
            'Affordable': "YES ✓" if affordable else "No"
        })
    return res

# =============================================================================
# 3. STREAMLIT USER INTERFACE
# =============================================================================

st.set_page_config(page_title="House Affordability Simulator", layout="wide")
st.title("🏠 House Affordability Simulator")
st.markdown("Find out exactly when you can afford your target house based on projected savings, income growth, and loan constraints.")

tab1, tab2, tab3, tab4 = st.tabs(["👤 Personal & Housing", "💰 Income & Expenses", "📈 Assets & Loan", "📊 Results"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Your Details")
        age = st.number_input("Current Age", value=30, min_value=18, max_value=80)
        max_age = st.number_input("Simulate up to age", value=60, min_value=age+1)
        
    with col2:
        st.subheader("Target Property")
        house_price = st.number_input("House Price Today (₹)", value=5_000_000, step=500_000)
        house_infl = st.number_input("Annual Price Inflation (%)", value=5.0) / 100.0
        tx_cost = st.number_input("Transaction Costs (%)", value=7.0) / 100.0
        cash_buf = st.number_input("Required Cash Buffer (₹)", value=1_000_000, step=100_000)
        buf_infl = st.number_input("Buffer Inflation (%)", value=6.0) / 100.0

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Income & Taxes")
        income_0 = st.number_input("Monthly Gross Income (₹)", value=100_000, step=10_000)
        net_0 = st.number_input("Monthly Net Take-Home (₹)", value=80_000, step=10_000)
        inc_growth = st.number_input("Income Growth Rate (%)", value=8.0) / 100.0
        tax_regime = st.selectbox("Tax Regime", options=["new", "old"], format_func=lambda x: "New Regime" if x == "new" else "Old Regime")
        
        with st.expander("Advanced Tax Settings (Bonus, 80C, HRA)"):
            basic_m = st.number_input("Basic Salary (₹/mo)", value=50_000)
            hra_m = st.number_input("HRA Received (₹/mo)", value=20_000)
            metro = st.checkbox("Metro City?", value=True)
            bonus_0 = st.number_input("Annual Bonus (₹)", value=0)
            bonus_mode = 'fixed'
            bonus_gross = False
            bonus_gr = st.number_input("Bonus Growth (%)", value=5.0) / 100.0
            bonus_sav_pct = st.number_input("Bonus Savings (%)", value=100.0)
            other_80c = st.number_input("Other 80C (₹/yr)", value=50_000)
            nps_ann = st.number_input("Employer NPS (₹/yr)", value=0)
            nps_pct = st.number_input("NPS % of Basic", value=0.0)
            slab_infl = st.number_input("Slab Inflation (%)", value=0.0) / 100.0

    with col2:
        st.subheader("Expenses")
        exp_mode = st.radio("Expense Mode", ["fraction", "absolute"], format_func=lambda x: "% of Take-Home" if x=="fraction" else "Fixed ₹ Amount")
        exp_frac = st.number_input("Expenses (% of Take-Home)", value=50.0) / 100.0 if exp_mode == "fraction" else 0
        exp_abs = st.number_input("Fixed Expenses (₹/mo)", value=50_000) if exp_mode == "absolute" else 0
        exp_infl = st.number_input("Expense Inflation (%)", value=6.0) / 100.0 if exp_mode == "absolute" else 0
        rent_0 = st.number_input("Current Rent (₹/mo)", value=20_000)
        rent_infl = st.number_input("Rent Inflation (%)", value=8.0) / 100.0

with tab3:
    st.subheader("Investment Accounts / Assets")
    st.info("Edit the table below to add or modify your current assets and SIPs.")
    
    default_assets = pd.DataFrame([{
        "name": "Savings/Equity", "initial_value": 0.0, "annual_contribution": 0.0,
        "annual_return": 10.0, "stepup_type": "pct", "stepup_value": 0.0, "surplus_alloc_pct": 100.0,
    }])
    
    edited_assets_df = st.data_editor(default_assets, num_rows="dynamic", use_container_width=True)
    # Convert back to dict and normalize returns
    asset_classes = edited_assets_df.to_dict(orient="records")
    for ac in asset_classes:
        ac['annual_return'] /= 100.0  # Convert % input to decimal for engine

    st.markdown("---")
    st.subheader("Home Loan Constraints")
    loan_enabled = st.checkbox("Enable Home Loan Financing", value=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        loan_rate = st.number_input("Loan Interest Rate (%)", value=8.5) / 100.0
    with col2:
        loan_tenure = st.number_input("Loan Tenure (Years)", value=20)
    with col3:
        bank_mult = st.number_input("Bank Eligibility Multiplier", value=60)
        
    emi_mode = st.radio("EMI Limit Mode", ["fraction", "fixed"])
    emi_frac = st.number_input("Max EMI (% of Take-Home)", value=40.0) / 100.0 if emi_mode == "fraction" else 0.0
    emi_fixed = st.number_input("Fixed EMI Limit (₹/mo)", value=50_000) if emi_mode == "fixed" else 0.0
    emi_buf = st.number_input("EMI Safety Buffer (%)", value=0.0) / 100.0
    user_max_loan = st.number_input("Max Loan I Want (₹) [0 for no cap]", value=0)

with tab4:
    st.subheader("Simulation Results")
    
    # Pack parameters for engine
    params = {
        'age': age, 'max_years': max_age - age, 'house_price': house_price, 'house_infl': house_infl,
        'tx_cost': tx_cost, 'cash_buf': cash_buf, 'buf_infl': buf_infl, 'income_0': income_0, 
        'net_0': net_0, 'inc_growth': inc_growth, 'tax_regime': tax_regime, 'basic_m': basic_m, 
        'hra_m': hra_m, 'metro': metro, 'bonus_0': bonus_0, 'bonus_mode': bonus_mode, 'bonus_gross': bonus_gross,
        'bonus_gr': bonus_gr, 'bonus_sav_pct': bonus_sav_pct, 'other_80c': other_80c, 'nps_ann': nps_ann,
        'nps_pct': nps_pct, 'slab_infl': slab_infl, 'exp_mode': exp_mode, 'exp_frac': exp_frac,
        'exp_abs': exp_abs, 'exp_infl': exp_infl, 'rent_0': rent_0, 'rent_infl': rent_infl,
        'loan_enabled': loan_enabled, 'loan_rate': loan_rate, 'loan_tenure': loan_tenure,
        'bank_mult': bank_mult, 'emi_mode': emi_mode, 'emi_frac': emi_frac, 'emi_fixed': emi_fixed,
        'emi_buf': emi_buf, 'user_max_loan': user_max_loan
    }
    
    if st.button("▶ Run Simulation", type="primary"):
        results = run_affordability(params, asset_classes)
        df_res = pd.DataFrame(results)
        
        # Format the dataframe columns for better readability
        format_dict = {
            'TakeHome/mo': '₹{:,.0f}', 'Surplus/yr': '₹{:,.0f}', 'Portfolio': '₹{:,.0f}',
            'HousePrice': '₹{:,.0f}', 'MaxLoan': '₹{:,.0f}', 'CashLeft': '₹{:,.0f}',
            'EffEMI': '₹{:,.0f}', 'AffEMI': '₹{:,.0f}', 'Tax%': '{:.1f}%'
        }
        
        affordable_rows = df_res[df_res['Affordable'] == "YES ✓"]
        if not affordable_rows.empty:
            earliest_age = affordable_rows.iloc[0]['Age']
            st.success(f"### 🎉 Earliest Affordable Age: {earliest_age}")
        else:
            st.error(f"### ❌ Not affordable by age {max_age}")
            
        st.dataframe(df_res.style.format(format_dict), use_container_width=True, height=600)
