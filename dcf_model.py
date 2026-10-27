"""Transparent DCF calculations. Monetary values are £bn; shares are billions."""
import pandas as pd


def wacc_calculation(risk_free_rate, equity_risk_premium, beta, pre_tax_cost_of_debt, tax_rate, equity_weight):
    values = [risk_free_rate, equity_risk_premium, beta, pre_tax_cost_of_debt, tax_rate, equity_weight]
    if any(v is None for v in values):
        raise ValueError("WACC inputs cannot be missing")
    if not (0 <= risk_free_rate <= 1 and 0 <= equity_risk_premium <= 1 and beta >= 0 and 0 <= pre_tax_cost_of_debt <= 1 and 0 <= tax_rate <= 1 and 0 <= equity_weight <= 1):
        raise ValueError("Invalid WACC input range")
    debt_weight = 1 - equity_weight
    cost_of_equity = risk_free_rate + beta * equity_risk_premium
    wacc = equity_weight * cost_of_equity + debt_weight * pre_tax_cost_of_debt * (1 - tax_rate)
    return wacc, cost_of_equity


def build_forecast(base_revenue_bn, revenue_growth, ebit_margin, tax_rate, da_pct_revenue, capex_pct_revenue, nwc_pct_incremental_revenue, years=5, start_year=2026):
    if base_revenue_bn <= 0 or years < 1:
        raise ValueError("Base revenue must be positive and years must be at least one")
    if not (0 <= tax_rate <= 1 and 0 <= ebit_margin <= 1):
        raise ValueError("Tax rate and EBIT margin must be between 0 and 100%")
    if revenue_growth <= -1:
        raise ValueError("Revenue growth must be greater than -100%")
    rows=[]
    previous_revenue = float(base_revenue_bn)
    for i in range(1, years + 1):
        revenue = previous_revenue * (1 + revenue_growth)
        ebit = revenue * ebit_margin
        tax = max(0.0, ebit * tax_rate)
        da = revenue * da_pct_revenue
        capex = revenue * capex_pct_revenue
        delta_nwc = (revenue - previous_revenue) * nwc_pct_incremental_revenue
        ufcf = ebit - tax + da - capex - delta_nwc
        rows.append({"year": start_year + i - 1, "revenue_bn": revenue, "revenue_growth_pct": revenue / previous_revenue - 1,
                     "ebit_bn": ebit, "ebit_margin_pct": ebit / revenue if revenue else 0,
                     "cash_tax_bn": tax, "da_bn": da, "capex_bn": capex,
                     "change_nwc_bn": delta_nwc, "ufcf_bn": ufcf})
        previous_revenue = revenue
    return pd.DataFrame(rows)


def calculate_dcf(forecast, wacc, terminal_growth, net_cash_bn, shares_bn):
    if forecast is None or forecast.empty:
        raise ValueError("Forecast cannot be empty")
    if shares_bn <= 0:
        raise ValueError("Shares outstanding must be positive")
    if wacc <= terminal_growth:
        raise ValueError("WACC must exceed terminal growth")
    if wacc <= -1:
        raise ValueError("WACC must be greater than -100%")
    cashflows = forecast["ufcf_bn"].astype(float).tolist()
    pv_forecast = sum(cf / ((1 + wacc) ** t) for t, cf in enumerate(cashflows, start=1))
    terminal_value = cashflows[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
    pv_terminal = terminal_value / ((1 + wacc) ** len(cashflows))
    ev = pv_forecast + pv_terminal
    equity_value = ev + net_cash_bn
    value_per_share_pounds = equity_value / shares_bn
    return {"pv_forecast_bn": pv_forecast, "terminal_value_bn": terminal_value,
            "pv_terminal_bn": pv_terminal, "enterprise_value_bn": ev,
            "equity_value_bn": equity_value, "value_per_share_pounds": value_per_share_pounds,
            "value_per_share_pence": value_per_share_pounds * 100}


def sensitivity_table(forecast, wacc_values, growth_values, net_cash_bn, shares_bn):
    result = {}
    for wacc in wacc_values:
        row = {}
        for growth in growth_values:
            if wacc <= growth:
                row[growth] = float("nan")
            else:
                row[growth] = calculate_dcf(forecast, wacc, growth, net_cash_bn, shares_bn)["value_per_share_pence"]
        result[wacc] = row
    return pd.DataFrame.from_dict(result, orient="index").sort_index().sort_index(axis=1)
