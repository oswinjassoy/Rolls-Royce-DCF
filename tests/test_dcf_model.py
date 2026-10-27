import math
import pandas as pd
import pytest
from dcf_model import build_forecast, calculate_dcf, sensitivity_table, wacc_calculation


def test_wacc_capm_and_weights():
    wacc, coe = wacc_calculation(.04, .05, 1.2, .06, .25, .8)
    assert coe == pytest.approx(.10)
    assert wacc == pytest.approx(.8*.10 + .2*.06*.75)


def test_forecast_formulas_and_growth():
    f = build_forecast(100, .10, .20, .25, .04, .05, .10, years=2, start_year=2026)
    first = f.iloc[0]
    assert first.revenue_bn == pytest.approx(110)
    assert first.ebit_bn == pytest.approx(22)
    assert first.cash_tax_bn == pytest.approx(5.5)
    assert first.da_bn == pytest.approx(4.4)
    assert first.capex_bn == pytest.approx(5.5)
    assert first.change_nwc_bn == pytest.approx(1)
    assert first.ufcf_bn == pytest.approx(14.4)
    assert f.iloc[1].year == 2027


def test_dcf_discounting_and_equity_bridge():
    f = pd.DataFrame({"ufcf_bn": [10.0, 10.0]})
    v = calculate_dcf(f, .10, .02, 5, 2)
    pv_fcfs = 10/1.1 + 10/(1.1**2)
    tv = 10*1.02/(.10-.02)
    assert v["pv_forecast_bn"] == pytest.approx(pv_fcfs)
    assert v["pv_terminal_bn"] == pytest.approx(tv/(1.1**2))
    assert v["equity_value_bn"] == pytest.approx(v["enterprise_value_bn"] + 5)
    assert v["value_per_share_pounds"] == pytest.approx(v["equity_value_bn"]/2)
    assert v["value_per_share_pence"] == pytest.approx(v["value_per_share_pounds"]*100)


def test_invalid_terminal_growth_and_share_count():
    f = pd.DataFrame({"ufcf_bn": [1.0]})
    with pytest.raises(ValueError): calculate_dcf(f, .05, .05, 1, 2)
    with pytest.raises(ValueError): calculate_dcf(f, .10, .02, 1, 0)


def test_sensitivity_monotonicity():
    f = pd.DataFrame({"ufcf_bn": [10.0, 11.0, 12.0]})
    s = sensitivity_table(f, [.08, .09], [.01, .02], 2, 1)
    assert s.loc[.08, .01] > s.loc[.09, .01]
    assert s.loc[.08, .02] > s.loc[.08, .01]
