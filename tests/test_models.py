import pytest
from subsystem3.models import EnergySettings, EnergyAnalytics, SustainabilityScore, EnergyGoal, EnergyAlert

def test_settings_constructor_getters_setters_and_validation():
    s = EnergySettings(1, 0.30, 0.4, "Demo source")
    assert s.get_price_per_kwh() == 0.30
    s.set_price_per_kwh(0.25)
    assert s.get_price_per_kwh() == 0.25
    with pytest.raises(ValueError): s.set_price_per_kwh(-1)
    with pytest.raises(ValueError): s.set_factor_source(" ")

def test_analytics_cost_and_carbon():
    settings = EnergySettings(1, 0.30, 0.4, "Demo")
    a = EnergyAnalytics(100, settings, "month")
    assert a.calculate_cost() == 30.00
    assert a.calculate_carbon_emissions() == 40.00
    a.set_energy_kwh(50)
    assert a.calculate_cost() == 15.00
    with pytest.raises(ValueError): a.set_period("year")

def test_score_is_bounded_and_carbon_reduction_component():
    s = SustainabilityScore(100, 300, 60, 80)
    assert s.calculate_score() == pytest.approx(54.166666, abs=0.01)
    s.set_monthly_target_kwh(50)
    assert 0 <= s.calculate_score() <= 100
    with pytest.raises(ValueError): s.set_score(101)

def test_goal_progress_and_daily_limit():
    goal = EnergyGoal(1, 1, 200, "2026-10", 20)
    assert goal.calculate_progress(50) == 25
    assert goal.is_daily_limit_exceeded(21)
    assert not goal.is_daily_limit_exceeded(20)
    with pytest.raises(ValueError): goal.set_month("October")

def test_alert_encapsulation_and_mark_read():
    alert = EnergyAlert(1, 1, "Over limit", "2026-10-28", False)
    assert alert.get_is_read() is False
    alert.mark_read()
    assert alert.get_is_read() is True
    with pytest.raises(ValueError): alert.set_message("")
