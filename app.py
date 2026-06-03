import streamlit as st
import pandas as pd
import math
import io
import json

# =============================================================================
# PAGE CONFIG — must be first Streamlit call
# =============================================================================
st.set_page_config(
    page_title="House Affordability Simulator",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# CUSTOM CSS — light theme, high contrast
# =============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
    --bg:#f0f4f8; --surface:#ffffff; --surface2:#f8fafc;
    --border:#d1dbe8; --border-dark:#b0bfcc;
    --accent:#1d6fce; --accent-dark:#155bb5; --accent-soft:#e8f0fb;
    --green:#166534; --green-bg:#dcfce7; --green-border:#86efac;
    --red:#991b1b; --red-bg:#fee2e2; --red-border:#fca5a5;
    --amber:#92400e; --amber-bg:#fef3c7; --amber-border:#fcd34d;
    --text:#0f172a; --text-secondary:#334155; --text-muted:#64748b;
    --radius:12px; --radius-sm:8px;
    --shadow-sm:0 1px 3px rgba(0,0,0,.08),0 1px 2px rgba(0,0,0,.05);
    --shadow:0 4px 12px rgba(0,0,0,.08),0 2px 4px rgba(0,0,0,.04);
}
html,body,[class*="css"]{font-family:'Plus Jakarta Sans',sans-serif !important;color:var(--text) !important;}
.stApp{background:var(--bg) !important;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:1.5rem 2rem 3rem !important;max-width:1400px;}

/* Hero */
.hero{background:linear-gradient(135deg,#1d6fce 0%,#2d4a9e 60%,#1e3a8a 100%);border-radius:16px;padding:2rem 2.5rem;margin-bottom:1.5rem;position:relative;overflow:hidden;box-shadow:0 8px 24px rgba(29,111,206,.25);}
.hero::before{content:'';position:absolute;top:-50px;right:-50px;width:200px;height:200px;background:radial-gradient(circle,rgba(255,255,255,.12) 0%,transparent 70%);pointer-events:none;}
.hero-title{font-size:2rem;font-weight:800;letter-spacing:-.02em;color:#ffffff;margin:0 0 .4rem;text-shadow:0 1px 3px rgba(0,0,0,.2);}
.hero-sub{font-size:.95rem;color:rgba(255,255,255,.85);margin:0;font-weight:500;max-width:600px;line-height:1.5;}

/* Metric cards */
.metric-row{display:flex;gap:1rem;margin-bottom:1.5rem;flex-wrap:wrap;}
.metric-card{flex:1;min-width:165px;background:var(--surface);border:1.5px solid var(--border);border-radius:var(--radius);padding:1.1rem 1.3rem;box-shadow:var(--shadow-sm);transition:box-shadow .2s,border-color .2s;}
.metric-card:hover{box-shadow:var(--shadow);border-color:var(--accent);}
.metric-card .label{font-size:.7rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--text-muted);margin-bottom:.5rem;}
.metric-card .value{font-size:1.5rem;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--text);line-height:1;}
.metric-card .delta{font-size:.74rem;color:var(--text-muted);margin-top:.35rem;font-weight:500;}
.metric-card.blue{border-color:#93c5fd;background:#eff6ff;}.metric-card.blue .value{color:var(--accent-dark);}
.metric-card.green{border-color:var(--green-border);background:var(--green-bg);}.metric-card.green .value{color:var(--green);}
.metric-card.red{border-color:var(--red-border);background:var(--red-bg);}.metric-card.red .value{color:var(--red);}

/* Section headers */
.section-header{display:flex;align-items:center;gap:.65rem;margin:1.6rem 0 .85rem;padding-bottom:.6rem;border-bottom:2px solid var(--border);}
.section-header .icon{font-size:1rem;width:32px;height:32px;background:var(--accent-soft);border-radius:8px;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.section-header h3{font-size:.92rem;font-weight:700;letter-spacing:.01em;color:var(--text);margin:0;text-transform:uppercase;}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{background:var(--surface) !important;border-radius:var(--radius) !important;padding:5px !important;gap:3px !important;border:1.5px solid var(--border) !important;box-shadow:var(--shadow-sm) !important;}
.stTabs [data-baseweb="tab"]{background:transparent !important;border-radius:var(--radius-sm) !important;color:var(--text-secondary) !important;font-size:.85rem !important;font-weight:600 !important;padding:.5rem 1.1rem !important;transition:all .15s !important;}
.stTabs [data-baseweb="tab"]:hover{background:var(--accent-soft) !important;color:var(--accent) !important;}
.stTabs [aria-selected="true"]{background:var(--accent) !important;color:#ffffff !important;box-shadow:0 2px 6px rgba(29,111,206,.3) !important;}
.stTabs [data-baseweb="tab-panel"]{padding-top:1.2rem !important;}

/* Inputs */
.stNumberInput > div > div > input,.stTextInput > div > div > input{background:var(--surface) !important;border:1.5px solid var(--border) !important;border-radius:var(--radius-sm) !important;color:var(--text) !important;font-family:'Plus Jakarta Sans',sans-serif !important;font-size:.9rem !important;font-weight:500 !important;}
.stNumberInput > div > div > input:focus,.stTextInput > div > div > input:focus{border-color:var(--accent) !important;box-shadow:0 0 0 3px rgba(29,111,206,.15) !important;}
.stSelectbox > div > div{background:var(--surface) !important;border:1.5px solid var(--border) !important;border-radius:var(--radius-sm) !important;color:var(--text) !important;}
label[data-testid="stWidgetLabel"] > div,label[data-testid="stWidgetLabel"] p{font-size:.78rem !important;font-weight:700 !important;color:var(--text-secondary) !important;letter-spacing:.04em !important;text-transform:uppercase !important;}

/* Expander */
details > summary{background:var(--surface2) !important;border:1.5px solid var(--border) !important;border-radius:var(--radius-sm) !important;padding:.6rem 1rem !important;font-size:.85rem !important;font-weight:600 !important;color:var(--text) !important;cursor:pointer;}
details[open] > summary{border-radius:var(--radius-sm) var(--radius-sm) 0 0 !important;border-bottom:none !important;}
details > div{background:var(--surface) !important;border:1.5px solid var(--border) !important;border-top:none !important;border-radius:0 0 var(--radius-sm) var(--radius-sm) !important;padding:.8rem 1rem !important;}

/* Buttons */
.stButton > button[kind="primary"]{background:linear-gradient(135deg,#1d6fce,#2d4a9e) !important;border:none !important;border-radius:var(--radius-sm) !important;color:#ffffff !important;font-weight:700 !important;font-size:.92rem !important;letter-spacing:.02em !important;padding:.65rem 1.8rem !important;box-shadow:0 3px 10px rgba(29,111,206,.3) !important;transition:all .2s !important;}
.stButton > button[kind="primary"]:hover{transform:translateY(-1px) !important;box-shadow:0 5px 18px rgba(29,111,206,.45) !important;}
.stButton > button[kind="secondary"],.stButton > button:not([kind]){background:var(--surface) !important;border:1.5px solid var(--border-dark) !important;border-radius:var(--radius-sm) !important;color:var(--text-secondary) !important;font-weight:600 !important;}
.stDownloadButton > button{background:var(--surface) !important;border:1.5px solid var(--border-dark) !important;border-radius:var(--radius-sm) !important;color:var(--text) !important;font-weight:600 !important;font-size:.87rem !important;}
.stDownloadButton > button:hover{background:var(--accent-soft) !important;border-color:var(--accent) !important;color:var(--accent) !important;}

/* Dataframe */
.stDataFrame{border-radius:var(--radius) !important;overflow:hidden;box-shadow:var(--shadow-sm);}
[data-testid="stDataFrameResizable"]{border:1.5px solid var(--border) !important;border-radius:var(--radius) !important;}

/* Alerts */
.stAlert,[data-testid="stNotification"]{border-radius:var(--radius-sm) !important;}

/* Result banner */
.result-banner{border-radius:var(--radius);padding:1.4rem 2rem;margin-bottom:1.3rem;border:2px solid;display:flex;align-items:center;gap:1.3rem;box-shadow:var(--shadow-sm);}
.result-banner.success{background:var(--green-bg);border-color:var(--green-border);}
.result-banner.failure{background:var(--red-bg);border-color:var(--red-border);}
.result-banner .emoji{font-size:2.4rem;flex-shrink:0;}
.result-banner .title{font-size:1.35rem;font-weight:800;line-height:1.2;}
.result-banner .sub{font-size:.86rem;margin-top:.3rem;font-weight:500;line-height:1.6;}
.result-banner.success .title{color:var(--green);}
.result-banner.success .sub{color:#166534cc;}
.result-banner.failure .title{color:var(--red);}
.result-banner.failure .sub{color:#991b1baa;}

/* Tip box */
.tip-box{background:var(--accent-soft);border:1.5px solid #93c5fd;border-radius:var(--radius-sm);padding:.75rem 1rem;font-size:.84rem;color:var(--text-secondary);margin-bottom:1.1rem;line-height:1.6;font-weight:500;}
.tip-box strong{color:var(--accent-dark);font-weight:700;}

/* Misc */
hr{border-color:var(--border) !important;margin:1.3rem 0 !important;}
.stCheckbox label p{font-size:.85rem !important;color:var(--text-secondary) !important;font-weight:500 !important;}
.stRadio label p{font-size:.85rem !important;color:var(--text-secondary) !important;font-weight:500 !important;}
[data-testid="stFileUploader"]{background:var(--surface2) !important;border:2px dashed var(--border-dark) !important;border-radius:var(--radius) !important;}
[data-testid="metric-container"]{background:var(--surface) !important;border:1.5px solid var(--border) !important;border-radius:var(--radius) !important;padding:1rem 1.2rem !important;box-shadow:var(--shadow-sm) !important;}
[data-testid="metric-container"] label{color:var(--text-muted) !important;font-size:.78rem !important;font-weight:700 !important;text-transform:uppercase !important;letter-spacing:.05em !important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:var(--text) !important;font-family:'JetBrains Mono',monospace !important;font-weight:700 !important;}
::-webkit-scrollbar{width:6px;height:6px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border-dark);border-radius:4px;}
::-webkit-scrollbar-thumb:hover{background:var(--accent);}
.stCaption,[data-testid="stCaptionContainer"] p{color:var(--text-muted) !important;font-size:.81rem !important;font-weight:500 !important;}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# 0. SESSION STATE
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

for key, val in default_params.items():
    if key not in st.session_state:
        st.session_state[key] = val

if 'assets_table' not in st.session_state:
    st.session_state['assets_table'] = pd.DataFrame([{
        "Asset_Class": "Equity Mutual Fund", "Opening_Value": 500000.0,
        "monthly_contribution": 20000.0, "Annual Return": 12.0,
        "Stepup_type": "Percentage", "Stepup_Value": 5.0,
        "Surplus_Allocation_Percentage": 100.0,
        "Invest_above_Surplus_Cash": False,
        "Tax_Treatment": "Taxed at fixed rate", "Fixed_Tax_Pct": 12.5
    }])

if 'reinvest_table' not in st.session_state:
    st.session_state['reinvest_table'] = pd.DataFrame(
        columns=["Source_Asset", "Destination_Asset", "Allocation_Pct"])

if 'rebalance_table' not in st.session_state:
    st.session_state['rebalance_table'] = pd.DataFrame(
        columns=["Year", "Source_Asset", "Destination_Asset", "Transfer_Type", "Value"])

if 'sim_results' not in st.session_state:
    st.session_state['sim_results'] = None


def handle_scenario_upload():
    f = st.session_state.get("scenario_uploader")
    if f is not None:
        try:
            data = json.load(f)
            for k, v in data.get("params", {}).items():
                if k in st.session_state:
                    st.session_state[k] = v
            if "assets" in data:
                st.session_state['assets_table'] = pd.DataFrame(data["assets"])
            if "reinvest_rules" in data:
                st.session_state['reinvest_table'] = pd.DataFrame(data["reinvest_rules"])
            if "rebalance_events" in data:
                st.session_state['rebalance_table'] = pd.DataFrame(data["rebalance_events"])
            st.success("✅ Scenario loaded successfully!")
        except Exception as e:
            st.error(f"Error loading scenario: {e}")


# =============================================================================
# 1. FINANCIAL MATH & TAX MODULE
# =============================================================================
NEW_REGIME_SLABS = [
    (400_000, 0.00), (800_000, 0.05), (1_200_000, 0.10),
    (1_600_000, 0.15), (2_000_000, 0.20), (2_400_000, 0.25), (float('inf'), 0.30)
]
OLD_REGIME_SLABS = [
    (250_000, 0.00), (500_000, 0.05), (1_000_000, 0.20), (float('inf'), 0.30)
]
SURCHARGE_THRESHOLDS_NEW = [
    (5_000_000, 0.00), (10_000_000, 0.10), (20_000_000, 0.15), (float('inf'), 0.25)
]
SURCHARGE_THRESHOLDS_OLD = [
    (5_000_000, 0.00), (10_000_000, 0.10), (20_000_000, 0.15),
    (50_000_000, 0.25), (float('inf'), 0.37)
]
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


def _scale_slabs(slabs, factor):
    return [(limit * factor if limit != float('inf') else float('inf'), rate)
            for limit, rate in slabs]


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


def compute_annual_tax(annual_gross, tax_regime, home_loan_interest_paid=0.0,
                       home_loan_principal_paid=0.0, other_80c_investments=0.0,
                       basic_monthly=0.0, hra_received_monthly=0.0,
                       rent_paid_monthly=0.0, metro_city=True,
                       employer_nps_annual=0.0, nps_pct_of_basic=0.0,
                       slab_scale_factor=1.0):
    nps_deduction = (employer_nps_annual if employer_nps_annual > 0
                     else (basic_monthly * 12 * (nps_pct_of_basic / 100.0)
                           if basic_monthly > 0 else 0.0))
    nps_deduction = min(nps_deduction,
                        basic_monthly * 12 * 0.10 if basic_monthly > 0 else float('inf'))

    if tax_regime == "old":
        hra_ex = 0.0
        if basic_monthly > 0 and hra_received_monthly > 0 and rent_paid_monthly > 0:
            hra_ex = min(
                hra_received_monthly * 12,
                (basic_monthly * 12) * (0.50 if metro_city else 0.40),
                max(0.0, (rent_paid_monthly * 12) - 0.10 * (basic_monthly * 12))
            )
        total_deductions = (STANDARD_DEDUCTION_OLD + hra_ex +
                            min(home_loan_interest_paid, 200_000) +
                            min(home_loan_principal_paid + other_80c_investments, 150_000) +
                            nps_deduction)
        taxable_income = max(0.0, annual_gross - total_deductions)
        base_tax = _slab_tax(taxable_income, _scale_slabs(OLD_REGIME_SLABS, slab_scale_factor))
        if taxable_income <= 500_000 * slab_scale_factor:
            base_tax = max(0.0, base_tax - 12_500)
    else:
        total_deductions = STANDARD_DEDUCTION_NEW + nps_deduction
        taxable_income = max(0.0, annual_gross - total_deductions)
        base_tax = _slab_tax(taxable_income, _scale_slabs(NEW_REGIME_SLABS, slab_scale_factor))
        if taxable_income <= 1_200_000 * slab_scale_factor:
            base_tax = 0.0
        elif taxable_income <= 1_275_000 * slab_scale_factor:
            base_tax = min(base_tax, taxable_income - 1_200_000 * slab_scale_factor)

    surcharge = base_tax * _surcharge_rate(taxable_income, tax_regime)
    cess = (base_tax + surcharge) * HEALTH_EDUCATION_CESS
    total_tax = base_tax + surcharge + cess

    return {
        'gross_income': annual_gross, 'taxable_income': taxable_income,
        'total_tax': total_tax, 'take_home_annual': annual_gross - total_tax,
        'take_home_monthly': (annual_gross - total_tax) / 12,
        'effective_rate': (total_tax / annual_gross) if annual_gross > 0 else 0.0
    }


# =============================================================================
# 2. PORTFOLIO & AFFORDABILITY ENGINE
# =============================================================================
TIMING_FACTORS = {
    'start': lambda r: (1 + r),
    'mid':   lambda r: (1 + r) ** 0.5,
    'end':   lambda r: 1.0,
    'monthly': lambda r: (1 + r) ** 0.5
}


def simulate_portfolio(params, asset_classes, reinvest_rules, rebalance_events):
    series, n = [], len(asset_classes)
    asset_balances = [ac["initial_value"] for ac in asset_classes]
    cash_accumulated = 0.0

    name_to_idx = {ac['name']: i for i, ac in enumerate(asset_classes)}

    reinvest_map = {}
    for r in reinvest_rules:
        src, dest, pct = r['Source_Asset'], r['Destination_Asset'], r['Allocation_Pct']
        if src in name_to_idx and dest in name_to_idx:
            s_idx, d_idx = name_to_idx[src], name_to_idx[dest]
            if s_idx not in reinvest_map: reinvest_map[s_idx] = []
            reinvest_map[s_idx].append((d_idx, pct / 100.0))

    rebalance_map = {}
    for r in rebalance_events:
        yr = r['Year'] - params['age']
        src, dest, t_type, val = r['Source_Asset'], r['Destination_Asset'], r['Transfer_Type'], r['Value']
        if src in name_to_idx and dest in name_to_idx and yr >= 0:
            if yr not in rebalance_map: rebalance_map[yr] = []
            rebalance_map[yr].append((name_to_idx[src], name_to_idx[dest], t_type, val))

    for t in range(params['max_years'] + 1):
        gross_monthly = params['income_0'] * ((1 + params['inc_growth']) ** t)
        gross_annual = gross_monthly * 12
        rent_monthly = params['rent_0'] * ((1 + params['rent_infl']) ** t)
        slab_scale = (1 + params['slab_infl']) ** t

        tax_info = compute_annual_tax(
            annual_gross=gross_annual, tax_regime=params['tax_regime'],
            other_80c_investments=params['other_80c'],
            basic_monthly=params['basic_m'], hra_received_monthly=params['hra_m'],
            rent_paid_monthly=rent_monthly, metro_city=params['metro'],
            employer_nps_annual=params['nps_ann'], nps_pct_of_basic=params['nps_pct'],
            slab_scale_factor=slab_scale
        )

        slab_asset_income = sum(
            asset_balances[i] * ac['annual_return']
            for i, ac in enumerate(asset_classes)
            if ac['tax_treatment'] == 'Taxed at slab rate'
        )
        if slab_asset_income > 0:
            revised = compute_annual_tax(
                gross_annual + slab_asset_income,
                tax_regime=params['tax_regime'],
                other_80c_investments=params['other_80c'],
                basic_monthly=params['basic_m'],
                hra_received_monthly=params['hra_m'],
                rent_paid_monthly=rent_monthly, metro_city=params['metro'],
                employer_nps_annual=params['nps_ann'],
                nps_pct_of_basic=params['nps_pct'],
                slab_scale_factor=slab_scale
            )
            revised_eff_rate = revised['effective_rate']
        else:
            revised_eff_rate = tax_info['effective_rate']

        th_monthly = (params['net_0'] * ((1 + params['inc_growth']) ** t)
                      if params['net_0'] > 0 else tax_info["take_home_monthly"])
        exp_monthly = (th_monthly * params['exp_frac']
                       if params['exp_mode'] == 'fraction'
                       else params['exp_abs'] * ((1 + params['exp_infl']) ** t))

        bonus_gross = (params['bonus_0'] * ((1 + params['bonus_gr']) ** t)
                       if params['bonus_mode'] == 'fixed'
                       else gross_annual * (params['bonus_0'] / 100.0) * ((1 + params['bonus_gr']) ** t))
        bonus_net = bonus_gross * (1.0 - tax_info['effective_rate']) if params['bonus_gross'] else bonus_gross
        bonus_savings = bonus_net * (params['bonus_sav_pct'] / 100.0)

        surplus_yr = max(0.0, th_monthly * 12 - exp_monthly * 12 - rent_monthly * 12) + bonus_savings
        req_liquid = params['cash_buf'] * ((1 + params['buf_infl']) ** t)

        sip_yr = []
        sip_subject_to_limit = 0.0
        for ac in asset_classes:
            mb = ac.get("monthly_contribution", 0.0)
            mc = (mb * ((1 + ac.get("stepup_value", 0.0) / 100.0) ** t)
                  if ac.get("stepup_type", "pct") == "pct"
                  else mb + ac.get("stepup_value", 0.0) * t)
            annual_sip = max(0.0, mc * 12)
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
                surplus_alloc_in = [excess_amt * (p / total_alloc) for p in alloc_pcts]
            else:
                cash_accumulated += excess_amt

        opening_portfolio = sum(asset_balances)
        new_bals = []
        total_added_to_assets = 0.0

        net_returns_generated = []
        for i, ac in enumerate(asset_classes):
            gross_r = ac["annual_return"]
            if ac['tax_treatment'] == 'Exempt':
                net_r = gross_r
            elif ac['tax_treatment'] == 'Taxed at fixed rate':
                net_r = gross_r * (1 - ac['fixed_tax_pct'])
            else:
                net_r = gross_r * (1 - revised_eff_rate)
            net_returns_generated.append(asset_balances[i] * net_r)

        reinvest_inflow = [0.0] * n
        for i in range(n):
            if i in reinvest_map:
                for dest_idx, pct in reinvest_map[i]:
                    reinvest_inflow[dest_idx] += net_returns_generated[i] * pct
            else:
                reinvest_inflow[i] += net_returns_generated[i]

        for i, ac in enumerate(asset_classes):
            tf = TIMING_FACTORS.get(ac.get("contribution_timing", "monthly"), TIMING_FACTORS["monthly"])
            total_added = sip_yr[i] + surplus_alloc_in[i]
            total_added_to_assets += total_added
            new_bals.append(asset_balances[i] + reinvest_inflow[i] + total_added * tf(0))

        if t in rebalance_map:
            for src_i, dest_i, r_type, r_val in rebalance_map[t]:
                transfer_amt = (new_bals[src_i] * (r_val / 100.0)
                                if r_type == 'Percentage'
                                else min(new_bals[src_i], r_val))
                new_bals[src_i] -= transfer_amt
                new_bals[dest_i] += transfer_amt

        breakdown_lines = [f"{ac['name']}: ₹{new_bals[i]:,.0f}"
                           for i, ac in enumerate(asset_classes)]
        if cash_accumulated > 0:
            breakdown_lines.append(f"Static Cash: ₹{cash_accumulated:,.0f}")

        invested_closing = sum(new_bals)
        asset_gains = invested_closing - opening_portfolio - total_added_to_assets
        invested_base = opening_portfolio + (total_added_to_assets / 2)
        eff_return_rate = (asset_gains / invested_base) if invested_base > 0 else 0.0

        asset_balances = new_bals
        total_portfolio_value = sum(asset_balances) + cash_accumulated

        series.append({
            'year': t, 'portfolio_value': total_portfolio_value,
            'opening_portfolio': opening_portfolio,
            'gross_monthly': gross_monthly, 'take_home_monthly': th_monthly,
            'expense_monthly': exp_monthly, 'rent_monthly': rent_monthly,
            'surplus_yr': surplus_yr, 'req_liquid': req_liquid,
            'tax_info': tax_info, 'slab_scale': slab_scale,
            'shortfall_amt': shortfall_amt, 'excess_amt': excess_amt,
            'eff_return_rate': eff_return_rate,
            'Portfolio_Breakdown': "  |  ".join(breakdown_lines)
        })
    return series


def run_affordability(params, asset_classes, reinvest_rules, rebalance_events):
    series = simulate_portfolio(params, asset_classes, reinvest_rules, rebalance_events)
    res = []
    over_details, under_details = [], []
    total_alloc = sum(ac.get('surplus_alloc_pct', 0.0) for ac in asset_classes)
    perfect_allocation = abs(total_alloc - 100.0) < 0.001

    for t, ps in enumerate(series):
        age = params['age'] + t
        h_t = params['house_price'] * ((1 + params['house_infl']) ** t)
        v_t = ps['portfolio_value']
        outlay = h_t * (1 + params['tx_cost'])

        if ps['shortfall_amt'] > 0: over_details.append((age, ps['shortfall_amt']))
        if ps['excess_amt'] > 0 and not perfect_allocation: under_details.append((age, ps['excess_amt']))

        max_loan_t, emi_aff_net = 0.0, 0.0
        if params['loan_enabled']:
            emi_aff = (ps['take_home_monthly'] * params['emi_frac']
                       if params['emi_mode'] == 'fraction'
                       else params['emi_fixed'])
            emi_aff_net = emi_aff * (1 - params['emi_buf'])
            max_loan_t = min(
                max_loan_from_emi(emi_aff_net, params['loan_rate'], params['loan_tenure']),
                ps['gross_monthly'] * params['bank_mult']
            )
            if params['user_max_loan'] > 0:
                max_loan_t = min(max_loan_t,
                                 params['user_max_loan'] * ((1 + params['house_infl']) ** t))

        actual_loan = min(max_loan_t, outlay) if params['loan_enabled'] else 0.0
        down_payment = max(0.0, outlay - actual_loan)
        cash_rem = v_t - down_payment

        cond_finance = (v_t + max_loan_t) >= outlay
        cond_liquidity = cash_rem >= ps['req_liquid']
        actual_emi = (emi_monthly(actual_loan, params['loan_rate'], params['loan_tenure'])
                      if params['loan_enabled'] and actual_loan > 0 else 0.0)
        cond_emi = actual_emi <= emi_aff_net if params['loan_enabled'] else True

        affordable = cond_finance and cond_liquidity and cond_emi

        res.append({
            'Age': age, 'TakeHome/mo': ps['take_home_monthly'], 'Surplus/yr': ps['surplus_yr'],
            'Portfolio': v_t, 'HousePrice': h_t, 'MaxLoan': max_loan_t,
            'CashLeft': cash_rem, 'EffEMI': actual_emi, 'AffEMI': emi_aff_net,
            'Tax%': ps['tax_info']['effective_rate'] * 100,
            'Eff_Return%': ps['eff_return_rate'] * 100,
            'Affordable': "YES ✓" if affordable else "No",
            'Portfolio_Breakdown': ps['Portfolio_Breakdown']
        })

    return res, over_details, under_details


# =============================================================================
# HELPER: Section header
# =============================================================================
def section_header(icon, title):
    st.markdown(f"""
    <div class="section-header">
        <div class="icon">{icon}</div>
        <h3>{title}</h3>
    </div>""", unsafe_allow_html=True)


def tip(text):
    st.markdown(f'<div class="tip-box">{text}</div>', unsafe_allow_html=True)


# =============================================================================
# 3. HERO BANNER
# =============================================================================
st.markdown("""
<div class="hero">
    <div class="hero-title">🏠 House Affordability Simulator</div>
    <div class="hero-sub">
        Model your path to homeownership — factor in income growth, taxes, investments, and loan eligibility across time.
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SCENARIO BAR (load/save — always visible at top)
# =============================================================================
with st.expander("💾  Load / Save Scenario", expanded=False):
    col_load, col_save = st.columns(2)
    with col_load:
        st.markdown("**Load Scenario**")
        st.file_uploader(
            "Upload a saved .json file", type="json",
            key="scenario_uploader", on_change=handle_scenario_upload,
            label_visibility="collapsed"
        )
    with col_save:
        st.markdown("**Export Current Scenario**")
        export_data = {
            "params": {k: st.session_state[k] for k in default_params.keys()},
            "assets": st.session_state['assets_table'].to_dict(orient='records'),
            "reinvest_rules": st.session_state['reinvest_table'].to_dict(orient='records'),
            "rebalance_events": st.session_state['rebalance_table'].to_dict(orient='records')
        }
        st.download_button(
            label="📤 Download Setup as JSON",
            data=json.dumps(export_data, indent=2),
            file_name="house_scenario.json",
            mime="application/json",
            use_container_width=True
        )

# =============================================================================
# TABS
# =============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "👤  Personal & Housing",
    "💰  Income & Expenses",
    "📈  Assets & Loan",
    "📊  Results"
])

# ─────────────────────────────────────────────
# TAB 1 — Personal & Housing
# ─────────────────────────────────────────────
with tab1:
    tip("Set your <strong>current age</strong>, simulation horizon, and the <strong>target property details</strong>. All future projections start from these values.")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        section_header("🧑", "Your Details")
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("Current Age", min_value=18, max_value=80, key="age",
                            help="Your age today.")
        with c2:
            st.number_input("Simulate up to Age", min_value=19, key="max_age",
                            help="Upper age limit for the simulation.")

    with col2:
        section_header("🏡", "Target Property")
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("House Price Today (₹)", step=500_000,
                            key="house_price", help="Current market value of target property.")
            st.number_input("Annual Price Inflation (%)", key="house_infl",
                            help="Expected yearly rise in property prices.")
        with c2:
            st.number_input("Transaction Costs (%)", key="tx_cost",
                            help="Stamp duty, registration, brokerage — as % of price.")
            st.number_input("Required Cash Buffer (₹)", step=100_000,
                            key="cash_buf", help="Emergency fund to retain after purchase.")
            st.number_input("Buffer Inflation (%)", key="buf_infl",
                            help="Annual growth of your required cash buffer.")

# ─────────────────────────────────────────────
# TAB 2 — Income & Expenses
# ─────────────────────────────────────────────
with tab2:
    tip("Enter your <strong>income, tax details, and monthly expenditure</strong>. The simulator projects these forward year-by-year to estimate investable surplus.")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        section_header("💵", "Income & Taxes")
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("Monthly Gross Income (₹)", step=10_000, key="income_0")
            st.number_input("Monthly Net Take-Home (₹)", step=10_000, key="net_0",
                            help="Leave 0 to let the simulator compute from gross.")
        with c2:
            st.number_input("Income Growth Rate (%)", key="inc_growth",
                            help="Expected annual salary increment.")
            st.selectbox("Tax Regime", options=["new", "old"],
                         format_func=lambda x: "New Regime" if x == "new" else "Old Regime",
                         key="tax_regime")

        with st.expander("⚙️  Advanced Tax Settings"):
            c1, c2 = st.columns(2)
            with c1:
                st.number_input("Basic Salary (₹/mo)", key="basic_m")
                st.number_input("HRA Received (₹/mo)", key="hra_m")
                st.checkbox("Metro City?", key="metro")
                st.number_input("Annual Bonus (₹)", key="bonus_0")
                st.number_input("Bonus Growth (%)", key="bonus_gr")
            with c2:
                st.number_input("Bonus Savings (%)", key="bonus_sav_pct")
                st.number_input("Other 80C (₹/yr)", key="other_80c")
                st.number_input("Employer NPS (₹/yr)", key="nps_ann")
                st.number_input("NPS % of Basic", key="nps_pct")
                st.number_input("Slab Inflation (%)", key="slab_infl",
                                help="Annual increase in tax slab limits. Usually 0.")

    with col2:
        section_header("🛒", "Expenses & Rent")
        st.radio("Expense Mode", ["fraction", "absolute"],
                 format_func=lambda x: "% of Take-Home" if x == "fraction" else "Fixed ₹ Amount",
                 key="exp_mode", horizontal=True)
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("Expenses (% of Take-Home)", key="exp_frac")
            st.number_input("Fixed Expenses (₹/mo)", key="exp_abs")
        with c2:
            st.number_input("Expense Inflation (%)", key="exp_infl")
            st.number_input("Current Rent (₹/mo)", key="rent_0")
            st.number_input("Rent Inflation (%)", key="rent_infl")

# ─────────────────────────────────────────────
# TAB 3 — Assets & Loan
# ─────────────────────────────────────────────
with tab3:
    tip("Define your <strong>investment accounts</strong> and their growth assumptions. Add reinvestment routing and rebalancing events if needed, then configure home loan constraints.")

    # ── 1. Assets Table ──
    section_header("📂", "Investment Accounts / Assets")
    edited_assets_df = st.data_editor(
        st.session_state['assets_table'],
        num_rows="dynamic",
        use_container_width=True,
        key="assets_ui",
        column_config={
            "Stepup_type": st.column_config.SelectboxColumn(
                "Stepup Type", options=["Percentage", "Fixed"], required=True),
            "Invest_above_Surplus_Cash": st.column_config.CheckboxColumn(
                "External Funding?",
                help="Check if this asset is funded from outside your salary surplus (e.g. employer contributions)."),
            "Tax_Treatment": st.column_config.SelectboxColumn(
                "Tax Treatment",
                options=["Exempt", "Taxed at slab rate", "Taxed at fixed rate"],
                required=True),
            "Fixed_Tax_Pct": st.column_config.NumberColumn(
                "Fixed Tax %", min_value=0.0, max_value=100.0,
                help="Applies only if 'Taxed at fixed rate' is selected.")
        }
    )
    st.session_state['assets_table'] = edited_assets_df

    c1, c2 = st.columns(2)
    tot_open = sum(row.get("Opening_Value", 0.0) for _, row in edited_assets_df.iterrows())
    tot_sip = sum(row.get("monthly_contribution", 0.0) for _, row in edited_assets_df.iterrows())
    c1.metric("Total Opening Balance", f"₹ {tot_open:,.0f}")
    c2.metric("Total Monthly SIPs", f"₹ {tot_sip:,.0f}")

    asset_names_list = edited_assets_df["Asset_Class"].dropna().unique().tolist()

    st.divider()

    # ── 2. Reinvestment Rules ──
    section_header("🔄", "Return Reallocation Rules")
    st.caption("By default returns compound in-place. Use this to redirect returns across assets. All rules for one source must sum to 100%.")
    edited_reinvest_df = st.data_editor(
        st.session_state['reinvest_table'],
        num_rows="dynamic",
        use_container_width=True,
        key="reinvest_ui",
        column_config={
            "Source_Asset": st.column_config.SelectboxColumn(options=asset_names_list, required=True),
            "Destination_Asset": st.column_config.SelectboxColumn(options=asset_names_list, required=True),
            "Allocation_Pct": st.column_config.NumberColumn(
                "Allocation %", min_value=0.0, max_value=100.0, required=True)
        }
    )
    st.session_state['reinvest_table'] = edited_reinvest_df

    st.divider()

    # ── 3. Rebalancing Events ──
    section_header("⚖️", "Scheduled Rebalancing Events")
    st.caption("One-time capital transfers between assets at the end of a specific year.")
    edited_rebalance_df = st.data_editor(
        st.session_state['rebalance_table'],
        num_rows="dynamic",
        use_container_width=True,
        key="rebalance_ui",
        column_config={
            "Year": st.column_config.NumberColumn(
                "At End of Age",
                min_value=st.session_state.age,
                max_value=st.session_state.max_age,
                required=True),
            "Source_Asset": st.column_config.SelectboxColumn(options=asset_names_list, required=True),
            "Destination_Asset": st.column_config.SelectboxColumn(options=asset_names_list, required=True),
            "Transfer_Type": st.column_config.SelectboxColumn(
                "Type", options=["Percentage", "Absolute ₹"], required=True),
            "Value": st.column_config.NumberColumn("Amount / %", min_value=0.0, required=True)
        }
    )
    st.session_state['rebalance_table'] = edited_rebalance_df

    st.divider()

    # ── 4. Loan ──
    section_header("🏦", "Home Loan Constraints")
    st.checkbox("Enable Home Loan Financing", key="loan_enabled")

    if st.session_state.loan_enabled:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.number_input("Interest Rate (%)", key="loan_rate")
        with c2:
            st.number_input("Tenure (Years)", key="loan_tenure")
        with c3:
            st.number_input("Bank Eligibility Multiplier", key="bank_mult",
                            help="Max loan = this × monthly gross salary.")

        st.radio("EMI Limit Mode", ["fraction", "fixed"],
                 format_func=lambda x: "% of Take-Home" if x == "fraction" else "Fixed ₹ Amount",
                 key="emi_mode", horizontal=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.number_input("Max EMI (% of Take-Home)", key="emi_frac")
        with c2:
            st.number_input("Fixed EMI Limit (₹/mo)", key="emi_fixed")
        with c3:
            st.number_input("EMI Safety Buffer (%)", key="emi_buf")

        st.number_input("Max Loan I Want (₹)  — enter 0 for no cap", key="user_max_loan")

# ─────────────────────────────────────────────
# TAB 4 — Results
# ─────────────────────────────────────────────
with tab4:
    tip("Click <strong>▶ Run Simulation</strong> to project your finances year by year and find the earliest age you can afford your target home.")

    # Validation
    validation_passed = True
    if not edited_reinvest_df.empty:
        grouped = edited_reinvest_df.groupby("Source_Asset")["Allocation_Pct"].sum()
        for src, total in grouped.items():
            if abs(total - 100.0) > 0.001:
                st.error(f"🛑 Reallocation rules for **'{src}'** sum to **{total:.1f}%** — must equal 100%. Fix in the Assets & Loan tab.")
                validation_passed = False

    if not validation_passed:
        st.stop()

    # Build params
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
            "fixed_tax_pct": (float(row.get("Fixed_Tax_Pct") or 0.0)) / 100.0
        })

    reinvest_rules = edited_reinvest_df.to_dict(orient='records')
    rebalance_events = edited_rebalance_df.to_dict(orient='records')

    params = {
        'age': st.session_state.age,
        'max_years': st.session_state.max_age - st.session_state.age,
        'house_price': st.session_state.house_price,
        'house_infl': st.session_state.house_infl / 100.0,
        'tx_cost': st.session_state.tx_cost / 100.0,
        'cash_buf': st.session_state.cash_buf,
        'buf_infl': st.session_state.buf_infl / 100.0,
        'income_0': st.session_state.income_0,
        'net_0': st.session_state.net_0,
        'inc_growth': st.session_state.inc_growth / 100.0,
        'tax_regime': st.session_state.tax_regime,
        'basic_m': st.session_state.basic_m,
        'hra_m': st.session_state.hra_m,
        'metro': st.session_state.metro,
        'bonus_0': st.session_state.bonus_0,
        'bonus_mode': st.session_state.bonus_mode,
        'bonus_gross': st.session_state.bonus_gross,
        'bonus_gr': st.session_state.bonus_gr / 100.0,
        'bonus_sav_pct': st.session_state.bonus_sav_pct,
        'other_80c': st.session_state.other_80c,
        'nps_ann': st.session_state.nps_ann,
        'nps_pct': st.session_state.nps_pct,
        'slab_infl': st.session_state.slab_infl / 100.0,
        'exp_mode': st.session_state.exp_mode,
        'exp_frac': st.session_state.exp_frac / 100.0,
        'exp_abs': st.session_state.exp_abs,
        'exp_infl': st.session_state.exp_infl / 100.0,
        'rent_0': st.session_state.rent_0,
        'rent_infl': st.session_state.rent_infl / 100.0,
        'loan_enabled': st.session_state.loan_enabled,
        'loan_rate': st.session_state.loan_rate / 100.0,
        'loan_tenure': st.session_state.loan_tenure,
        'bank_mult': st.session_state.bank_mult,
        'emi_mode': st.session_state.emi_mode,
        'emi_frac': st.session_state.emi_frac / 100.0,
        'emi_fixed': st.session_state.emi_fixed,
        'emi_buf': st.session_state.emi_buf / 100.0,
        'user_max_loan': st.session_state.user_max_loan
    }

    col_btn, col_spacer = st.columns([1, 3])
    with col_btn:
        run_clicked = st.button("▶  Run Simulation", type="primary", use_container_width=True)

    if run_clicked:
        with st.spinner("Running simulation…"):
            results, over_details, under_details = run_affordability(
                params, asset_classes, reinvest_rules, rebalance_events)
        st.session_state['sim_results'] = (results, over_details, under_details)

    # ── Display results ──
    if st.session_state['sim_results'] is not None:
        results, over_details, under_details = st.session_state['sim_results']
        df_res = pd.DataFrame(results)
        affordable_rows = df_res[df_res['Affordable'] == "YES ✓"]

        # ── Result Banner ──
        if not affordable_rows.empty:
            first = affordable_rows.iloc[0]
            st.markdown(f"""
            <div class="result-banner success">
                <div class="emoji">🎉</div>
                <div>
                    <div class="title">Earliest Affordable Age: {int(first['Age'])}</div>
                    <div class="sub">
                        Portfolio: ₹{first['Portfolio']:,.0f} &nbsp;·&nbsp;
                        House Price: ₹{first['HousePrice']:,.0f} &nbsp;·&nbsp;
                        Max Loan: ₹{first['MaxLoan']:,.0f} &nbsp;·&nbsp;
                        EMI: ₹{first['EffEMI']:,.0f}/mo
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-banner failure">
                <div class="emoji">❌</div>
                <div>
                    <div class="title">Not affordable by age {st.session_state.max_age}</div>
                    <div class="sub">Consider increasing income growth, reducing expenses, or adjusting loan parameters.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Summary KPI Row ──
        last = df_res.iloc[-1]
        years_span = st.session_state.max_age - st.session_state.age
        final_house = last['HousePrice']
        final_portfolio = last['Portfolio']
        final_surplus = last['Surplus/yr']

        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card blue">
                <div class="label">Final Portfolio (Age {st.session_state.max_age})</div>
                <div class="value">₹{final_portfolio/1e7:.2f} Cr</div>
                <div class="delta">across {years_span} years</div>
            </div>
            <div class="metric-card">
                <div class="label">House Price (Age {st.session_state.max_age})</div>
                <div class="value">₹{final_house/1e7:.2f} Cr</div>
                <div class="delta">at {st.session_state.house_infl}% inflation</div>
            </div>
            <div class="metric-card">
                <div class="label">Annual Surplus (Age {st.session_state.max_age})</div>
                <div class="value">₹{final_surplus/1e5:.1f} L</div>
                <div class="delta">per year at final age</div>
            </div>
            <div class="metric-card">
                <div class="label">Affordable Windows</div>
                <div class="value">{len(affordable_rows)}</div>
                <div class="delta">years out of {years_span + 1}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Chart: Portfolio vs House Price ──
        section_header("📈", "Portfolio vs House Price Over Time")
        chart_df = df_res[['Age', 'Portfolio', 'HousePrice']].copy()
        chart_df = chart_df.rename(columns={'Portfolio': 'Portfolio Value', 'HousePrice': 'House Price (incl. costs)'})
        chart_df = chart_df.set_index('Age')
        st.line_chart(chart_df, use_container_width=True, height=280)

        # ── Warnings ──
        if over_details:
            msg = "**⚠️ Budget Deficit:** Your planned SIPs exceed available surplus in these years — "
            msg += ", ".join([f"Age {a} (₹{v:,.0f})" for a, v in over_details[:5]])
            if len(over_details) > 5: msg += f" + {len(over_details) - 5} more"
            st.error(msg)

        if under_details:
            msg = "**ℹ️ Unallocated Surplus:** You have uninvested surplus in these years — "
            msg += ", ".join([f"Age {a} (₹{v:,.0f})" for a, v in under_details[:5]])
            if len(under_details) > 5: msg += f" + {len(under_details) - 5} more"
            st.warning(msg)

        # ── Download ──
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df_res.to_excel(writer, sheet_name='Simulation Results', index=False)

        section_header("📋", "Year-by-Year Breakdown")
        col_dl, _ = st.columns([1, 3])
        with col_dl:
            st.download_button(
                label="📥 Download Excel",
                data=excel_buffer.getvalue(),
                file_name="house_affordability_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # ── Styled Table ──
        def color_affordable(val):
            if val == "YES ✓":
                return 'background-color: rgba(34,197,94,0.15); color: #22c55e; font-weight: 600;'
            return 'color: #8892a4;'

        format_dict = {
            'TakeHome/mo': '₹{:,.0f}', 'Surplus/yr': '₹{:,.0f}',
            'Portfolio': '₹{:,.0f}', 'HousePrice': '₹{:,.0f}',
            'MaxLoan': '₹{:,.0f}', 'CashLeft': '₹{:,.0f}',
            'EffEMI': '₹{:,.0f}', 'AffEMI': '₹{:,.0f}',
            'Tax%': '{:.1f}%', 'Eff_Return%': '{:.1f}%'
        }

        styled = (df_res.style
                  .format(format_dict)
                  .map(color_affordable, subset=['Affordable']))

        st.dataframe(
            styled,
            use_container_width=True,
            height=540,
            column_config={
                "Portfolio_Breakdown": st.column_config.TextColumn(
                    "Portfolio Breakdown",
                    help="Asset balances post-rebalancing for this year.",
                    width="large"
                )
            }
        )
