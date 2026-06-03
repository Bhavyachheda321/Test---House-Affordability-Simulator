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
.block-container{padding:1rem 2rem 3rem !important;max-width:1400px;}

/* ── Hero ── */
.hero{background:linear-gradient(135deg,#1d6fce 0%,#2d4a9e 60%,#1e3a8a 100%);border-radius:16px;padding:1.4rem 2rem;margin-bottom:.8rem;position:relative;overflow:hidden;box-shadow:0 8px 24px rgba(29,111,206,.25);}
.hero::before{content:'';position:absolute;top:-50px;right:-50px;width:200px;height:200px;background:radial-gradient(circle,rgba(255,255,255,.12) 0%,transparent 70%);pointer-events:none;}
.hero-title{font-size:1.7rem;font-weight:800;letter-spacing:-.02em;color:#ffffff;margin:0 0 .25rem;text-shadow:0 1px 3px rgba(0,0,0,.2);}
.hero-sub{font-size:.88rem;color:rgba(255,255,255,.85);margin:0;font-weight:500;line-height:1.5;}
/* action strip inside hero */
.hero-strip{display:flex;gap:.6rem;align-items:center;margin-top:.9rem;flex-wrap:wrap;}
.hero-pill{background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.3);border-radius:20px;padding:.3rem .85rem;font-size:.78rem;font-weight:600;color:#ffffff;cursor:pointer;transition:background .15s;white-space:nowrap;}
.hero-pill:hover{background:rgba(255,255,255,.25);}

/* ── Info strip (editorial + how-to in one row) ── */
.info-strip{display:flex;gap:.75rem;margin-bottom:.8rem;flex-wrap:wrap;}
.info-card{flex:1;min-width:260px;background:var(--surface);border:1.5px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow-sm);}
.info-card summary{padding:.65rem 1rem;font-size:.82rem;font-weight:700;color:var(--text-secondary);cursor:pointer;list-style:none;display:flex;align-items:center;gap:.5rem;}
.info-card summary::after{content:'▾';margin-left:auto;font-size:.75rem;color:var(--text-muted);}
.info-card[open] summary::after{content:'▴';}
.info-card .body{padding:.8rem 1rem 1rem;border-top:1px solid var(--border);font-size:.84rem;color:var(--text-secondary);line-height:1.65;}

/* ── Metric cards ── */
.metric-row{display:flex;gap:1rem;margin-bottom:1.5rem;flex-wrap:wrap;}
.metric-card{flex:1;min-width:165px;background:var(--surface);border:1.5px solid var(--border);border-radius:var(--radius);padding:1.1rem 1.3rem;box-shadow:var(--shadow-sm);transition:box-shadow .2s,border-color .2s;}
.metric-card:hover{box-shadow:var(--shadow);border-color:var(--accent);}
.metric-card .label{font-size:.7rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--text-muted);margin-bottom:.5rem;}
.metric-card .value{font-size:1.5rem;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--text);line-height:1;}
.metric-card .delta{font-size:.74rem;color:var(--text-muted);margin-top:.35rem;font-weight:500;}
.metric-card.blue{border-color:#93c5fd;background:#eff6ff;}.metric-card.blue .value{color:var(--accent-dark);}
.metric-card.green{border-color:var(--green-border);background:var(--green-bg);}.metric-card.green .value{color:var(--green);}
.metric-card.red{border-color:var(--red-border);background:var(--red-bg);}.metric-card.red .value{color:var(--red);}

/* ── Section headers ── */
.section-header{display:flex;align-items:center;gap:.65rem;margin:1.4rem 0 .75rem;padding-bottom:.55rem;border-bottom:2px solid var(--border);}
.section-header .icon{font-size:1rem;width:30px;height:30px;background:var(--accent-soft);border-radius:8px;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.section-header h3{font-size:.88rem;font-weight:700;letter-spacing:.01em;color:var(--text);margin:0;text-transform:uppercase;}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]{background:var(--surface) !important;border-radius:var(--radius) !important;padding:5px !important;gap:3px !important;border:1.5px solid var(--border) !important;box-shadow:var(--shadow-sm) !important;}
.stTabs [data-baseweb="tab"]{background:transparent !important;border-radius:var(--radius-sm) !important;color:var(--text-secondary) !important;font-size:.85rem !important;font-weight:600 !important;padding:.5rem 1.2rem !important;transition:all .15s !important;}
.stTabs [data-baseweb="tab"]:hover{background:var(--accent-soft) !important;color:var(--accent) !important;}
.stTabs [aria-selected="true"]{background:var(--accent) !important;color:#ffffff !important;box-shadow:0 2px 6px rgba(29,111,206,.3) !important;}
.stTabs [data-baseweb="tab-panel"]{padding-top:1rem !important;}

/* ── Inputs ── */
.stNumberInput > div > div > input,.stTextInput > div > div > input{background:var(--surface) !important;border:1.5px solid var(--border) !important;border-radius:var(--radius-sm) !important;color:var(--text) !important;font-family:'Plus Jakarta Sans',sans-serif !important;font-size:.9rem !important;font-weight:500 !important;}
.stNumberInput > div > div > input:focus,.stTextInput > div > div > input:focus{border-color:var(--accent) !important;box-shadow:0 0 0 3px rgba(29,111,206,.15) !important;}
.stSelectbox > div > div{background:var(--surface) !important;border:1.5px solid var(--border) !important;border-radius:var(--radius-sm) !important;color:var(--text) !important;}
label[data-testid="stWidgetLabel"] > div,label[data-testid="stWidgetLabel"] p{font-size:.78rem !important;font-weight:700 !important;color:var(--text-secondary) !important;letter-spacing:.04em !important;text-transform:uppercase !important;}

/* ── Expander (standard) ── */
details > summary{background:var(--surface2) !important;border:1.5px solid var(--border) !important;border-radius:var(--radius-sm) !important;padding:.6rem 1rem !important;font-size:.85rem !important;font-weight:600 !important;color:var(--text) !important;cursor:pointer;}
details[open] > summary{border-radius:var(--radius-sm) var(--radius-sm) 0 0 !important;border-bottom:none !important;}
details > div{background:var(--surface) !important;border:1.5px solid var(--border) !important;border-top:none !important;border-radius:0 0 var(--radius-sm) var(--radius-sm) !important;padding:.8rem 1rem !important;}

/* ── Buttons ── */
.stButton > button[kind="primary"]{background:linear-gradient(135deg,#1d6fce,#2d4a9e) !important;border:none !important;border-radius:var(--radius-sm) !important;color:#ffffff !important;font-weight:700 !important;font-size:.92rem !important;padding:.65rem 1.8rem !important;box-shadow:0 3px 10px rgba(29,111,206,.3) !important;transition:all .2s !important;}
.stButton > button[kind="primary"]:hover{transform:translateY(-1px) !important;box-shadow:0 5px 18px rgba(29,111,206,.45) !important;}
.stButton > button[kind="secondary"],.stButton > button:not([kind]){background:var(--surface) !important;border:1.5px solid var(--border-dark) !important;border-radius:var(--radius-sm) !important;color:var(--text-secondary) !important;font-weight:600 !important;}
.stDownloadButton > button{background:var(--surface) !important;border:1.5px solid var(--border-dark) !important;border-radius:var(--radius-sm) !important;color:var(--text) !important;font-weight:600 !important;font-size:.87rem !important;}
.stDownloadButton > button:hover{background:var(--accent-soft) !important;border-color:var(--accent) !important;color:var(--accent) !important;}

/* ── Save-run banner ── */
.save-banner{background:var(--amber-bg);border:1.5px solid var(--amber-border);border-radius:var(--radius-sm);padding:.8rem 1.2rem;margin-bottom:1rem;display:flex;align-items:center;gap:1rem;flex-wrap:wrap;}
.save-banner .sb-text{flex:1;min-width:200px;}
.save-banner .sb-title{font-size:.85rem;font-weight:700;color:var(--amber);}
.save-banner .sb-sub{font-size:.78rem;color:var(--text-secondary);margin-top:.15rem;line-height:1.5;}

/* ── Nav row ── */
.nav-row{display:flex;justify-content:space-between;align-items:center;margin-top:1.8rem;padding-top:1rem;border-top:1.5px solid var(--border);}

/* ── Dataframe ── */
.stDataFrame{border-radius:var(--radius) !important;overflow:hidden;box-shadow:var(--shadow-sm);}
[data-testid="stDataFrameResizable"]{border:1.5px solid var(--border) !important;border-radius:var(--radius) !important;}

/* ── Alerts ── */
.stAlert,[data-testid="stNotification"]{border-radius:var(--radius-sm) !important;}

/* ── Result banner ── */
.result-banner{border-radius:var(--radius);padding:1.3rem 1.8rem;margin-bottom:1.1rem;border:2px solid;display:flex;align-items:center;gap:1.2rem;box-shadow:var(--shadow-sm);}
.result-banner.success{background:var(--green-bg);border-color:var(--green-border);}
.result-banner.failure{background:var(--red-bg);border-color:var(--red-border);}
.result-banner .emoji{font-size:2.2rem;flex-shrink:0;}
.result-banner .title{font-size:1.3rem;font-weight:800;line-height:1.2;}
.result-banner .sub{font-size:.84rem;margin-top:.25rem;font-weight:500;line-height:1.6;}
.result-banner.success .title{color:var(--green);}
.result-banner.success .sub{color:#166534cc;}
.result-banner.failure .title{color:var(--red);}
.result-banner.failure .sub{color:#991b1baa;}

/* ── Tip box ── */
.tip-box{background:var(--accent-soft);border:1.5px solid #93c5fd;border-radius:var(--radius-sm);padding:.7rem 1rem;font-size:.83rem;color:var(--text-secondary);margin-bottom:1rem;line-height:1.6;font-weight:500;}
.tip-box strong{color:var(--accent-dark);font-weight:700;}

/* ── Rebalance help ── */
.rb-help{background:var(--surface2);border:1.5px solid var(--border);border-radius:var(--radius-sm);padding:.8rem 1rem;font-size:.82rem;color:var(--text-secondary);margin-bottom:.8rem;line-height:1.7;}
.rb-help b{color:var(--text);font-weight:700;}

/* ── Misc ── */
hr{border-color:var(--border) !important;margin:1.2rem 0 !important;}
.stCheckbox label p{font-size:.85rem !important;color:var(--text-secondary) !important;font-weight:500 !important;}
.stRadio label p{font-size:.85rem !important;color:var(--text-secondary) !important;font-weight:500 !important;}
[data-testid="stFileUploader"]{background:var(--surface2) !important;border:2px dashed var(--border-dark) !important;border-radius:var(--radius) !important;}
[data-testid="metric-container"]{background:var(--surface) !important;border:1.5px solid var(--border) !important;border-radius:var(--radius) !important;padding:1rem 1.2rem !important;box-shadow:var(--shadow-sm) !important;}
[data-testid="metric-container"] label{color:var(--text-muted) !important;font-size:.78rem !important;font-weight:700 !important;text-transform:uppercase !important;letter-spacing:.05em !important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:var(--text) !important;font-family:'JetBrains Mono',monospace !important;font-weight:700 !important;}
::-webkit-scrollbar{width:6px;height:6px;}::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border-dark);border-radius:4px;}::-webkit-scrollbar-thumb:hover{background:var(--accent);}
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

REBALANCE_COLS = [
    "Trigger_Type", "Source_Asset", "Destination_Asset",
    "Transfer_Type", "Value",
    "Start_Age", "End_Age", "Frequency_Years",
    "Threshold_Asset", "Threshold_Amount"
]
if 'rebalance_table' not in st.session_state:
    st.session_state['rebalance_table'] = pd.DataFrame(columns=REBALANCE_COLS)
else:
    # migrate old schema that only had Year/Source/Destination/Transfer_Type/Value
    existing = st.session_state['rebalance_table']
    if 'Trigger_Type' not in existing.columns:
        new_rb = pd.DataFrame(columns=REBALANCE_COLS)
        if not existing.empty and 'Year' in existing.columns:
            for _, row in existing.iterrows():
                new_rb = pd.concat([new_rb, pd.DataFrame([{
                    "Trigger_Type": "One-Time",
                    "Source_Asset": row.get("Source_Asset", ""),
                    "Destination_Asset": row.get("Destination_Asset", ""),
                    "Transfer_Type": row.get("Transfer_Type", "Percentage"),
                    "Value": row.get("Value", 0),
                    "Start_Age": row.get("Year", 0),
                    "End_Age": None, "Frequency_Years": None,
                    "Threshold_Asset": None, "Threshold_Amount": None
                }])], ignore_index=True)
        st.session_state['rebalance_table'] = new_rb

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
                rb = pd.DataFrame(data["rebalance_events"])
                if 'Trigger_Type' not in rb.columns:
                    rb = pd.DataFrame(columns=REBALANCE_COLS)
                st.session_state['rebalance_table'] = rb
            st.success("✅ Scenario loaded successfully!")
        except Exception as e:
            st.error(f"Error loading scenario: {e}")


def go_to_tab(n):
    st.session_state['active_tab'] = n


# =============================================================================
# TAX ENGINE
# =============================================================================
NEW_REGIME_SLABS = [
    (400_000,0.00),(800_000,0.05),(1_200_000,0.10),
    (1_600_000,0.15),(2_000_000,0.20),(2_400_000,0.25),(float('inf'),0.30)
]
OLD_REGIME_SLABS = [
    (250_000,0.00),(500_000,0.05),(1_000_000,0.20),(float('inf'),0.30)
]
SURCHARGE_NEW = [(5e6,0.),(10e6,.10),(20e6,.15),(float('inf'),.25)]
SURCHARGE_OLD = [(5e6,0.),(10e6,.10),(20e6,.15),(50e6,.25),(float('inf'),.37)]
CESS = 0.04
STD_OLD, STD_NEW = 50_000, 75_000

def emi_monthly(principal, r_ann, years):
    if principal<=0 or years<=0: return 0.0
    n=years*12
    if r_ann==0: return principal/n
    r=r_ann/12
    return principal*r*((1+r)**n)/(((1+r)**n)-1)

def max_loan_from_emi(emi, r_ann, years):
    if emi<=0 or years<=0: return 0.0
    n=years*12
    if r_ann==0: return emi*n
    r=r_ann/12
    return emi*(((1+r)**n)-1)/(r*((1+r)**n))

def _scale(slabs,f): return [(l*f if l!=float('inf') else float('inf'),r) for l,r in slabs]
def _slab(inc,slabs):
    tax,prev=0.,0.
    for l,r in slabs:
        if inc<=prev: break
        tax+=(min(inc,l)-prev)*r; prev=l
    return tax
def _sur(inc,reg):
    th=SURCHARGE_NEW if reg=="new" else SURCHARGE_OLD
    for l,r in th:
        if inc<=l: return r
    return th[-1][1]

def compute_annual_tax(annual_gross, tax_regime, other_80c=0., basic_m=0.,
                       hra_m=0., rent_m=0., metro=True, nps_ann=0., nps_pct=0., scale=1.):
    nps = nps_ann if nps_ann>0 else basic_m*12*(nps_pct/100.) if basic_m>0 else 0.
    nps = min(nps, basic_m*12*0.10 if basic_m>0 else float('inf'))
    if tax_regime=="old":
        hra_ex=0.
        if basic_m>0 and hra_m>0 and rent_m>0:
            hra_ex=min(hra_m*12,(basic_m*12)*(0.50 if metro else 0.40),
                       max(0.,(rent_m*12)-0.10*(basic_m*12)))
        ded = STD_OLD + hra_ex + min(other_80c,150_000) + nps
        ti = max(0., annual_gross-ded)
        bt = _slab(ti,_scale(OLD_REGIME_SLABS,scale))
        if ti<=500_000*scale: bt=max(0.,bt-12_500)
    else:
        ded = STD_NEW + nps
        ti = max(0., annual_gross-ded)
        bt = _slab(ti,_scale(NEW_REGIME_SLABS,scale))
        if ti<=1_200_000*scale: bt=0.
        elif ti<=1_275_000*scale: bt=min(bt,ti-1_200_000*scale)
    sur=bt*_sur(ti,tax_regime)
    cess_amt=(bt+sur)*CESS
    total=bt+sur+cess_amt
    return {'total_tax':total,'take_home_monthly':(annual_gross-total)/12,
            'effective_rate':(total/annual_gross) if annual_gross>0 else 0.}


# =============================================================================
# REBALANCE ENGINE
# =============================================================================
def build_rebalance_schedule(rb_df, name_to_idx, sim_start_age, max_years):
    """
    Convert rebalance rules into a year-indexed schedule dict.
    Key insight: Start_Age=0 or blank means "use simulation start age" for
    One-Time/Annual, and "first fire after one frequency period" for Every N Years.
    This prevents rebalancing from firing spuriously in year 0 before assets accumulate.
    """
    schedule = {}

    def add(t, rule):
        if 0 <= t <= max_years:
            schedule.setdefault(t, []).append(rule)

    for _, row in rb_df.iterrows():
        trigger   = str(row.get("Trigger_Type","")).strip()
        src       = str(row.get("Source_Asset","")).strip()
        dest      = str(row.get("Destination_Asset","")).strip()
        t_type    = str(row.get("Transfer_Type","Percentage")).strip()
        val       = float(row.get("Value",0) or 0)

        # Safely parse ages — None/NaN/0 all treated as "not set"
        def _age(key, default=0):
            v = row.get(key, None)
            try:
                iv = int(float(v))
                return iv if iv > 0 else default
            except (TypeError, ValueError):
                return default

        start_age = _age("Start_Age", sim_start_age)
        end_age   = _age("End_Age",   0)
        freq      = max(1, _age("Frequency_Years", 1))
        thr_asset = str(row.get("Threshold_Asset","") or "").strip()
        thr_amt   = float(row.get("Threshold_Amount",0) or 0)

        if src not in name_to_idx or dest not in name_to_idx:
            continue
        si, di = name_to_idx[src], name_to_idx[dest]

        if trigger == "One-Time":
            sim_t = start_age - sim_start_age
            add(sim_t, (si, di, t_type, val))

        elif trigger == "Annual":
            # start_age=0 means start from year 1 (not year 0) to avoid spurious t=0 fire
            s = max(1, start_age - sim_start_age)
            e = min(max_years, (end_age - sim_start_age) if end_age > sim_start_age else max_years)
            for sim_t in range(s, e + 1):
                add(sim_t, (si, di, t_type, val))

        elif trigger == "Every N Years":
            # If start_age not meaningfully set, first fire is at t=freq (not t=0)
            if start_age <= sim_start_age:
                s = freq   # first fire after one full period
            else:
                s = max(1, start_age - sim_start_age)
            e = min(max_years, (end_age - sim_start_age) if end_age > sim_start_age else max_years)
            sim_t = s
            while sim_t <= e:
                add(sim_t, (si, di, t_type, val))
                sim_t += freq

        elif trigger == "Balance Threshold":
            thr_idx = name_to_idx.get(thr_asset, -1)
            if thr_idx == -1: continue
            s = max(1, start_age - sim_start_age) if start_age > sim_start_age else 1
            e = min(max_years, (end_age - sim_start_age) if end_age > sim_start_age else max_years)
            for sim_t in range(s, e + 1):
                add(sim_t, ('__thr__', si, di, t_type, val, thr_idx, thr_amt))

    return schedule


# =============================================================================
# PORTFOLIO SIMULATION
# =============================================================================
TIMING = {'start': lambda r:(1+r), 'mid': lambda r:(1+r)**.5,
           'end': lambda r:1., 'monthly': lambda r:(1+r)**.5}

def simulate_portfolio(params, asset_classes, reinvest_rules, rebalance_df):
    series, n = [], len(asset_classes)
    bals = [ac["initial_value"] for ac in asset_classes]
    cash_acc = 0.0
    name_to_idx = {ac['name']: i for i, ac in enumerate(asset_classes)}

    reinvest_map = {}
    for r in reinvest_rules:
        s,d,p = r['Source_Asset'],r['Destination_Asset'],r['Allocation_Pct']
        if s in name_to_idx and d in name_to_idx:
            si,di = name_to_idx[s], name_to_idx[d]
            reinvest_map.setdefault(si,[]).append((di, p/100.))

    rb_schedule = build_rebalance_schedule(
        rebalance_df, name_to_idx, params['age'], params['max_years'])

    for t in range(params['max_years']+1):
        gm = params['income_0']*((1+params['inc_growth'])**t)
        ga = gm*12
        rm = params['rent_0']*((1+params['rent_infl'])**t)
        sc = (1+params['slab_infl'])**t

        ti = compute_annual_tax(ga, params['tax_regime'],
            other_80c=params['other_80c'], basic_m=params['basic_m'],
            hra_m=params['hra_m'], rent_m=rm, metro=params['metro'],
            nps_ann=params['nps_ann'], nps_pct=params['nps_pct'], scale=sc)

        slab_inc = sum(bals[i]*ac['annual_return'] for i,ac in enumerate(asset_classes)
                       if ac['tax_treatment']=='Taxed at slab rate')
        if slab_inc>0:
            ti2 = compute_annual_tax(ga+slab_inc, params['tax_regime'],
                other_80c=params['other_80c'], basic_m=params['basic_m'],
                hra_m=params['hra_m'], rent_m=rm, metro=params['metro'],
                nps_ann=params['nps_ann'], nps_pct=params['nps_pct'], scale=sc)
            eff_r = ti2['effective_rate']
        else:
            eff_r = ti['effective_rate']

        th = params['net_0']*((1+params['inc_growth'])**t) if params['net_0']>0 \
             else ti['take_home_monthly']
        exp = th*params['exp_frac'] if params['exp_mode']=='fraction' \
              else params['exp_abs']*((1+params['exp_infl'])**t)

        bg = (params['bonus_0']*((1+params['bonus_gr'])**t) if params['bonus_mode']=='fixed'
              else ga*(params['bonus_0']/100.)*((1+params['bonus_gr'])**t))
        bn = bg*(1.-eff_r) if params['bonus_gross'] else bg
        bs = bn*(params['bonus_sav_pct']/100.)

        surplus = max(0., th*12 - exp*12 - rm*12) + bs
        req_liq = params['cash_buf']*((1+params['buf_infl'])**t)

        sips, sip_lim = [], 0.
        for ac in asset_classes:
            mb = ac.get("monthly_contribution",0.)
            mc = mb*((1+ac.get("stepup_value",0.)/100.)**t) if ac.get("stepup_type","pct")=="pct" \
                 else mb+ac.get("stepup_value",0.)*t
            s_ = max(0.,mc*12); sips.append(s_)
            if not ac.get("invest_above_surplus",False): sip_lim += s_

        shortfall = max(0., sip_lim-surplus)
        excess    = max(0., surplus-sip_lim)

        alloc_in = [0.]*n
        if excess>0:
            ap = [max(0.,ac.get("surplus_alloc_pct",0.)) for ac in asset_classes]
            ta = sum(ap)
            if ta>0: alloc_in = [excess*(p/ta) for p in ap]
            else: cash_acc += excess

        op = sum(bals)
        net_ret = []
        for i,ac in enumerate(asset_classes):
            gr = ac["annual_return"]
            nr = gr if ac['tax_treatment']=='Exempt' \
                 else gr*(1-ac['fixed_tax_pct']) if ac['tax_treatment']=='Taxed at fixed rate' \
                 else gr*(1-eff_r)
            net_ret.append(bals[i]*nr)

        ri = [0.]*n
        for i in range(n):
            if i in reinvest_map:
                for di,p in reinvest_map[i]: ri[di] += net_ret[i]*p
            else: ri[i] += net_ret[i]

        new_bals, tot_add = [], 0.
        for i,ac in enumerate(asset_classes):
            tf = TIMING.get(ac.get("contribution_timing","monthly"), TIMING["monthly"])
            add_ = sips[i]+alloc_in[i]; tot_add += add_
            new_bals.append(bals[i]+ri[i]+add_*tf(0))

        if t in rb_schedule:
            for rule in rb_schedule[t]:
                if rule[0]=='__thr__':
                    _,si,di,rt,rv,ti_,ta_ = rule
                    if new_bals[ti_]>=ta_:
                        amt = new_bals[si]*(rv/100.) if rt=='Percentage' else min(new_bals[si],rv)
                        new_bals[si]=max(0.,new_bals[si]-amt); new_bals[di]+=amt
                else:
                    si,di,rt,rv = rule
                    amt = new_bals[si]*(rv/100.) if rt=='Percentage' else min(new_bals[si],rv)
                    new_bals[si]=max(0.,new_bals[si]-amt); new_bals[di]+=amt

        bd = ["  |  ".join([f"{ac['name']}: ₹{new_bals[i]:,.0f}"
                             for i,ac in enumerate(asset_classes)])]
        if cash_acc>0: bd.append(f"Static Cash: ₹{cash_acc:,.0f}")

        cl = sum(new_bals); gain = cl-op-tot_add
        ib = op+(tot_add/2); eff_ret = (gain/ib) if ib>0 else 0.
        bals = new_bals
        pv = sum(bals)+cash_acc

        series.append({
            'year':t,'portfolio_value':pv,'opening_portfolio':op,
            'gross_monthly':gm,'take_home_monthly':th,
            'expense_monthly':exp,'rent_monthly':rm,
            'surplus_yr':surplus,'req_liquid':req_liq,
            'tax_info':ti,'shortfall_amt':shortfall,'excess_amt':excess,
            'eff_return_rate':eff_ret,
            'Portfolio_Breakdown':"  |  ".join(bd)
        })
    return series


def _check_affordable(h_price, v_t, max_loan_t, req_liquid,
                       params, take_home_m, gross_m, emi_aff_net):
    """Return (affordable_bool, actual_emi) for a given house price."""
    outlay = h_price * (1 + params['tx_cost'])
    loan = min(max_loan_t, outlay) if params['loan_enabled'] else 0.0
    down = max(0., outlay - loan)
    cash_rem = v_t - down
    c1 = (v_t + max_loan_t) >= outlay
    c2 = cash_rem >= req_liquid
    emi = emi_monthly(loan, params['loan_rate'], params['loan_tenure']) \
          if params['loan_enabled'] and loan > 0 else 0.0
    c3 = emi <= emi_aff_net if params['loan_enabled'] else True
    return (c1 and c2 and c3), emi


def compute_affordable_sqft(v_t, max_loan_t, req_liquid, h_t, target_sqft):
    """
    Compute affordable sq ft using the direct formula:
        Aff_Sqft = (Portfolio + MaxLoan - CashBuffer) / (HousePrice_t / TargetSqft)

    - HousePrice_t / TargetSqft  = implied price per sq ft this year
      (derived from the house price the user entered, inflated to year t)
    - Portfolio + MaxLoan - CashBuffer = net spendable budget after
      keeping the required cash buffer aside

    Returns 0 if target_sqft is 0, if the implied psf is 0,
    or if the net budget is negative.
    """
    if target_sqft <= 0 or h_t <= 0:
        return 0.0
    implied_psf = h_t / target_sqft        # ₹ per sq ft at year t
    net_budget  = v_t + max_loan_t - req_liquid
    if net_budget <= 0 or implied_psf <= 0:
        return 0.0
    return net_budget / implied_psf


def run_affordability(params, asset_classes, reinvest_rules, rebalance_df):
    series = simulate_portfolio(params, asset_classes, reinvest_rules, rebalance_df)
    res = []
    over_details, under_details = [], []
    total_alloc = sum(ac.get('surplus_alloc_pct',0.) for ac in asset_classes)
    perfect_alloc = abs(total_alloc-100.)<0.001

    for t, ps in enumerate(series):
        age = params['age']+t
        h_t = params['house_price']*((1+params['house_infl'])**t)
        v_t = ps['portfolio_value']
        outlay = h_t*(1+params['tx_cost'])

        if ps['shortfall_amt']>0: over_details.append((age,ps['shortfall_amt']))
        if ps['excess_amt']>0 and not perfect_alloc: under_details.append((age,ps['excess_amt']))

        max_loan_t, emi_aff_net = 0., 0.
        if params['loan_enabled']:
            emi_aff = (ps['take_home_monthly']*params['emi_frac']
                       if params['emi_mode']=='fraction' else params['emi_fixed'])
            emi_aff_net = emi_aff*(1-params['emi_buf'])
            max_loan_t = min(
                max_loan_from_emi(emi_aff_net, params['loan_rate'], params['loan_tenure']),
                ps['gross_monthly']*params['bank_mult'])
            if params['user_max_loan']>0:
                max_loan_t = min(max_loan_t, params['user_max_loan']*((1+params['house_infl'])**t))

        affordable, actual_emi = _check_affordable(
            h_t, v_t, max_loan_t, ps['req_liquid'],
            params, ps['take_home_monthly'], ps['gross_monthly'], emi_aff_net)

        # Affordable sq ft — direct formula
        aff_sqft_val = compute_affordable_sqft(
            v_t, max_loan_t, ps['req_liquid'],
            h_t, params.get('target_sqft', 0))

        res.append({
            'Age': age,
            'TakeHome/mo': ps['take_home_monthly'],
            'Surplus/yr':  ps['surplus_yr'],
            'Portfolio':   v_t,
            'HousePrice':  h_t,
            'MaxLoan':     max_loan_t,
            'CashLeft':    v_t - max(0., outlay - min(max_loan_t, outlay)),
            'EffEMI':      actual_emi,
            'AffEMI':      emi_aff_net,
            'Tax%':        ps['tax_info']['effective_rate']*100,
            'Eff_Return%': ps['eff_return_rate']*100,
            'Affordable':  "YES ✓" if affordable else "No",
            'Aff_Sqft':    aff_sqft_val,
            'Portfolio_Breakdown': ps['Portfolio_Breakdown']
        })

    return res, over_details, under_details


# =============================================================================
# HELPERS
# =============================================================================
def section_header(icon, title):
    st.markdown(f"""<div class="section-header">
        <div class="icon">{icon}</div><h3>{title}</h3>
    </div>""", unsafe_allow_html=True)

def tip(text):
    st.markdown(f'<div class="tip-box">{text}</div>', unsafe_allow_html=True)

def nav_buttons(current_tab, total=4):
    st.markdown('<div class="nav-row">', unsafe_allow_html=True)
    cp, _, cn = st.columns([1,4,1])
    with cp:
        if current_tab>0:
            if st.button("← Previous", key=f"prev_{current_tab}"):
                go_to_tab(current_tab-1); st.rerun()
    with cn:
        if current_tab<total-1:
            lbl = "Go to Results →" if current_tab==total-2 else "Next →"
            if st.button(lbl, key=f"next_{current_tab}", type="primary"):
                go_to_tab(current_tab+1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# ── HERO + COMPACT TOP BAR ──
# =============================================================================
# Build scenario export JSON (always available for hero buttons)
_export_data = {
    "params": {k: st.session_state[k] for k in default_params.keys()},
    "assets": st.session_state['assets_table'].to_dict(orient='records'),
    "reinvest_rules": st.session_state['reinvest_table'].to_dict(orient='records'),
    "rebalance_events": st.session_state['rebalance_table'].to_dict(orient='records')
}
_export_json = json.dumps(_export_data, indent=2)

st.markdown("""
<div class="hero">
    <div class="hero-title">🏠 House Affordability Simulator</div>
    <div class="hero-sub">
        A year-by-year forecast of when you can afford your home — factoring in income growth,
        tax, investments, inflation, and loan eligibility.
    </div>
</div>
""", unsafe_allow_html=True)

# ── compact info strip: editorial + how-to side by side, collapsed by default ──
st.markdown('<div class="info-strip">', unsafe_allow_html=True)
col_ed, col_ht, col_ls = st.columns([2, 2, 1])

with col_ed:
    with st.expander("📌  What problem does this solve?", expanded=False):
        st.markdown("""
Buying a home is the single largest financial decision most Indian families make — yet most people plan
with nothing more than a rough gut feel. They don't know *when* they can realistically afford it,
*how much* they need to save, or whether their investments keep pace with rising property prices.

This simulator brings together every variable that matters — income growth, tax deductions, expenses,
rent, investment returns, and loan eligibility — and projects them year by year. The result is a clear,
data-driven answer: the **earliest age at which you can afford your target home**, with a full breakdown
for every year along the way.
        """)

with col_ht:
    with st.expander("🎬  How to use this app", expanded=False):
        LOOM_URL = "https://www.loom.com/share/YOUR_LOOM_VIDEO_ID_HERE"
        st.info(f"📹 **Video placeholder** — replace `LOOM_URL` in source with your Loom `.mp4` link, "
                f"then change `st.info(...)` to `st.video(LOOM_URL)`.", icon="ℹ️")
        st.markdown("""
| Tab | Fill in | Why |
|-----|---------|-----|
| 👤 Personal & Housing | Age, target home price, sq ft | Sets the goal |
| 💰 Income & Expenses | Salary, tax, rent, bonus, spend | Computes monthly surplus |
| 📈 Assets & Loan | Investments, SIPs, rebalancing, loan | Models wealth growth |
| 📊 Results | Click ▶ Run | Year-by-year forecast |

**Tip:** Use **Next →** at the bottom of each tab to move forward.
        """)

with col_ls:
    with st.expander("💾  Load / Save", expanded=False):
        st.markdown("**Load**")
        st.file_uploader("Upload .json", type="json", key="scenario_uploader",
                         on_change=handle_scenario_upload, label_visibility="collapsed")
        st.markdown("**Save inputs**")
        st.download_button("📤 Download Setup",
                           data=_export_json,
                           file_name="house_scenario.json",
                           mime="application/json",
                           use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# TABS — shown prominently right below hero
# =============================================================================
# ── Manual tab bar (so Next/Prev buttons actually work) ──
TAB_LABELS = [
    ("👤", "Personal & Housing"),
    ("💰", "Income & Expenses"),
    ("📈", "Assets & Loan"),
    ("📊", "Results"),
]
_at = st.session_state.get('active_tab', 0)

tab_cols = st.columns(len(TAB_LABELS))
for _i, (_icon, _label) in enumerate(TAB_LABELS):
    with tab_cols[_i]:
        _is_active = (_i == _at)
        _btn_style = (
            "background:linear-gradient(135deg,#1d6fce,#2d4a9e);color:#fff;border:none;"
            "border-radius:8px;padding:.55rem 1rem;font-weight:700;font-size:.85rem;"
            "width:100%;cursor:pointer;box-shadow:0 2px 6px rgba(29,111,206,.3);"
        ) if _is_active else (
            "background:#fff;color:#334155;border:1.5px solid #d1dbe8;"
            "border-radius:8px;padding:.55rem 1rem;font-weight:600;font-size:.85rem;"
            "width:100%;cursor:pointer;"
        )
        if st.button(f"{_icon}  {_label}", key=f"tab_btn_{_i}",
                     use_container_width=True,
                     type="primary" if _is_active else "secondary"):
            st.session_state['active_tab'] = _i
            st.rerun()

st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
_at = st.session_state.get('active_tab', 0)  # re-read after potential rerun

# ─────────────────────────────────────────────
# TAB 1
# ─────────────────────────────────────────────
if _at == 0:
    tip("Start here. Tell the simulator <strong>who you are</strong> and <strong>what home you want to buy</strong>.")
    col1, col2 = st.columns(2, gap="large")

    with col1:
        section_header("🧑", "Your Details")
        c1,c2 = st.columns(2)
        with c1:
            st.number_input("Current Age", min_value=18, max_value=80, key="age",
                help="Your age today in years. The simulation starts from this age.\nExample: 32")
        with c2:
            st.number_input("Simulate up to Age", min_value=19, key="max_age",
                help="The simulator calculates year by year up to this age.\nExample: 60")

    with col2:
        section_header("🏡", "Target Property")
        c1,c2 = st.columns(2)
        with c1:
            st.number_input("House Price Today (₹)", step=500_000, key="house_price",
                help="Current market price of the home you want to buy. Inflated automatically each year.\nExample: ₹1.5 Cr → enter 15000000")
            st.number_input("Annual Price Inflation (%)", key="house_infl",
                help="How fast property prices rise per year. Typically 5–8% in Indian metros.\nExample: 6.0")
        with c2:
            st.number_input("Transaction Costs (%)", key="tx_cost",
                help="Stamp duty + registration + brokerage on top of property price. Typically 6–8% in Mumbai.\nExample: 7.0")
            st.number_input("Required Cash Buffer (₹)", step=100_000, key="cash_buf",
                help="Minimum liquid savings you want to retain AFTER buying. Don't be left with zero.\nExample: ₹10L → enter 1000000")
            st.number_input("Buffer Inflation (%)", key="buf_infl",
                help="How fast your required cash buffer grows each year. Match to general inflation.\nExample: 6.0")

        section_header("📐", "Sq Ft Affordability")
        st.caption("Optional — enter your target home size to see affordable sq ft each year.")
        st.number_input("Target Home Size (sq ft)", min_value=0, step=50, key="target_sqft",
            help="How many sq ft is the home you want to buy?\n\n"
                 "Leave at 0 to skip this feature entirely.\n\n"
                 "When filled, the simulator derives the implied price per sq ft from your house price "
                 "(HousePrice ÷ TargetSqft) and inflates it each year. The 'Affordable Sq Ft' column "
                 "in Results then shows: (Portfolio + MaxLoan - CashBuffer) ÷ (inflated ₹/sq ft) — "
                 "i.e. the largest home you can afford that year at the prevailing market rate.\n\n"
                 "Example: If your target is an 800 sq ft flat, enter 800.")

    nav_buttons(0)

# ─────────────────────────────────────────────
# TAB 2
# ─────────────────────────────────────────────
elif _at == 1:
    tip("Tell the simulator how much you <strong>earn, spend, and save</strong> each month.")
    col1, col2 = st.columns(2, gap="large")

    with col1:
        section_header("💵", "Income & Taxes")
        c1,c2 = st.columns(2)
        with c1:
            st.number_input("Monthly Gross Income (₹)", step=10_000, key="income_0",
                help="Total monthly salary BEFORE deductions (CTC/12).\nExample: ₹18L CTC → enter 150000")
            st.number_input("Monthly Net Take-Home (₹)", step=10_000, key="net_0",
                help="Amount credited to your bank each month. Enter 0 to auto-compute from gross.\nExample: 110000")
        with c2:
            st.number_input("Income Growth Rate (%)", key="inc_growth",
                help="Expected annual salary increment including promotions.\nExample: 10.0")
            st.selectbox("Tax Regime", options=["new","old"],
                format_func=lambda x:"New Regime" if x=="new" else "Old Regime",
                key="tax_regime",
                help="New Regime: lower rates, fewer deductions.\nOld Regime: higher rates but allows HRA, 80C, home loan deductions.")

        with st.expander("⚙️  Advanced Tax Settings"):
            st.caption("Fill only for precise HRA exemption and NPS deduction calculation.")
            c1,c2 = st.columns(2)
            with c1:
                st.number_input("Basic Salary (₹/mo)", key="basic_m",
                    help="'Basic' component on your payslip. Typically 40–50% of gross.\nExample: 60000")
                st.number_input("HRA Received (₹/mo)", key="hra_m",
                    help="House Rent Allowance shown on payslip. Only relevant for Old Regime.\nExample: 20000")
                st.checkbox("Metro City?", key="metro",
                    help="Tick if you live in Mumbai, Delhi, Kolkata or Chennai. Affects HRA exemption (50% vs 40%).")
                st.number_input("Other 80C (₹/yr)", key="other_80c",
                    help="ELSS + PPF + LIC etc., max ₹1.5L. Only applies to Old Regime.\nExample: 100000")
            with c2:
                st.number_input("Employer NPS (₹/yr)", key="nps_ann",
                    help="Company NPS contribution. Deductible under 80CCD(2) in both regimes.\nExample: 72000")
                st.number_input("NPS % of Basic", key="nps_pct",
                    help="Employer NPS as % of basic (usually 10%). Use if you don't know the annual amount.\nExample: 10.0")
                st.number_input("Slab Inflation (%)", key="slab_infl",
                    help="Expected annual widening of tax slabs. Set 0 for conservative estimates.\nExample: 0.0")

        section_header("🎁", "Bonus & Variable Pay")
        st.caption("Annual bonus or variable pay — added to yearly investable surplus.")
        c1,c2,c3 = st.columns(3)
        with c1:
            st.number_input("Annual Bonus Net of Tax (₹)", key="bonus_0",
                help="Bonus you receive AFTER tax deduction (TDS already taken out by employer).\nExample: You get ₹2L gross, ₹60K tax deducted → enter 140000")
            st.radio("Bonus Mode", ["fixed","percent_of_gross"],
                format_func=lambda x:"Fixed ₹" if x=="fixed" else "% of Gross",
                key="bonus_mode", horizontal=True,
                help="Fixed: same rupee amount each year (grown by Bonus Growth %).\n% of Gross: bonus = X% of annual gross salary.")
        with c2:
            st.number_input("Bonus Growth (%/yr)", key="bonus_gr",
                help="How fast your bonus grows each year.\nExample: 8.0")
            st.checkbox("Bonus is Gross (deduct tax)", key="bonus_gross",
                help="Check if the amount above is pre-tax. The simulator will deduct income tax at your effective rate.")
        with c3:
            st.number_input("Bonus Savings (%)", key="bonus_sav_pct",
                help="What % of bonus do you actually invest/save?\nExample: 80.0 if you save 80% and spend 20%.")

    with col2:
        section_header("🛒", "Expenses & Rent")
        st.radio("Expense Mode", ["fraction","absolute"],
            format_func=lambda x:"% of Take-Home" if x=="fraction" else "Fixed ₹ Amount",
            key="exp_mode", horizontal=True,
            help="% of Take-Home: expenses grow with salary.\nFixed ₹: you name a fixed amount that grows with Expense Inflation.")
        c1,c2 = st.columns(2)
        with c1:
            st.number_input("Expenses (% of Take-Home)", key="exp_frac",
                help="Monthly living costs as % of salary. Exclude rent — that's below.\nExample: 45.0")
            st.number_input("Fixed Expenses (₹/mo)", key="exp_abs",
                help="Used only in Fixed ₹ mode. Today's monthly spend excluding rent.\nExample: 45000")
        with c2:
            st.number_input("Expense Inflation (%)", key="exp_infl",
                help="How fast your fixed expenses rise per year.\nExample: 6.0")
            st.number_input("Current Rent (₹/mo)", key="rent_0",
                help="Monthly rent you pay today. Subtracted from income as a separate expense.\nExample: 25000")
            st.number_input("Rent Inflation (%)", key="rent_infl",
                help="How fast rent increases each year. Typically 8–10% in Indian cities.\nExample: 8.0")

    nav_buttons(1)

# ─────────────────────────────────────────────
# TAB 3
# ─────────────────────────────────────────────
elif _at == 2:
    tip("Define your <strong>current investments</strong>, how they grow, rebalancing rules, and home loan eligibility.")

    section_header("📂", "Investment Accounts / Assets")
    st.caption("List every investment account. Each row = one asset. The simulator grows it year by year.")
    with st.expander("❓ Column guide", expanded=False):
        st.markdown("""
| Column | What to enter | Example |
|--------|--------------|---------|
| **Asset Class** | Any name | "Equity MF", "PPF", "EPF" |
| **Opening Value (₹)** | Current balance | 500000 |
| **Monthly Contribution (₹)** | SIP or regular deposit | 20000 |
| **Annual Return (%)** | Expected average yearly return | 12% equity, 7.1% PPF |
| **Stepup Type** | How SIP grows — Percentage or Fixed | Percentage |
| **Stepup Value** | Growth per year | 5 → 5% more SIP each year |
| **Surplus Allocation %** | Share of leftover surplus invested here | 100 |
| **External Funding?** | Tick for employer-funded assets (EPF) | ✅ |
| **Tax Treatment** | How returns are taxed | Equity → Taxed at fixed rate |
| **Fixed Tax %** | Rate if Taxed at fixed rate | 12.5 (LTCG equity) |
        """)

    edited_assets_df = st.data_editor(
        st.session_state['assets_table'], num_rows="dynamic",
        use_container_width=True, key="assets_ui",
        column_config={
            "Stepup_type": st.column_config.SelectboxColumn(
                "Stepup Type", options=["Percentage","Fixed"], required=True),
            "Invest_above_Surplus_Cash": st.column_config.CheckboxColumn(
                "External Funding?",
                help="Tick for employer-funded assets (e.g. EPF). Not counted against monthly surplus."),
            "Tax_Treatment": st.column_config.SelectboxColumn(
                "Tax Treatment",
                options=["Exempt","Taxed at slab rate","Taxed at fixed rate"], required=True),
            "Fixed_Tax_Pct": st.column_config.NumberColumn(
                "Fixed Tax %", min_value=0., max_value=100.,
                help="Leave blank unless 'Taxed at fixed rate'. For equity LTCG enter 12.5.")
        }
    )
    st.session_state['assets_table'] = edited_assets_df

    c1,c2 = st.columns(2)
    c1.metric("Total Opening Balance",
              f"₹ {sum(r.get('Opening_Value',0.) for _,r in edited_assets_df.iterrows()):,.0f}")
    c2.metric("Total Monthly SIPs",
              f"₹ {sum(r.get('monthly_contribution',0.) for _,r in edited_assets_df.iterrows()):,.0f}")

    asset_names = edited_assets_df["Asset_Class"].dropna().unique().tolist()
    st.divider()

    # ── Return reallocation ──
    section_header("🔄", "Return Reallocation Rules")
    st.caption("Redirect an asset's annual returns into a different asset. Rules per source must sum to 100%.")
    edited_reinvest_df = st.data_editor(
        st.session_state['reinvest_table'], num_rows="dynamic",
        use_container_width=True, key="reinvest_ui",
        column_config={
            "Source_Asset": st.column_config.SelectboxColumn(
                "Source Asset", options=asset_names, required=True),
            "Destination_Asset": st.column_config.SelectboxColumn(
                "Destination Asset", options=asset_names, required=True),
            "Allocation_Pct": st.column_config.NumberColumn(
                "Allocation %", min_value=0., max_value=100., required=True)
        }
    )
    st.session_state['reinvest_table'] = edited_reinvest_df
    st.divider()

    # ── Flexible rebalancing ──
    section_header("⚖️", "Portfolio Rebalancing Rules")
    st.markdown("""
<div class="rb-help">
<b>Trigger Types:</b><br>
&nbsp;&nbsp;• <b>One-Time</b> — fires once at Start Age. <i>E.g. at age 45 move 30% of Equity → Debt.</i><br>
&nbsp;&nbsp;• <b>Annual</b> — fires every year from Start Age to End Age. <i>E.g. every year 50–60, move ₹5L Equity → FD.</i><br>
&nbsp;&nbsp;• <b>Every N Years</b> — fires periodically. Set Frequency. <i>E.g. every 3 years from age 40, rebalance 20% to Equity.</i><br>
&nbsp;&nbsp;• <b>Balance Threshold</b> — fires whenever Threshold Asset ≥ Threshold Amount. <i>E.g. when Equity crosses ₹50L, move 20% → Debt.</i><br><br>
<b>Transfer Type:</b> Percentage = X% of source balance. Absolute ₹ = fixed rupee amount.<br>
<b>Threshold Asset / Amount</b>: only for Balance Threshold — leave blank for other types.
</div>
""", unsafe_allow_html=True)

    edited_rebalance_df = st.data_editor(
        st.session_state['rebalance_table'], num_rows="dynamic",
        use_container_width=True, key="rebalance_ui",
        column_config={
            "Trigger_Type": st.column_config.SelectboxColumn(
                "Trigger Type",
                options=["One-Time","Annual","Every N Years","Balance Threshold"],
                required=True,
                help="One-Time: once at Start Age.\nAnnual: every year Start→End.\nEvery N Years: periodic.\nBalance Threshold: when watched asset crosses a value."),
            "Source_Asset": st.column_config.SelectboxColumn(
                "Source Asset", options=asset_names, required=True),
            "Destination_Asset": st.column_config.SelectboxColumn(
                "Destination Asset", options=asset_names, required=True),
            "Transfer_Type": st.column_config.SelectboxColumn(
                "Transfer Type", options=["Percentage","Absolute ₹"], required=True),
            "Value": st.column_config.NumberColumn("Amount / %", min_value=0., required=True,
                help="Percentage: enter 20 for 20%. Absolute ₹: enter 500000 for ₹5L."),
            "Start_Age": st.column_config.NumberColumn("Start Age", min_value=18, max_value=100,
                help="Age at which this rule starts (or fires for One-Time)."),
            "End_Age": st.column_config.NumberColumn("End Age", min_value=18, max_value=100,
                help="Last age for Annual / Every N Years. Leave blank = end of simulation."),
            "Frequency_Years": st.column_config.NumberColumn("Every N Yrs", min_value=1, max_value=50,
                help="For 'Every N Years' only: gap between transfers. E.g. 3 = every 3 years."),
            "Threshold_Asset": st.column_config.SelectboxColumn(
                "Threshold Asset", options=[""]+asset_names,
                help="Balance Threshold only: which asset to watch."),
            "Threshold_Amount": st.column_config.NumberColumn("Threshold ₹", min_value=0.,
                help="Balance Threshold only: the balance level that triggers the transfer."),
        }
    )
    st.session_state['rebalance_table'] = edited_rebalance_df
    st.divider()

    # ── Loan ──
    section_header("🏦", "Home Loan Constraints")
    st.checkbox("Enable Home Loan Financing", key="loan_enabled",
        help="Uncheck for full cash purchase.")
    if st.session_state.loan_enabled:
        c1,c2,c3 = st.columns(3)
        with c1:
            st.number_input("Interest Rate (%)", key="loan_rate",
                help="Expected home loan rate. Current range 8.5–9.5%.\nExample: 8.75")
        with c2:
            st.number_input("Tenure (Years)", key="loan_tenure",
                help="Loan repayment period. Typically 15–25 years.\nExample: 20")
        with c3:
            st.number_input("Bank Eligibility Multiplier", key="bank_mult",
                help="Max loan = this × monthly gross. Banks typically use 55–65×.\nExample: 60")
        st.radio("EMI Limit Mode", ["fraction","fixed"],
            format_func=lambda x:"% of Take-Home" if x=="fraction" else "Fixed ₹ Amount",
            key="emi_mode", horizontal=True)
        c1,c2,c3 = st.columns(3)
        with c1:
            st.number_input("Max EMI (% of Take-Home)", key="emi_frac",
                help="EMI cap as % of monthly salary. Advisors recommend ≤40–45%.\nExample: 40.0")
        with c2:
            st.number_input("Fixed EMI Limit (₹/mo)", key="emi_fixed",
                help="Used when Fixed ₹ mode is selected.\nExample: 60000")
        with c3:
            st.number_input("EMI Safety Buffer (%)", key="emi_buf",
                help="Conservative haircut on EMI capacity. E.g. 10% → effective limit = 90% of max EMI.\nExample: 10.0")
        st.number_input("Max Loan I Want (₹) — 0 for no cap", key="user_max_loan",
            help="Hard cap on borrowing regardless of bank eligibility. Enter 0 to let bank limit apply.\nExample: 10000000")

    nav_buttons(2)

# ─────────────────────────────────────────────
# TAB 4 — Results
# ─────────────────────────────────────────────
elif _at == 3:
    tip("Click <strong>▶ Run Simulation</strong> to get your year-by-year forecast and earliest affordable age.")

    # Validation
    ok = True
    if not edited_reinvest_df.empty:
        for src, tot in edited_reinvest_df.groupby("Source_Asset")["Allocation_Pct"].sum().items():
            if abs(tot-100.)>0.001:
                st.error(f"🛑 Reallocation rules for **'{src}'** sum to {tot:.1f}% — must equal 100%.")
                ok = False
    if not ok: st.stop()

    # Build asset_classes
    asset_classes = []
    for _, row in edited_assets_df.iterrows():
        asset_classes.append({
            "name": row.get("Asset_Class","Asset"),
            "initial_value": row.get("Opening_Value",0.),
            "monthly_contribution": row.get("monthly_contribution",0.),
            "annual_return": row.get("Annual Return",0.)/100.,
            "stepup_type": "pct" if row.get("Stepup_type")=="Percentage" else "fixed",
            "stepup_value": row.get("Stepup_Value",0.),
            "surplus_alloc_pct": row.get("Surplus_Allocation_Percentage",0.),
            "invest_above_surplus": row.get("Invest_above_Surplus_Cash",False),
            "tax_treatment": row.get("Tax_Treatment","Exempt"),
            "fixed_tax_pct": (float(row.get("Fixed_Tax_Pct") or 0.))/100.
        })

    reinvest_rules   = edited_reinvest_df.to_dict(orient='records')
    rebalance_df_run = edited_rebalance_df.copy()

    params = {
        'age': st.session_state.age,
        'max_years': st.session_state.max_age - st.session_state.age,
        'house_price': st.session_state.house_price,
        'house_infl': st.session_state.house_infl/100.,
        'tx_cost': st.session_state.tx_cost/100.,
        'cash_buf': st.session_state.cash_buf,
        'buf_infl': st.session_state.buf_infl/100.,
        'income_0': st.session_state.income_0,
        'net_0': st.session_state.net_0,
        'inc_growth': st.session_state.inc_growth/100.,
        'tax_regime': st.session_state.tax_regime,
        'basic_m': st.session_state.basic_m,
        'hra_m': st.session_state.hra_m,
        'metro': st.session_state.metro,
        'bonus_0': st.session_state.bonus_0,
        'bonus_mode': st.session_state.bonus_mode,
        'bonus_gross': st.session_state.bonus_gross,
        'bonus_gr': st.session_state.bonus_gr/100.,
        'bonus_sav_pct': st.session_state.bonus_sav_pct,
        'other_80c': st.session_state.other_80c,
        'nps_ann': st.session_state.nps_ann,
        'nps_pct': st.session_state.nps_pct,
        'slab_infl': st.session_state.slab_infl/100.,
        'exp_mode': st.session_state.exp_mode,
        'exp_frac': st.session_state.exp_frac/100.,
        'exp_abs': st.session_state.exp_abs,
        'exp_infl': st.session_state.exp_infl/100.,
        'rent_0': st.session_state.rent_0,
        'rent_infl': st.session_state.rent_infl/100.,
        'loan_enabled': st.session_state.loan_enabled,
        'loan_rate': st.session_state.loan_rate/100.,
        'loan_tenure': st.session_state.loan_tenure,
        'bank_mult': st.session_state.bank_mult,
        'emi_mode': st.session_state.emi_mode,
        'emi_frac': st.session_state.emi_frac/100.,
        'emi_fixed': st.session_state.emi_fixed,
        'emi_buf': st.session_state.emi_buf/100.,
        'user_max_loan': st.session_state.user_max_loan,
        'target_sqft': st.session_state.target_sqft
    }

    col_btn, _ = st.columns([1,3])
    with col_btn:
        run_clicked = st.button("▶  Run Simulation", type="primary", use_container_width=True)

    if run_clicked:
        with st.spinner("Running simulation…"):
            results, over_details, under_details = run_affordability(
                params, asset_classes, reinvest_rules, rebalance_df_run)
        st.session_state['sim_results'] = (results, over_details, under_details)

    if st.session_state['sim_results'] is not None:
        results, over_details, under_details = st.session_state['sim_results']
        df_res = pd.DataFrame(results)
        aff_rows = df_res[df_res['Affordable']=="YES ✓"]
        show_sqft = st.session_state.target_sqft > 0

        # ── Result banner ──
        if not aff_rows.empty:
            first = aff_rows.iloc[0]
            sqft_note = f" &nbsp;·&nbsp; Aff. Area: {first['Aff_Sqft']:,.0f} sq ft" if show_sqft else ""
            st.markdown(f"""
            <div class="result-banner success">
                <div class="emoji">🎉</div>
                <div>
                    <div class="title">Earliest Affordable Age: {int(first['Age'])}</div>
                    <div class="sub">
                        Portfolio: ₹{first['Portfolio']:,.0f} &nbsp;·&nbsp;
                        House Price: ₹{first['HousePrice']:,.0f} &nbsp;·&nbsp;
                        Max Loan: ₹{first['MaxLoan']:,.0f} &nbsp;·&nbsp;
                        EMI: ₹{first['EffEMI']:,.0f}/mo{sqft_note}
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-banner failure">
                <div class="emoji">❌</div>
                <div>
                    <div class="title">Not affordable by age {st.session_state.max_age}</div>
                    <div class="sub">Consider increasing income growth, reducing expenses, or adjusting loan parameters.</div>
                </div>
            </div>""", unsafe_allow_html=True)

        # ── KPI row ──
        last = df_res.iloc[-1]
        ys = st.session_state.max_age - st.session_state.age
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card blue">
                <div class="label">Final Portfolio (Age {st.session_state.max_age})</div>
                <div class="value">₹{last['Portfolio']/1e7:.2f} Cr</div>
                <div class="delta">across {ys} years</div>
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
                <div class="value">{len(aff_rows)}</div>
                <div class="delta">years out of {ys+1}</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # ── Warnings ──
        if over_details:
            msg = "**⚠️ Budget Deficit:** SIPs exceed surplus — "
            msg += ", ".join([f"Age {a} (₹{v:,.0f})" for a,v in over_details[:5]])
            if len(over_details)>5: msg += f" +{len(over_details)-5} more"
            st.error(msg)
        if under_details:
            msg = "**ℹ️ Unallocated Surplus:** "
            msg += ", ".join([f"Age {a} (₹{v:,.0f})" for a,v in under_details[:5]])
            if len(under_details)>5: msg += f" +{len(under_details)-5} more"
            st.warning(msg)

        # ── Save this run banner ──
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df_res.to_excel(writer, sheet_name='Simulation Results', index=False)

        st.markdown("""
        <div class="save-banner">
            <div class="sb-text">
                <div class="sb-title">💾 Want to save this run?</div>
                <div class="sb-sub">Download the Excel file to keep a record of this scenario —
                useful for comparing different salary or investment assumptions later,
                or to share with your financial advisor.</div>
            </div>
        </div>""", unsafe_allow_html=True)
        col_dl, col_sc, _ = st.columns([1,1,2])
        with col_dl:
            st.download_button(
                "📥 Download Results (Excel)",
                data=excel_buffer.getvalue(),
                file_name="house_affordability_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        with col_sc:
            st.download_button(
                "📤 Save Scenario (JSON)",
                data=_export_json,
                file_name="house_scenario.json",
                mime="application/json",
                use_container_width=True,
                help="Saves all your input settings so you can reload them later and re-run with tweaks.")

        # ── Table ──
        section_header("📋", "Year-by-Year Breakdown")

        def color_aff(val):
            if val=="YES ✓": return 'background-color:rgba(34,197,94,.15);color:#166534;font-weight:700;'
            return 'color:#64748b;'

        fmt = {
            'TakeHome/mo':'₹{:,.0f}','Surplus/yr':'₹{:,.0f}',
            'Portfolio':'₹{:,.0f}','HousePrice':'₹{:,.0f}',
            'MaxLoan':'₹{:,.0f}','CashLeft':'₹{:,.0f}',
            'EffEMI':'₹{:,.0f}','AffEMI':'₹{:,.0f}',
            'Tax%':'{:.1f}%','Eff_Return%':'{:.1f}%'
        }
        if show_sqft: fmt['Aff_Sqft'] = '{:,.0f} sq ft'

        disp = df_res if show_sqft else df_res.drop(columns=['Aff_Sqft'], errors='ignore')
        styled = (disp.style
                  .format({k:v for k,v in fmt.items() if k in disp.columns})
                  .map(color_aff, subset=['Affordable']))

        st.dataframe(styled, use_container_width=True, height=540,
            column_config={
                "Portfolio_Breakdown": st.column_config.TextColumn(
                    "Portfolio Breakdown", width="large",
                    help="Asset balances after rebalancing for this year."),
                "Aff_Sqft": st.column_config.NumberColumn(
                    "Affordable Sq Ft", format="%d sq ft",
                    help="Largest home (sq ft) you can buy this year while passing all 3 tests: "
                         "total funding ≥ outlay, cash left ≥ buffer, EMI ≤ limit. "
                         "0 means none of the tests pass at any size.")
            })
