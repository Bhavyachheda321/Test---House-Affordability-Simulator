import streamlit as st
import pandas as pd
import math
import io
import json

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="House Affordability Simulator",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# CUSTOM CSS
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
.hero{background:linear-gradient(135deg,#1d6fce 0%,#2d4a9e 60%,#1e3a8a 100%);border-radius:16px;padding:2rem 2.5rem;margin-bottom:1rem;position:relative;overflow:hidden;box-shadow:0 8px 24px rgba(29,111,206,.25);}
.hero::before{content:'';position:absolute;top:-50px;right:-50px;width:200px;height:200px;background:radial-gradient(circle,rgba(255,255,255,.12) 0%,transparent 70%);pointer-events:none;}
.hero-title{font-size:2rem;font-weight:800;letter-spacing:-.02em;color:#ffffff;margin:0 0 .4rem;text-shadow:0 1px 3px rgba(0,0,0,.2);}
.hero-sub{font-size:.95rem;color:rgba(255,255,255,.85);margin:0;font-weight:500;max-width:600px;line-height:1.5;}

/* Editorial note */
.editorial{background:#ffffff;border:1.5px solid var(--border);border-left:4px solid var(--accent);border-radius:var(--radius);padding:1.2rem 1.5rem;margin-bottom:1.2rem;box-shadow:var(--shadow-sm);}
.editorial h4{font-size:.8rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--accent);margin:0 0 .5rem;}
.editorial p{font-size:.9rem;color:var(--text-secondary);line-height:1.7;margin:0;}

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

/* Nav buttons row */
.nav-row{display:flex;justify-content:space-between;align-items:center;margin-top:2rem;padding-top:1rem;border-top:1.5px solid var(--border);}

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

/* Rebalance help table */
.rb-help{background:var(--surface2);border:1.5px solid var(--border);border-radius:var(--radius-sm);padding:.8rem 1rem;font-size:.82rem;color:var(--text-secondary);margin-bottom:.8rem;line-height:1.7;}
.rb-help b{color:var(--text);font-weight:700;}

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
# SESSION STATE
# =============================================================================
default_params = {
    'age': 30, 'max_age': 60, 'house_price': 5000000, 'house_infl': 5.0,
    'target_sqft': 0,
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

if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = 0

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

# New flexible rebalance table columns:
# Trigger_Type | Source_Asset | Destination_Asset | Transfer_Type | Value
# | Start_Age | End_Age | Frequency_Years | Threshold_Asset | Threshold_Amount
if 'rebalance_table' not in st.session_state:
    st.session_state['rebalance_table'] = pd.DataFrame(columns=[
        "Trigger_Type", "Source_Asset", "Destination_Asset",
        "Transfer_Type", "Value",
        "Start_Age", "End_Age", "Frequency_Years",
        "Threshold_Asset", "Threshold_Amount"
    ])

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


def go_to_tab(n):
    st.session_state['active_tab'] = n


# =============================================================================
# FINANCIAL MATH & TAX MODULE
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
# FLEXIBLE REBALANCE ENGINE
# =============================================================================
def build_rebalance_schedule(rebalance_events, name_to_idx, start_age, max_years):
    """
    Converts the flexible rebalance rules table into a dict:
      { simulation_year_t: [(src_idx, dest_idx, transfer_type, value), ...] }

    Supported Trigger_Types:
      'One-Time'          — fires once at Start_Age
      'Annual'            — fires every year from Start_Age to End_Age
      'Every N Years'     — fires every Frequency_Years years starting at Start_Age (up to End_Age)
      'Balance Threshold' — fires in any year where Threshold_Asset balance >= Threshold_Amount
                            (checked after returns, before contributions)
    """
    schedule = {}

    def add(t, src_i, dest_i, t_type, val):
        if t not in schedule:
            schedule[t] = []
        schedule[t].append((src_i, dest_i, t_type, val))

    for _, row in rebalance_events.iterrows():
        trigger   = str(row.get("Trigger_Type", "")).strip()
        src       = str(row.get("Source_Asset", "")).strip()
        dest      = str(row.get("Destination_Asset", "")).strip()
        t_type    = str(row.get("Transfer_Type", "Percentage")).strip()
        val       = float(row.get("Value", 0) or 0)
        start_age = int(row.get("Start_Age", 0) or 0)
        end_age   = int(row.get("End_Age", 0) or 0)
        freq      = int(row.get("Frequency_Years", 1) or 1)
        thr_asset = str(row.get("Threshold_Asset", "")).strip()
        thr_amt   = float(row.get("Threshold_Amount", 0) or 0)

        if src not in name_to_idx or dest not in name_to_idx:
            continue
        src_i, dest_i = name_to_idx[src], name_to_idx[dest]

        if trigger == "One-Time":
            t = start_age - start_age  # relative year = start_age - simulation start_age
            t = start_age - (start_age - (start_age - start_age))
            # properly: simulation year = rule_age - sim_start_age
            sim_t = start_age - start_age  # placeholder; compute below
            sim_t = start_age - st.session_state.age
            if 0 <= sim_t <= max_years:
                add(sim_t, src_i, dest_i, t_type, val)

        elif trigger == "Annual":
            s = max(0, start_age - st.session_state.age)
            e = min(max_years, (end_age - st.session_state.age) if end_age > 0 else max_years)
            for sim_t in range(s, e + 1):
                add(sim_t, src_i, dest_i, t_type, val)

        elif trigger == "Every N Years":
            s = max(0, start_age - st.session_state.age)
            e = min(max_years, (end_age - st.session_state.age) if end_age > 0 else max_years)
            f = max(1, freq)
            sim_t = s
            while sim_t <= e:
                add(sim_t, src_i, dest_i, t_type, val)
                sim_t += f

        elif trigger == "Balance Threshold":
            # Store as a special sentinel; resolved at simulation time
            thr_idx = name_to_idx.get(thr_asset, -1)
            if thr_idx == -1:
                continue
            s = max(0, start_age - st.session_state.age) if start_age > 0 else 0
            e = min(max_years, (end_age - st.session_state.age) if end_age > 0 else max_years)
            for sim_t in range(s, e + 1):
                # encode threshold rule as tuple with sentinel flag
                if sim_t not in schedule:
                    schedule[sim_t] = []
                schedule[sim_t].append(('__threshold__', src_i, dest_i, t_type, val, thr_idx, thr_amt))

    return schedule


# =============================================================================
# PORTFOLIO SIMULATION
# =============================================================================
TIMING_FACTORS = {
    'start':   lambda r: (1 + r),
    'mid':     lambda r: (1 + r) ** 0.5,
    'end':     lambda r: 1.0,
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

    rebalance_schedule = build_rebalance_schedule(
        rebalance_events, name_to_idx, params['age'], params['max_years'])

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
                basic_monthly=params['basic_m'], hra_received_monthly=params['hra_m'],
                rent_paid_monthly=rent_monthly, metro_city=params['metro'],
                employer_nps_annual=params['nps_ann'], nps_pct_of_basic=params['nps_pct'],
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

        # Apply rebalance schedule for this year
        if t in rebalance_schedule:
            for rule in rebalance_schedule[t]:
                if rule[0] == '__threshold__':
                    _, src_i, dest_i, r_type, r_val, thr_idx, thr_amt = rule
                    if new_bals[thr_idx] >= thr_amt:
                        transfer_amt = (new_bals[src_i] * (r_val / 100.0)
                                        if r_type == 'Percentage'
                                        else min(new_bals[src_i], r_val))
                        new_bals[src_i] = max(0.0, new_bals[src_i] - transfer_amt)
                        new_bals[dest_i] += transfer_amt
                else:
                    src_i, dest_i, r_type, r_val = rule
                    transfer_amt = (new_bals[src_i] * (r_val / 100.0)
                                    if r_type == 'Percentage'
                                    else min(new_bals[src_i], r_val))
                    new_bals[src_i] = max(0.0, new_bals[src_i] - transfer_amt)
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
            'Portfolio_Breakdown': "  |  ".join(breakdown_lines),
            'asset_balances_snapshot': list(new_bals)
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

        sqft = params.get('target_sqft', 0)
        psf = (h_t / sqft) if sqft > 0 else 0.0
        aff_sqft = ((v_t + max_loan_t) / psf) if psf > 0 else 0.0

        res.append({
            'Age': age, 'TakeHome/mo': ps['take_home_monthly'], 'Surplus/yr': ps['surplus_yr'],
            'Portfolio': v_t, 'HousePrice': h_t, 'MaxLoan': max_loan_t,
            'CashLeft': cash_rem, 'EffEMI': actual_emi, 'AffEMI': emi_aff_net,
            'Tax%': ps['tax_info']['effective_rate'] * 100,
            'Eff_Return%': ps['eff_return_rate'] * 100,
            'Affordable': "YES ✓" if affordable else "No",
            'Aff_Sqft': aff_sqft,
            'Portfolio_Breakdown': ps['Portfolio_Breakdown']
        })

    return res, over_details, under_details


# =============================================================================
# HELPERS
# =============================================================================
def section_header(icon, title):
    st.markdown(f"""
    <div class="section-header">
        <div class="icon">{icon}</div>
        <h3>{title}</h3>
    </div>""", unsafe_allow_html=True)


def tip(text):
    st.markdown(f'<div class="tip-box">{text}</div>', unsafe_allow_html=True)


def nav_buttons(current_tab, total_tabs=4):
    st.markdown('<div class="nav-row">', unsafe_allow_html=True)
    c_prev, c_mid, c_next = st.columns([1, 4, 1])
    with c_prev:
        if current_tab > 0:
            if st.button("← Previous", key=f"prev_{current_tab}"):
                go_to_tab(current_tab - 1)
                st.rerun()
    with c_next:
        if current_tab < total_tabs - 1:
            label = "Next →" if current_tab < total_tabs - 2 else "Go to Results →"
            if st.button(label, key=f"next_{current_tab}", type="primary"):
                go_to_tab(current_tab + 1)
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# HERO BANNER
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
# EDITORIAL NOTE — always visible
# =============================================================================
st.markdown("""
<div class="editorial">
    <h4>📌 What problem does this solve?</h4>
    <p>
        Buying a home is the single largest financial decision most Indian families make — yet most people plan for it
        with nothing more than a rough gut feel. They don't know <em>when</em> they can realistically afford it,
        <em>how much</em> they need to save, or whether their investments are growing fast enough to keep pace with
        rising property prices and inflation.
    </p>
    <p style="margin-top:.6rem;">
        This simulator brings together every variable that matters — your current income, expected salary growth,
        tax deductions, monthly expenses, rent, investment portfolio returns, and home loan eligibility — and projects
        them year by year into the future. The result is a clear, data-driven answer: the <strong>earliest age at which
        you can afford your target home</strong>, along with a full breakdown of your finances at every point along the way.
        No guesswork. No oversimplification.
    </p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# HOW TO USE — video placeholder + quick guide
# =============================================================================
with st.expander("🎬  How to Use This App — Watch the Walkthrough Video", expanded=False):
    st.markdown("""
    **Replace the URL below with your Loom video link once you've recorded it.**
    Loom provides a direct `.mp4` link or an embed URL — either works with `st.video()`.
    """)
    LOOM_VIDEO_URL = "https://www.loom.com/share/YOUR_LOOM_VIDEO_ID_HERE"
    st.info(
        f"📹 **Video placeholder** — paste your Loom share URL here: `{LOOM_VIDEO_URL}`\n\n"
        "Once you have your Loom link, replace `LOOM_VIDEO_URL` in the source code with the direct `.mp4` URL "
        "(click *Share → Copy video URL* in Loom). Then change `st.info(...)` to `st.video(LOOM_VIDEO_URL)`.",
        icon="ℹ️"
    )

    st.markdown("---")
    st.markdown("""
    **Quick guide — 4 tabs, 5 minutes:**

    | Tab | What you fill in | Why it matters |
    |-----|-----------------|----------------|
    | 👤 Personal & Housing | Your age, target home price, size | Sets the goal — everything is measured against this |
    | 💰 Income & Expenses | Salary, tax regime, rent, bonus, monthly spend | Determines how much you can save each month |
    | 📈 Assets & Loan | Existing investments, SIPs, rebalancing rules, loan limits | Tells the simulator how your wealth grows and what loan you qualify for |
    | 📊 Results | Click Run — read the output | Shows the year-by-year forecast and the earliest affordable age |

    **Tip:** Fill tabs in order and use the **Next →** button at the bottom of each tab.
    You can save your inputs at any time using **Load / Save Scenario** above.
    """)

# =============================================================================
# LOAD / SAVE
# =============================================================================
with st.expander("💾  Load / Save Scenario", expanded=False):
    col_load, col_save = st.columns(2)
    with col_load:
        st.markdown("**Load a previously saved scenario**")
        st.caption("Upload a .json file you exported earlier to restore all your inputs instantly.")
        st.file_uploader(
            "Upload .json", type="json",
            key="scenario_uploader", on_change=handle_scenario_upload,
            label_visibility="collapsed"
        )
    with col_save:
        st.markdown("**Export current inputs**")
        st.caption("Downloads all your current settings as a .json file you can reload later.")
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
tab_labels = [
    "👤  Personal & Housing",
    "💰  Income & Expenses",
    "📈  Assets & Loan",
    "📊  Results"
]
tab1, tab2, tab3, tab4 = st.tabs(tab_labels)

# ─────────────────────────────────────────────
# TAB 1 — Personal & Housing
# ─────────────────────────────────────────────
with tab1:
    tip("Start here. Tell the simulator <strong>who you are</strong> and <strong>what home you want to buy</strong>. "
        "Every projection in the Results tab is calculated relative to these numbers.")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        section_header("🧑", "Your Details")
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("Current Age", min_value=18, max_value=80, key="age",
                help="👤 How old are you today?\n\nEnter your current age in years. "
                     "The simulation starts from this age.\n\nExample: If you are 32, enter 32.")
        with c2:
            st.number_input("Simulate up to Age", min_value=19, key="max_age",
                help="📅 How far into the future should we simulate?\n\n"
                     "The simulator will calculate year by year from your current age up to this age. "
                     "A longer horizon gives you more time to become affordable.\n\n"
                     "Example: Enter 60 to see your finances all the way to age 60.")

    with col2:
        section_header("🏡", "Target Property")
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("House Price Today (₹)", step=500_000, key="house_price",
                help="🏠 What does your dream home cost RIGHT NOW?\n\n"
                     "Enter the current market value of the property you want to buy. "
                     "The simulator will inflate this price each year automatically.\n\n"
                     "Example: A 2BHK in Powai costs ₹1.5 Cr today → enter 15000000.")
            st.number_input("Annual Price Inflation (%)", key="house_infl",
                help="📈 How fast do you expect property prices to rise each year?\n\n"
                     "Indian real estate has historically appreciated 5–8% per year in metro cities. "
                     "A higher number makes it harder to afford the home over time.\n\n"
                     "Example: Enter 6.0 for 6% annual price rise.")
        with c2:
            st.number_input("Transaction Costs (%)", key="tx_cost",
                help="📋 What extra costs come on top of the property price?\n\n"
                     "This covers stamp duty (4–6%), registration fees (~1%), and brokerage (~1–2%). "
                     "In Mumbai the total is typically 6–8% of the property value.\n\n"
                     "Example: Enter 7.0 for 7% on top of the property price.")
            st.number_input("Required Cash Buffer (₹)", step=100_000, key="cash_buf",
                help="🛡️ How much emergency cash do you want to keep AFTER buying the house?\n\n"
                     "After paying the down payment, you should not be left with zero savings. "
                     "This is the minimum liquid reserve you want to retain.\n\n"
                     "Example: Enter 10,00,000 (₹10 lakh) to always keep ₹10L untouched.")
            st.number_input("Buffer Inflation (%)", key="buf_infl",
                help="📊 How fast should your emergency reserve grow each year?\n\n"
                     "Your required safety net should grow with inflation — ₹10L today won't feel "
                     "like enough in 10 years. Typically set this equal to general inflation (5–7%).\n\n"
                     "Example: Enter 6.0 to grow the buffer at 6% per year.")

        section_header("📐", "Sq Ft Affordability")
        st.caption("Optional — enter today's market rate per sq ft to see how many sq ft you can afford each year.")
        st.number_input("Market Rate Today (₹/sq ft)", min_value=0, step=500, key="target_sqft",
            help="📐 What is the price per square foot in your target area RIGHT NOW?\n\n"
                 "Leave at 0 to skip this feature. When filled, a new column 'Affordable Sq Ft' appears "
                 "in the Results table showing how many sq ft your total budget (portfolio + loan) can buy "
                 "each year as the market rate inflates.\n\n"
                 "Example: Flats in Andheri East cost ₹18,000/sq ft today → enter 18000.")

    nav_buttons(0)

# ─────────────────────────────────────────────
# TAB 2 — Income & Expenses
# ─────────────────────────────────────────────
with tab2:
    tip("Tell the simulator how much you <strong>earn, spend, and save</strong> each month. "
        "This is used to calculate how much surplus you have available to invest every year.")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        section_header("💵", "Income & Taxes")
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("Monthly Gross Income (₹)", step=10_000, key="income_0",
                help="💰 What is your total monthly salary BEFORE any deductions?\n\n"
                     "This is the CTC/12 or the gross figure on your payslip before PF, tax, etc. "
                     "The simulator uses this to compute your tax each year.\n\n"
                     "Example: If your annual CTC is ₹18L, enter 150000.")
            st.number_input("Monthly Net Take-Home (₹)", step=10_000, key="net_0",
                help="🏦 What amount actually gets credited to your bank account each month?\n\n"
                     "This is your in-hand salary after all deductions. "
                     "If you enter 0 here, the simulator will estimate it from your gross income and tax regime.\n\n"
                     "Example: If ₹1.1L lands in your account every month, enter 110000.")
        with c2:
            st.number_input("Income Growth Rate (%)", key="inc_growth",
                help="📈 By what % do you expect your salary to grow every year?\n\n"
                     "Include both increment and expected promotions. "
                     "10–12% is reasonable for mid-career professionals in India.\n\n"
                     "Example: Enter 10.0 for 10% annual increment.")
            st.selectbox("Tax Regime", options=["new", "old"],
                         format_func=lambda x: "New Regime" if x == "new" else "Old Regime",
                         key="tax_regime",
                help="🏛️ Which income tax regime do you file under?\n\n"
                     "New Regime (2024–25): Lower rates, fewer deductions — usually better for high earners "
                     "or those with few investments.\n"
                     "Old Regime: Higher rates but allows deductions like HRA, 80C, home loan interest.\n\n"
                     "Not sure? Check your Form 16 or ask your CA.")

        with st.expander("⚙️  Advanced Tax Settings"):
            st.caption("Fill these only if you want precise tax calculation. "
                       "They are used to compute HRA exemption and NPS deductions.")
            c1, c2 = st.columns(2)
            with c1:
                st.number_input("Basic Salary (₹/mo)", key="basic_m",
                    help="📋 What is the 'Basic' component of your monthly salary?\n\n"
                         "This is shown separately on your payslip. It's typically 40–50% of gross. "
                         "Used to calculate HRA exemption and NPS deduction limits.\n\n"
                         "Example: If gross is ₹1.5L and basic is 40%, enter 60000.")
                st.number_input("HRA Received (₹/mo)", key="hra_m",
                    help="🏠 How much House Rent Allowance does your employer give you each month?\n\n"
                         "Shown on your payslip as 'HRA'. Only relevant for Old Regime filers. "
                         "If you own a house or are in New Regime, this doesn't matter much.\n\n"
                         "Example: Enter 20000 if your payslip shows HRA of ₹20,000/mo.")
                st.checkbox("Metro City?", key="metro",
                    help="🌆 Do you currently live in a Metro city?\n\n"
                         "Metro cities (Mumbai, Delhi, Kolkata, Chennai) get a higher HRA exemption — "
                         "50% of basic vs 40% for non-metro. Tick this if you live in a metro.\n\n"
                         "Example: Check this box if you live in Mumbai or Bengaluru.")
                st.number_input("Other 80C (₹/yr)", key="other_80c",
                    help="💼 How much do you invest in 80C instruments per year (excluding EPF)?\n\n"
                         "This includes ELSS mutual funds, PPF, LIC premiums, NSC, etc. "
                         "Maximum limit is ₹1.5L/year. Only applies to Old Regime.\n\n"
                         "Example: If you invest ₹50K in ELSS and ₹50K in PPF, enter 100000.")
                st.number_input("Employer NPS (₹/yr)", key="nps_ann",
                    help="🏦 Does your employer contribute to NPS on your behalf?\n\n"
                         "Some companies contribute 10% of basic to National Pension System. "
                         "This amount is deductible under Section 80CCD(2) in both regimes.\n\n"
                         "Example: If employer contributes ₹72K/year to your NPS, enter 72000.")
            with c2:
                st.number_input("NPS % of Basic", key="nps_pct",
                    help="% How much does your employer contribute to NPS as a % of basic salary?\n\n"
                         "Usually 10%. Only fill this if you don't know the absolute annual amount above.\n\n"
                         "Example: Enter 10.0 if employer contributes 10% of basic to NPS.")
                st.number_input("Slab Inflation (%)", key="slab_infl",
                    help="📊 Do you expect tax slabs to be revised upward each year?\n\n"
                         "Governments sometimes widen tax slabs in budgets. Set to 0 for conservative "
                         "estimates. A positive value reduces your tax burden over time.\n\n"
                         "Example: Enter 0.0 to keep slabs fixed (recommended).")

        # ── Bonus Section ──
        section_header("🎁", "Bonus & Variable Pay")
        st.caption("Enter details of any annual bonus or variable pay you receive. "
                   "The simulator adds this to your yearly savings after applying the savings percentage.")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.number_input("Annual Bonus Net of Tax (₹)", key="bonus_0",
                help="🎁 How much bonus do you receive per year, AFTER paying tax on it?\n\n"
                     "Enter the amount that actually comes to you after your employer deducts TDS. "
                     "If you receive a gross bonus and it gets taxed, enter the net amount.\n\n"
                     "Example: You get a ₹2L bonus but ₹60K is deducted as tax → enter 140000.")
            st.radio("Bonus Mode", ["fixed", "percent_of_gross"],
                     format_func=lambda x: "Fixed ₹ Amount" if x == "fixed" else "% of Annual Gross",
                     key="bonus_mode", horizontal=True,
                help="How is your bonus defined?\n"
                     "Fixed: You always get a specific rupee amount (e.g. ₹1.5L/year).\n"
                     "% of Gross: Your bonus is a percentage of your annual salary (e.g. 10% of CTC).")
        with c2:
            st.number_input("Bonus Growth Rate (%/yr)", key="bonus_gr",
                help="📈 By how much do you expect your bonus to grow each year?\n\n"
                     "Your bonus typically grows with your salary. Set this similar to income growth.\n\n"
                     "Example: Enter 8.0 if you expect your bonus to increase ~8% every year.")
            st.checkbox("Bonus is Gross (deduct tax)", key="bonus_gross",
                help="☑️ Is the bonus amount you entered BEFORE or AFTER tax?\n\n"
                     "If unchecked: The amount you entered is already post-tax (net in hand).\n"
                     "If checked: The simulator will deduct income tax at your effective rate.\n\n"
                     "Example: Check this if you entered the gross bonus figure from your offer letter.")
        with c3:
            st.number_input("Bonus Savings (%)", key="bonus_sav_pct",
                help="💾 What percentage of your bonus do you actually save/invest?\n\n"
                     "Be honest — many people spend part of their bonus. "
                     "Only the saved portion is counted as investable surplus.\n\n"
                     "Example: Enter 80.0 if you save 80% of your bonus and spend the rest.")

    with col2:
        section_header("🛒", "Expenses & Rent")
        st.radio("Expense Mode", ["fraction", "absolute"],
                 format_func=lambda x: "% of Take-Home" if x == "fraction" else "Fixed ₹ Amount",
                 key="exp_mode", horizontal=True,
                 help="How do you want to define your monthly living expenses?\n\n"
                      "% of Take-Home: Simpler — your expenses stay as a fixed % of your salary "
                      "(so they grow as salary grows).\n"
                      "Fixed ₹ Amount: You specify an absolute figure that grows with inflation.")
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("Expenses (% of Take-Home)", key="exp_frac",
                help="🛒 What % of your monthly take-home do you spend on living expenses?\n\n"
                     "Include food, utilities, transport, subscriptions, dining, clothes etc. "
                     "Do NOT include rent here — rent is entered separately below.\n\n"
                     "Example: If take-home is ₹1L and you spend ₹45K on expenses, enter 45.0.")
            st.number_input("Fixed Expenses (₹/mo)", key="exp_abs",
                help="🛒 What is your fixed monthly living cost in today's Rupees?\n\n"
                     "Used only when 'Fixed ₹ Amount' mode is selected above. "
                     "This amount will be grown by Expense Inflation each year.\n\n"
                     "Example: If you spend ₹45,000/month today on everything except rent, enter 45000.")
        with c2:
            st.number_input("Expense Inflation (%)", key="exp_infl",
                help="📊 How fast do you expect your living costs to rise each year?\n\n"
                     "Only applies in Fixed ₹ mode. General inflation in India runs 5–6% per year. "
                     "Lifestyle upgrades can push this to 7–8%.\n\n"
                     "Example: Enter 6.0 for 6% annual rise in expenses.")
            st.number_input("Current Rent (₹/mo)", key="rent_0",
                help="🏘️ How much rent do you pay RIGHT NOW every month?\n\n"
                     "This is subtracted from your income as a separate expense. "
                     "It is assumed you will stop paying rent once you buy the house.\n\n"
                     "Example: If you pay ₹25,000/month rent, enter 25000.")
            st.number_input("Rent Inflation (%)", key="rent_infl",
                help="📈 How fast do you expect your rent to increase each year?\n\n"
                     "Rents in Indian cities typically rise 8–10% per year. "
                     "Higher rent growth hurts your surplus and delays affordability.\n\n"
                     "Example: Enter 8.0 for 8% annual rent increase.")

    nav_buttons(1)

# ─────────────────────────────────────────────
# TAB 3 — Assets & Loan
# ─────────────────────────────────────────────
with tab3:
    tip("Define your <strong>current investments</strong>, how they grow, and when you want to rebalance them. "
        "Then set your home loan eligibility constraints.")

    # ── 1. Assets Table ──
    section_header("📂", "Investment Accounts / Assets")
    st.caption(
        "List every investment account you have — mutual funds, PPF, FD, stocks, EPF, etc. "
        "Each row is one asset. The simulator grows each asset year by year using the return and stepup you specify."
    )
    with st.expander("❓ How to fill the Assets table — field-by-field guide", expanded=False):
        st.markdown("""
| Column | What to enter | Example |
|--------|--------------|---------|
| **Asset Class** | A name you recognise — anything works | "Equity MF", "PPF", "EPF", "FD" |
| **Opening Value (₹)** | How much is in this account TODAY | ₹5,00,000 |
| **Monthly Contribution (₹)** | Fixed SIP or monthly deposit going forward | ₹20,000 |
| **Annual Return (%)** | Expected average yearly return on this asset | 12% for equity, 7.1% for PPF |
| **Stepup Type** | How your SIP increases each year — Percentage or Fixed ₹ | Percentage |
| **Stepup Value** | By how much the SIP grows each year | 5 → SIP grows 5% each year |
| **Surplus Allocation %** | What share of your leftover monthly surplus goes here | 100 → all surplus goes here |
| **External Funding?** | Tick if this is funded by your employer (e.g. EPF) — not from your surplus | ✅ for EPF |
| **Tax Treatment** | How returns are taxed | Equity MF → "Taxed at fixed rate" @ 12.5% |
| **Fixed Tax %** | The tax rate if you chose "Taxed at fixed rate" above | 12.5 for LTCG on equity |
        """)

    edited_assets_df = st.data_editor(
        st.session_state['assets_table'],
        num_rows="dynamic",
        use_container_width=True,
        key="assets_ui",
        column_config={
            "Stepup_type": st.column_config.SelectboxColumn(
                "Stepup Type", options=["Percentage", "Fixed"], required=True,
                help="Percentage: SIP grows by X% each year. Fixed: SIP increases by a flat ₹X each year."),
            "Invest_above_Surplus_Cash": st.column_config.CheckboxColumn(
                "External Funding?",
                help="Tick this for assets funded externally (e.g. EPF from employer). "
                     "These are NOT deducted from your monthly surplus."),
            "Tax_Treatment": st.column_config.SelectboxColumn(
                "Tax Treatment",
                options=["Exempt", "Taxed at slab rate", "Taxed at fixed rate"],
                required=True,
                help="Exempt: No tax on returns (PPF, EPF). "
                     "Taxed at slab rate: Returns taxed at your income tax rate (FD interest). "
                     "Taxed at fixed rate: Returns taxed at a fixed % (equity LTCG = 12.5%)."),
            "Fixed_Tax_Pct": st.column_config.NumberColumn(
                "Fixed Tax %", min_value=0.0, max_value=100.0,
                help="Leave blank unless Tax Treatment is 'Taxed at fixed rate'. "
                     "For equity mutual funds (LTCG), enter 12.5.")
        }
    )
    st.session_state['assets_table'] = edited_assets_df

    c1, c2 = st.columns(2)
    tot_open = sum(row.get("Opening_Value", 0.0) for _, row in edited_assets_df.iterrows())
    tot_sip  = sum(row.get("monthly_contribution", 0.0) for _, row in edited_assets_df.iterrows())
    c1.metric("Total Opening Balance", f"₹ {tot_open:,.0f}")
    c2.metric("Total Monthly SIPs",    f"₹ {tot_sip:,.0f}")

    asset_names_list = edited_assets_df["Asset_Class"].dropna().unique().tolist()

    st.divider()

    # ── 2. Reinvestment Rules ──
    section_header("🔄", "Return Reallocation Rules")
    st.caption(
        "By default, every asset's returns compound back into itself. "
        "Use this table to redirect returns — e.g. send your FD interest into your equity fund. "
        "If you add rules for a source asset, they must sum to exactly 100%."
    )
    edited_reinvest_df = st.data_editor(
        st.session_state['reinvest_table'],
        num_rows="dynamic",
        use_container_width=True,
        key="reinvest_ui",
        column_config={
            "Source_Asset": st.column_config.SelectboxColumn(
                "Source Asset", options=asset_names_list, required=True,
                help="Which asset's returns do you want to redirect?"),
            "Destination_Asset": st.column_config.SelectboxColumn(
                "Destination Asset", options=asset_names_list, required=True,
                help="Where should those returns go?"),
            "Allocation_Pct": st.column_config.NumberColumn(
                "Allocation %", min_value=0.0, max_value=100.0, required=True,
                help="What % of the source returns go to this destination? Must total 100% per source.")
        }
    )
    st.session_state['reinvest_table'] = edited_reinvest_df

    st.divider()

    # ── 3. Flexible Rebalancing ──
    section_header("⚖️", "Portfolio Rebalancing Rules")

    st.markdown("""
<div class="rb-help">
<b>How rebalancing works:</b> At the end of each simulated year, the engine checks your rebalancing rules
and executes any transfers that are triggered. You can mix and match as many rules as you like.<br><br>
<b>Trigger Types explained:</b><br>
&nbsp;&nbsp;• <b>One-Time</b> — Transfer once at a specific age. Example: at age 45, move 30% of equity to debt.<br>
&nbsp;&nbsp;• <b>Annual</b> — Transfer every year between Start Age and End Age. Example: every year from 50 to 60, move ₹5L from equity to FD.<br>
&nbsp;&nbsp;• <b>Every N Years</b> — Transfer periodically. Example: every 3 years starting at age 40, rebalance 20% back to equity.<br>
&nbsp;&nbsp;• <b>Balance Threshold</b> — Transfer only when a watched asset crosses a certain value.
  Example: whenever your equity fund crosses ₹50L, move the excess 20% into debt.<br><br>
<b>Transfer Type:</b> Percentage = X% of the source asset's current value. Absolute ₹ = a fixed rupee amount.<br>
<b>Threshold Asset</b> and <b>Threshold Amount</b> are only used for Balance Threshold triggers — leave blank for others.
</div>
""", unsafe_allow_html=True)

    edited_rebalance_df = st.data_editor(
        st.session_state['rebalance_table'],
        num_rows="dynamic",
        use_container_width=True,
        key="rebalance_ui",
        column_config={
            "Trigger_Type": st.column_config.SelectboxColumn(
                "Trigger Type",
                options=["One-Time", "Annual", "Every N Years", "Balance Threshold"],
                required=True,
                help="When should this transfer fire?\n"
                     "One-Time: once at Start Age.\n"
                     "Annual: every year from Start Age to End Age.\n"
                     "Every N Years: every N years starting at Start Age.\n"
                     "Balance Threshold: whenever Threshold Asset >= Threshold Amount."
            ),
            "Source_Asset": st.column_config.SelectboxColumn(
                "Source Asset", options=asset_names_list, required=True,
                help="Which asset do you want to transfer FROM?"),
            "Destination_Asset": st.column_config.SelectboxColumn(
                "Destination Asset", options=asset_names_list, required=True,
                help="Which asset should receive the transferred amount?"),
            "Transfer_Type": st.column_config.SelectboxColumn(
                "Transfer Type", options=["Percentage", "Absolute ₹"], required=True,
                help="Percentage: transfer X% of source balance. Absolute ₹: transfer a fixed rupee amount."),
            "Value": st.column_config.NumberColumn(
                "Amount / %", min_value=0.0, required=True,
                help="The percentage or rupee amount to transfer. E.g. 20 for 20%, or 500000 for ₹5L."),
            "Start_Age": st.column_config.NumberColumn(
                "Start Age", min_value=18, max_value=100,
                help="The age at which this rule starts (or fires, for One-Time). Required for all trigger types."),
            "End_Age": st.column_config.NumberColumn(
                "End Age", min_value=18, max_value=100,
                help="For Annual and Every N Years: the last age at which this rule can fire. Leave blank to run until end of simulation."),
            "Frequency_Years": st.column_config.NumberColumn(
                "Every N Yrs", min_value=1, max_value=50,
                help="For 'Every N Years' trigger only: how many years between transfers. E.g. 3 = every 3 years."),
            "Threshold_Asset": st.column_config.SelectboxColumn(
                "Threshold Asset", options=[""] + asset_names_list,
                help="For 'Balance Threshold' only: which asset's balance do you want to watch?"),
            "Threshold_Amount": st.column_config.NumberColumn(
                "Threshold ₹", min_value=0.0,
                help="For 'Balance Threshold' only: the rupee value that triggers the transfer when the watched asset reaches it."),
        }
    )
    st.session_state['rebalance_table'] = edited_rebalance_df

    st.divider()

    # ── 4. Loan ──
    section_header("🏦", "Home Loan Constraints")
    st.caption("Configure how much home loan you can take. The simulator uses this to work out how much "
               "of the house price your bank will finance, and whether the EMI fits your monthly budget.")
    st.checkbox("Enable Home Loan Financing", key="loan_enabled",
                help="✅ Check this if you plan to take a home loan.\n\n"
                     "If unchecked, the simulator assumes you will buy the house entirely from your own savings (full cash purchase).")

    if st.session_state.loan_enabled:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.number_input("Interest Rate (%)", key="loan_rate",
                help="🏦 What interest rate do you expect on your home loan?\n\n"
                     "Current home loan rates in India are 8.5–9.5% p.a. Use your bank's current rate "
                     "or a slightly conservative estimate.\n\nExample: Enter 8.75 for 8.75% per year.")
        with c2:
            st.number_input("Tenure (Years)", key="loan_tenure",
                help="📅 For how many years will you repay the loan?\n\n"
                     "Longer tenure = lower EMI but more total interest paid. "
                     "Most people choose 15–25 years.\n\nExample: Enter 20 for a 20-year loan.")
        with c3:
            st.number_input("Bank Eligibility Multiplier", key="bank_mult",
                help="🏦 Banks typically lend 55–65× your monthly gross salary as a maximum loan.\n\n"
                     "This caps how much your bank will approve regardless of EMI capacity. "
                     "Check with your bank or use 60 as a standard estimate.\n\n"
                     "Example: If gross monthly is ₹1.5L and multiplier is 60, max loan = ₹90L.")

        st.radio("EMI Limit Mode", ["fraction", "fixed"],
                 format_func=lambda x: "% of Take-Home" if x == "fraction" else "Fixed ₹ Amount",
                 key="emi_mode", horizontal=True,
                 help="How do you want to set your maximum comfortable EMI?\n\n"
                      "% of Take-Home: EMI is capped at X% of your monthly salary (grows as salary grows).\n"
                      "Fixed ₹: You name a specific rupee cap regardless of salary.")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.number_input("Max EMI (% of Take-Home)", key="emi_frac",
                help="📊 What % of your monthly take-home are you comfortable paying as EMI?\n\n"
                     "Financial advisors recommend keeping EMI below 40–45% of take-home. "
                     "Higher means more financial stress.\n\nExample: Enter 40.0 for 40%.")
        with c2:
            st.number_input("Fixed EMI Limit (₹/mo)", key="emi_fixed",
                help="💳 What is the maximum monthly EMI you are willing to pay?\n\n"
                     "Used only when 'Fixed ₹ Amount' mode is selected above.\n\n"
                     "Example: Enter 60000 if you don't want to pay more than ₹60K/month.")
        with c3:
            st.number_input("EMI Safety Buffer (%)", key="emi_buf",
                help="🛡️ A conservative haircut on your EMI capacity.\n\n"
                     "Example: If buffer = 10%, and your max EMI is ₹60K, the simulator uses ₹54K "
                     "as the effective limit to leave some breathing room.\n\nEnter 0 for no buffer.")

        st.number_input("Max Loan I Want (₹)  — enter 0 for no cap", key="user_max_loan",
            help="🔒 Do you want to cap the loan regardless of what the bank offers?\n\n"
                 "Example: Even if the bank will give ₹1.5 Cr, enter 10000000 (₹1 Cr) if you don't "
                 "want to borrow more than ₹1 Cr. Enter 0 to let the bank's limit apply.")

    nav_buttons(2)

# ─────────────────────────────────────────────
# TAB 4 — Results
# ─────────────────────────────────────────────
with tab4:
    tip("Click <strong>▶ Run Simulation</strong> to project your finances year by year. "
        "The simulator will tell you the <strong>earliest age you can afford your target home</strong> "
        "and show a full breakdown for every year in between.")

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

    # Build asset_classes
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

    reinvest_rules   = edited_reinvest_df.to_dict(orient='records')
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
        'user_max_loan': st.session_state.user_max_loan,
        'target_sqft': st.session_state.target_sqft
    }

    col_btn, col_spacer = st.columns([1, 3])
    with col_btn:
        run_clicked = st.button("▶  Run Simulation", type="primary", use_container_width=True)

    if run_clicked:
        with st.spinner("Running simulation…"):
            results, over_details, under_details = run_affordability(
                params, asset_classes, reinvest_rules,
                pd.DataFrame(rebalance_events) if rebalance_events else st.session_state['rebalance_table'])
        st.session_state['sim_results'] = (results, over_details, under_details)

    if st.session_state['sim_results'] is not None:
        results, over_details, under_details = st.session_state['sim_results']
        df_res = pd.DataFrame(results)
        affordable_rows = df_res[df_res['Affordable'] == "YES ✓"]

        # ── Result Banner ──
        show_sqft = st.session_state.target_sqft > 0
        if not affordable_rows.empty:
            first = affordable_rows.iloc[0]
            sqft_extra = f" &nbsp;·&nbsp; Aff. Area: {first['Aff_Sqft']:,.0f} sq ft" if show_sqft else ""
            st.markdown(f"""
            <div class="result-banner success">
                <div class="emoji">🎉</div>
                <div>
                    <div class="title">Earliest Affordable Age: {int(first['Age'])}</div>
                    <div class="sub">
                        Portfolio: ₹{first['Portfolio']:,.0f} &nbsp;·&nbsp;
                        House Price: ₹{first['HousePrice']:,.0f} &nbsp;·&nbsp;
                        Max Loan: ₹{first['MaxLoan']:,.0f} &nbsp;·&nbsp;
                        EMI: ₹{first['EffEMI']:,.0f}/mo{sqft_extra}
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

        # ── KPI Row ──
        last = df_res.iloc[-1]
        years_span = st.session_state.max_age - st.session_state.age
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card blue">
                <div class="label">Final Portfolio (Age {st.session_state.max_age})</div>
                <div class="value">₹{last['Portfolio']/1e7:.2f} Cr</div>
                <div class="delta">across {years_span} years</div>
            </div>
            <div class="metric-card">
                <div class="label">House Price (Age {st.session_state.max_age})</div>
                <div class="value">₹{last['HousePrice']/1e7:.2f} Cr</div>
                <div class="delta">at {st.session_state.house_infl}% inflation</div>
            </div>
            <div class="metric-card">
                <div class="label">Annual Surplus (Age {st.session_state.max_age})</div>
                <div class="value">₹{last['Surplus/yr']/1e5:.1f} L</div>
                <div class="delta">per year at final age</div>
            </div>
            <div class="metric-card">
                <div class="label">Affordable Windows</div>
                <div class="value">{len(affordable_rows)}</div>
                <div class="delta">years out of {years_span + 1}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Chart ──
        section_header("📈", "Portfolio vs House Price Over Time")
        chart_df = df_res[['Age', 'Portfolio', 'HousePrice']].copy()
        chart_df = chart_df.rename(columns={
            'Portfolio': 'Portfolio Value',
            'HousePrice': 'House Price (incl. costs)'})
        chart_df = chart_df.set_index('Age')
        st.line_chart(chart_df, use_container_width=True, height=260)

        # ── Warnings ──
        if over_details:
            msg = "**⚠️ Budget Deficit:** Planned SIPs exceed surplus — "
            msg += ", ".join([f"Age {a} (₹{v:,.0f})" for a, v in over_details[:5]])
            if len(over_details) > 5: msg += f" + {len(over_details)-5} more"
            st.error(msg)
        if under_details:
            msg = "**ℹ️ Unallocated Surplus:** Uninvested surplus in — "
            msg += ", ".join([f"Age {a} (₹{v:,.0f})" for a, v in under_details[:5]])
            if len(under_details) > 5: msg += f" + {len(under_details)-5} more"
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
                return 'background-color: rgba(34,197,94,0.15); color: #166534; font-weight: 700;'
            return 'color: #64748b;'

        format_dict = {
            'TakeHome/mo': '₹{:,.0f}', 'Surplus/yr': '₹{:,.0f}',
            'Portfolio': '₹{:,.0f}', 'HousePrice': '₹{:,.0f}',
            'MaxLoan': '₹{:,.0f}', 'CashLeft': '₹{:,.0f}',
            'EffEMI': '₹{:,.0f}', 'AffEMI': '₹{:,.0f}',
            'Tax%': '{:.1f}%', 'Eff_Return%': '{:.1f}%',
        }
        if show_sqft:
            format_dict['Aff_Sqft'] = '{:,.0f} sq ft'

        display_df = df_res if show_sqft else df_res.drop(columns=['Aff_Sqft'], errors='ignore')
        display_styled = (display_df.style
                          .format({k: v for k, v in format_dict.items() if k in display_df.columns})
                          .map(color_affordable, subset=['Affordable']))

        st.dataframe(
            display_styled,
            use_container_width=True,
            height=540,
            column_config={
                "Portfolio_Breakdown": st.column_config.TextColumn(
                    "Portfolio Breakdown",
                    help="Asset balances post-rebalancing for this year.",
                    width="large"
                ),
                "Aff_Sqft": st.column_config.NumberColumn(
                    "Affordable Sq Ft",
                    help="How many sq ft you can buy this year with your total budget (portfolio + max loan).",
                    format="%d sq ft"
                ),
            }
        )
