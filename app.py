from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dcf_model import build_forecast, calculate_dcf, sensitivity_table, wacc_calculation

st.set_page_config(page_title="Rolls-Royce | DCF Valuation", page_icon="✈️", layout="wide")
st.markdown("""<style>
.stApp {background:#0b1220;color:#e8edf5}.block-container{padding-top:1.7rem;max-width:1500px}
[data-testid="stMetric"]{background:#121d30;border:1px solid #24344d;padding:16px;border-radius:12px}
[data-testid="stSidebar"]{background:#101a2b}.rr-muted{color:#9eacc2;font-size:.9rem}
.rr-title{font-size:2rem;font-weight:700;letter-spacing:-.03em}.rr-pill{display:inline-block;padding:4px 9px;border-radius:99px;background:#26364c;color:#b8c9df;font-size:.8rem}
</style>""", unsafe_allow_html=True)

ROOT = Path(__file__).parent
hist = pd.read_csv(ROOT / "data" / "historical_financials.csv")
latest = hist.loc[hist.year == hist.year.max()].iloc[0]

st.markdown('<div class="rr-muted">EQUITY RESEARCH • VALUATION WORKBENCH</div>', unsafe_allow_html=True)
st.markdown('<div class="rr-title">Rolls-Royce Holdings plc</div>', unsafe_allow_html=True)
st.caption("LSE: RR. • Discounted cash flow valuation • All financial figures in £bn unless stated otherwise")
st.warning("Research prototype: historical inputs below are sourced, but forecast and WACC inputs are editable analyst assumptions. This is an analytical estimate, not investment advice.")

with st.sidebar:
    st.header("Model assumptions")
    st.caption("These are illustrative starting assumptions, not company guidance or verified market estimates.")
    st.subheader("Operating forecast")
    growth = st.slider("Revenue growth (%)", -5.0, 20.0, 6.0, 0.5) / 100
    margin = st.slider("EBIT margin (%)", 5.0, 30.0, 18.0, 0.5) / 100
    tax = st.slider("Cash tax rate (%)", 0.0, 35.0, 25.0, 0.5) / 100
    da_pct = st.slider("D&A / revenue (%)", 1.0, 8.0, 3.5, 0.25) / 100
    capex_pct = st.slider("Capex / revenue (%)", 1.0, 10.0, 4.5, 0.25) / 100
    nwc_pct = st.slider("Change in NWC / incremental revenue (%)", -10.0, 20.0, 3.0, 0.5) / 100
    st.subheader("WACC assumptions")
    rf = st.slider("Risk-free rate (%)", 0.0, 8.0, 4.5, 0.1) / 100
    erp = st.slider("Equity risk premium (%)", 2.0, 8.0, 5.0, 0.1) / 100
    beta = st.slider("Levered beta", 0.5, 2.5, 1.3, 0.05)
    cost_debt = st.slider("Pre-tax cost of debt (%)", 1.0, 12.0, 5.0, 0.1) / 100
    equity_weight = st.slider("Equity weight (%)", 50.0, 100.0, 90.0, 1.0) / 100
    st.subheader("Valuation bridge")
    net_cash = st.number_input("Net cash (£bn; FY2025 reported)", min_value=-20.0, max_value=30.0, value=float(latest.net_cash_bn), step=0.1)
    shares = st.number_input("Shares outstanding (bn; verify)", min_value=1.0, max_value=20.0, value=8.21, step=0.01, help="Illustrative third-party reported figure; verify latest issued share count before relying on per-share output.")
    share_price = st.number_input("Share price (pence; dated market snapshot)", min_value=0.0, max_value=10000.0, value=1249.8, step=1.0, help="FT snapshot: 1,249.80p, 27 Oct 2026 at 10:46 BST; delayed data, not a live feed.")
    terminal_growth = st.slider("Terminal growth (%)", 0.0, 4.0, 2.0, 0.25) / 100

wacc, coe = wacc_calculation(rf, erp, beta, cost_debt, tax, equity_weight)
if wacc <= terminal_growth:
    st.error("WACC must be greater than terminal growth for the perpetual-growth DCF. Adjust assumptions in the sidebar.")
    st.stop()
forecast = build_forecast(float(latest.revenue_bn), growth, margin, tax, da_pct, capex_pct, nwc_pct, years=5)
valuation = calculate_dcf(forecast, wacc, terminal_growth, net_cash, shares)
valuation["upside_pct"] = (valuation["value_per_share_pence"] / share_price - 1) * 100 if share_price > 0 else float("nan")

m1,m2,m3,m4 = st.columns(4)
m1.metric("Implied value / share", f"{valuation['value_per_share_pence']:,.0f}p", f"{valuation['upside_pct']:+.1f}% vs snapshot")
m2.metric("Enterprise value", f"£{valuation['enterprise_value_bn']:,.1f}bn")
m3.metric("Equity value", f"£{valuation['equity_value_bn']:,.1f}bn")
m4.metric("Model WACC", f"{wacc:.2%}")
st.caption(f"Market comparison snapshot: {share_price:,.1f}p (27 Oct 2026, 10:46 BST; delayed FT data). Valuation date: 27 October 2026. Inputs are not refreshed automatically.")

tab1,tab2,tab3,tab4 = st.tabs(["Overview", "Forecast & DCF", "Sensitivity", "Sources & methodology"])
with tab1:
    st.subheader("Company financial snapshot")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("FY2025 statutory revenue", f"£{latest.revenue_bn:.3f}bn")
    c2.metric("FY2025 statutory operating profit", f"£{latest.operating_profit_bn:.3f}bn")
    c3.metric("FY2025 statutory net cash", f"£{latest.net_cash_bn:.3f}bn")
    c4.metric("FY2025 underlying free cash flow", f"£{latest.underlying_fcf_bn:.3f}bn")
    st.markdown("**Historical revenue and operating profit**")
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Statutory revenue", x=hist.year.astype(str), y=hist.revenue_bn, marker_color="#5b8def"))
    fig.add_trace(go.Bar(name="Statutory operating profit", x=hist.year.astype(str), y=hist.operating_profit_bn, marker_color="#40c6a3"))
    fig.update_layout(barmode="group", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis_title="£bn", legend_orientation="h")
    st.plotly_chart(fig, use_container_width=True)
    st.info("Only FY2024–FY2025 have been loaded in this initial build. The company’s underlying free cash flow is a non-IFRS performance measure and is not interchangeable with statutory operating cash flow or FCFF.")
    st.subheader("Key valuation drivers")
    st.markdown(f"- **Revenue growth:** {growth:.1%} annually; each forecast year compounds from prior-year revenue.\n- **Operating margin:** held at {margin:.1%} for all forecast years.\n- **WACC:** {wacc:.2%}, using CAPM cost of equity ({coe:.2%}) and an assumed capital structure.\n- **Terminal growth:** {terminal_growth:.2%}; must remain below WACC.\n- **Main risks:** civil aerospace aftermarket demand and flying hours, engine programme execution, defence spending, supply-chain capacity, FX/hedging, working-capital volatility and long-run terminal assumptions.")
with tab2:
    st.subheader("Five-year unlevered free cash flow forecast")
    
    
display = forecast.copy()

percent_cols = ["revenue_growth_pct", "ebit_margin_pct"]

for col in percent_cols:
    if col in display.columns:
        display[col] = display[col].map(lambda x: f"{x:.1%}")

money_cols = [
    "revenue_bn", "ebit_bn", "cash_tax_bn",
    "da_bn", "capex_bn", "change_nwc_bn", "ufcf_bn"
]

for col in money_cols:
    if col in display.columns:
        display[col] = display[col].map(lambda x: f"£{x:.3f}")

st.dataframe(display, use_container_width=True, hide_index=True)
fig = px.line(forecast, x="year", y="ufcf_bn", markers=True, template="plotly_dark", labels={"year":"Fiscal year","ufcf_bn":"Unlevered free cash flow (£bn)"})
fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)
st.subheader("DCF valuation bridge")
bridge = pd.DataFrame({"Component":["PV of forecast UFCF","PV of terminal value","Enterprise value","Net cash adjustment","Equity value"],"£bn":[valuation["pv_forecast_bn"],valuation["pv_terminal_bn"],valuation["enterprise_value_bn"],net_cash,valuation["equity_value_bn"]]})
st.dataframe(bridge.round(3), use_container_width=True, hide_index=True)
st.markdown("**Core formulas**")
st.latex(r"FCFF = EBIT(1-T) + D\&A - CapEx - \Delta NWC")
st.latex(r"TV_5 = \frac{FCFF_5(1+g)}{WACC-g}")
st.latex(r"EV = \sum_{t=1}^{5}\frac{FCFF_t}{(1+WACC)^t}+\frac{TV_5}{(1+WACC)^5}")
st.latex(r"Equity\ Value = EV + Net\ Cash;\quad Value/Share = Equity\ Value / Shares")
with tab3:
    st.subheader("WACC vs terminal growth")
    waccs = [max(wacc - .02, terminal_growth + .005), max(wacc - .01, terminal_growth + .005), wacc, wacc + .01, wacc + .02]
    gs = sorted(set([max(0, terminal_growth - .01), max(0, terminal_growth - .005), terminal_growth, terminal_growth + .005, terminal_growth + .01]))
    sens = sensitivity_table(forecast, waccs, gs, net_cash, shares)
    sens_fmt = sens.copy()
    sens_fmt.columns = [f"g={x:.2%}" for x in sens_fmt.columns]
    sens_fmt.index = [f"WACC={x:.2%}" for x in sens_fmt.index]
    st.dataframe(sens_fmt.style.format("{:.0f}p"), use_container_width=True)
    heat = go.Figure(data=go.Heatmap(z=sens.values, x=[f"{g:.2%}" for g in gs], y=[f"{w:.2%}" for w in waccs], colorscale="RdYlGn", colorbar={"title":"pence/share"}, text=[[f"{v:.0f}p" for v in row] for row in sens.values], texttemplate="%{text}"))
    heat.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Terminal growth", yaxis_title="WACC")
    st.plotly_chart(heat, use_container_width=True)
    st.subheader("Illustrative operating scenarios")
    scenarios = {"Bear": (growth - .03, margin - .03), "Base": (growth, margin), "Bull": (growth + .03, margin + .03)}
    rows=[]
    for name,(g,m) in scenarios.items():
        sf=build_forecast(float(latest.revenue_bn),g,m,tax,da_pct,capex_pct,nwc_pct,years=5)
        sv=calculate_dcf(sf,wacc,terminal_growth,net_cash,shares)
        rows.append({"Scenario":name,"Revenue growth":g,"EBIT margin":m,"Implied value/share (p)":sv["value_per_share_pence"]})
    scen=pd.DataFrame(rows)
    scen["Revenue growth"]=scen["Revenue growth"].map(lambda x:f"{x:.1%}")
    scen["EBIT margin"]=scen["EBIT margin"].map(lambda x:f"{x:.1%}")
    scen["Implied value/share (p)"]=scen["Implied value/share (p)"].map(lambda x:f"{x:,.0f}p")
    st.dataframe(scen, use_container_width=True, hide_index=True)
with tab4:
    st.subheader("Verified historical inputs")
    st.dataframe(hist, use_container_width=True, hide_index=True)
    st.markdown("**Primary source — Rolls-Royce FY2025 full-year results (26 February 2026)**")
    st.markdown("[Official results and financial tables](https://www.rolls-royce.com/investors/results-reports-and-presentations/financial-results/rr-holdings-plc-2025-full-year-results.aspx)")
    st.markdown("FY2025 statutory revenue £21.207bn, statutory operating profit £4.468bn, statutory cash flows from operating activities £4.565bn, capex £0.978bn, D&A and impairment £0.737bn and net cash £1.895bn. FY2025 underlying FCF £3.270bn is shown separately and is not used as FCFF.")
    st.markdown("**Market snapshot**")
    st.markdown("[Financial Times RR. quote](https://markets.ft.markitdigital.com/data/equities/tearsheet/historical?s=RR.%3ALSE) — 1,249.80p at 10:46 BST on 27 October 2026; data delayed at least 20 minutes. The sidebar value is a dated snapshot, not a live market feed.")
    st.markdown("**Assumptions requiring verification before investment use**")
    st.markdown("- Risk-free rate, equity risk premium, beta, pre-tax cost of debt and capital structure weights are illustrative analyst inputs, not claimed as sourced live market inputs.\n- Forecast growth, EBIT margin, cash tax, D&A, capex, working-capital assumptions and terminal growth are editable assumptions.\n- Shares outstanding is an approximate third-party starting point and must be checked against latest company filings.\n- Net cash is the FY2025 reported figure; refresh it for later reporting periods and review pension, leases, minorities and other non-operating adjustments before relying on the equity bridge.\n- A rigorous FCFF model should reconcile tax to operating profit and working-capital movements to the relevant cash-flow definitions. This simplified first version uses a transparent forecast-driver approach.")
    st.markdown("**Data limitations**")
    st.write("The app currently ships with two years of verified historical figures rather than filling gaps with fabricated history. No live financial-data API or automated source refresh is configured.")

st.divider()
st.caption("For educational and portfolio purposes only. DCF output is highly sensitive to assumptions and is not a recommendation to buy or sell securities.")
