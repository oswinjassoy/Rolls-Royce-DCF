# Rolls-Royce DCF Valuation Dashboard

An interactive Streamlit DCF model for Rolls-Royce Holdings plc (LSE: RR.). Built as a finance portfolio project to demonstrate forecasting, WACC, enterprise-to-equity value bridging, and sensitivity analysis.

## Status and integrity notes

- Historical financial data currently includes FY2024 and FY2025 only, drawn from Rolls-Royce's official FY2025 results.
- FY2025 statutory revenue (£21.207bn), statutory operating profit (£4.468bn), net cash (£1.895bn), statutory operating cash flow (£4.565bn), capex (£0.978bn) and D&A/impairment (£0.737bn) are sourced reported figures.
- Underlying free cash flow (£3.270bn in 2025; £2.425bn in 2024) is an alternative performance measure and is kept separate from statutory cash flow. It is **not** used as FCFF in the DCF.
- Forecast assumptions and WACC inputs are illustrative and editable, not company guidance or verified market estimates.
- Share price is a dated snapshot from the Financial Times (1,249.80p at 10:46 BST on 27 October 2026, delayed at least 20 minutes), not a live feed.
- Shares outstanding is an approximate starting point that must be verified against the latest filing before relying on per-share output.
- Net cash is FY2025 year-end reported data; update for newer financial statements and consider pension, lease, minority-interest and other adjustments in a more advanced bridge.
- The model does not automatically fetch data. It avoids inventing missing historical periods.

## Mac setup

Open the `rolls-royce-dcf` folder in Cursor (normal editor/terminal only; no Cursor AI needed).

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest -q
streamlit run app.py
```

If `python3` is missing or too old, install a current Python 3 version from https://www.python.org/downloads/macos/ and repeat. The project does not touch the separate `Portfolio-risk-dashboard` folder.

## Model methodology

All monetary values in calculations are £bn; share count is billions.

- Revenue forecast: prior-year revenue × (1 + growth assumption).
- EBIT: revenue × EBIT margin.
- Cash tax: max(0, EBIT × cash tax rate).
- D&A and capex: revenue × their respective assumptions.
- Change in NWC: change in revenue × NWC assumption (% of incremental revenue).
- FCFF: EBIT − cash tax + D&A − capex − change in NWC.
- Cost of equity: risk-free rate + beta × equity risk premium (CAPM).
- WACC: equity weight × cost of equity + debt weight × pre-tax cost of debt × (1 − tax rate).
- Terminal value: final forecast FCFF × (1 + terminal growth) / (WACC − terminal growth).
- Enterprise value: PV of forecast FCFF + PV of terminal value.
- Equity value: enterprise value + net cash (simplified bridge).
- Implied value per share: equity value / shares outstanding × 100 to convert pounds to pence.

The first forecast year is 2026 following FY2025 reported financials. Mid-year discounting is not used. WACC must exceed terminal growth.

## Sources

1. Rolls-Royce, FY2025 full-year results, published 26 February 2026: https://www.rolls-royce.com/investors/results-reports-and-presentations/financial-results/rr-holdings-plc-2025-full-year-results.aspx
2. Financial Times, RR. historical quote: https://markets.ft.markitdigital.com/data/equities/tearsheet/historical?s=RR.%3ALSE

## Limitations / next improvements

1. Extend audited history from official annual reports and preserve statutory vs underlying definitions.
2. Source and date each market input (UK gilt yield, ERP, beta, debt cost, capital structure) rather than treating the sidebar defaults as sourced.
3. Verify latest diluted shares outstanding and the full enterprise-to-equity bridge.
4. Reconcile FCFF inputs to statutory cash flow and balance sheet definitions, including cash taxes and working capital.
5. Add automated data-refresh with source validation only after deciding on a reliable data provider.
6. Add a company-results/annual-report source log and model versioning.

## Disclaimer

Educational and portfolio use only. A DCF is sensitive to assumptions and is not investment advice or a recommendation to buy or sell securities.
