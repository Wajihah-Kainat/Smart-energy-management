# Subsystem 4: coach and reports use buildings (S1), readings (S2) and cost/carbon/goal (S3)
from datetime import date

from conftest import register
from app.s4.models import AICoachService, ReportGenerator
import io

MONTH = date.today().strftime("%Y-%m")
LAST_MONTH_DAY = f"{MONTH}-01"


def add_reading(client, day, kwh):
    client.post("/readings", data={"device_id": 1, "date": day, "amount_kwh": kwh})


def configure(client, price=0.5, factor=0.4):
    client.put("/api/v1/s3/settings/1", json={"price_per_kwh": price, "emission_factor": factor, "factor_source": "t"})


def test_pages_need_login(client):
    for url in ("/coach", "/reports", "/reports/1/pdf"):
        assert client.get(url).status_code == 302


def test_coach_building_list_comes_from_subsystem_1(user):
    page = user.get("/coach").get_data(as_text=True)
    assert "Main office" in page and "21 °C" in page


def test_coach_uses_real_usage_of_the_building(user):
    add_reading(user, LAST_MONTH_DAY, 55)
    page = user.get("/coach").get_data(as_text=True)
    assert "55.0 kWh" in page
    tip = user.post("/coach", data={"building_id": 1, "period": MONTH}).get_data(as_text=True)
    assert "<li>" in tip


def test_coach_without_readings_says_so(user):
    tip = user.post("/coach", data={"building_id": 1, "period": MONTH}).get_data(as_text=True)
    assert "No readings found" in tip


def test_report_shows_cost_and_carbon_from_subsystem_3(user):
    add_reading(user, LAST_MONTH_DAY, 100)
    configure(user)
    user.post("/reports", data={"building_id": 1, "period": MONTH})
    page = user.get("/reports").get_data(as_text=True)
    assert "100.0 kWh" in page and "€50.00" in page and "40.00 kg" in page


def test_report_without_price_asks_for_settings(user):
    add_reading(user, LAST_MONTH_DAY, 10)
    user.post("/reports", data={"building_id": 1, "period": MONTH})
    assert "set price" in user.get("/reports").get_data(as_text=True)


def test_report_pdf_download_and_delete(user):
    add_reading(user, LAST_MONTH_DAY, 10)
    configure(user)
    user.post("/reports", data={"building_id": 1, "period": MONTH})
    pdf = user.get("/reports/1/pdf")
    assert pdf.status_code == 200 and pdf.mimetype == "application/pdf" and pdf.data.startswith(b"%PDF")
    user.post("/reports/1/delete")
    assert "No reports created yet" in user.get("/reports").get_data(as_text=True)


def test_reports_are_private(user, app):
    user.post("/reports", data={"building_id": 1, "period": MONTH})
    other = app.test_client()
    register(other, name="Bob", email="bob@example.com")
    assert other.get("/reports/1/pdf").status_code == 404
    assert "Main office" not in other.get("/reports").get_data(as_text=True)


def test_report_for_foreign_building_is_not_created(user, app):
    other = app.test_client()
    register(other, name="Bob", email="bob@example.com")
    other.post("/reports", data={"building_id": 1, "period": MONTH})
    import sqlite3
    count = sqlite3.connect(app.config["DATABASE"]).execute("SELECT COUNT(*) FROM reports").fetchone()[0]
    assert count == 0


def test_ai_coach_service_rule_based_tips():
    coach = AICoachService()
    coach.client = None
    assert "optimal" in coach.generate_coach_tips(5)
    assert "high" in coach.generate_coach_tips(25)
    context = {"building_type": "office", "comfort_temp": 21.0, "month": "2026-10", "energy_kwh": 10,
               "change_percent": 30.0, "goal_percent": 120}
    assert "120%" in coach.generate_coach_tips(5, context)
    prompt = coach.build_prompt(5, context)
    assert "office" in prompt and "21 °C" in prompt            # building type and comfort temperature from S1
    context.update(energy_kwh=700, change_percent=0, goal_percent=50)
    assert "21 °C" in coach.generate_coach_tips(25, context)


def test_report_generator_writes_pdf():
    buffer = io.BytesIO()
    ReportGenerator().create_pdf_report(["Line 1", "Line 2"], "A tip " * 40, output=buffer)
    assert buffer.getvalue().startswith(b"%PDF")


def test_comfort_temperature_is_printed_in_the_report(user):
    from app.s4 import _report_lines, data
    add_reading(user, LAST_MONTH_DAY, 5)
    with user.application.app_context():
        summary = data.building_summary(1, 1, MONTH)
    assert "Comfort temperature: 21 C" in _report_lines(summary)


def test_coach_page_says_when_no_openai_key_is_set(user, monkeypatch):
    from app.s4 import ai_coach
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(ai_coach, "client", None)
    page = user.get("/coach").get_data(as_text=True)
    assert "No OpenAI key set" in page and "What is sent to the AI" not in page
    tip = user.post("/coach", data={"building_id": 1, "period": MONTH}).get_data(as_text=True)
    assert "Built-in tip: no OpenAI key is set" in tip


def test_coach_page_shows_openai_label_when_key_works(user, monkeypatch):
    from app.s4 import ai_coach

    class FakeClient:                       # a fake OpenAI: no real request is sent (requirement S4-N9)
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    message = type("M", (), {"content": " Turn off the lights. "})
                    return type("R", (), {"choices": [type("C", (), {"message": message})]})
    monkeypatch.setattr(ai_coach, "client", FakeClient)
    page = user.post("/coach", data={"building_id": 1, "period": MONTH}).get_data(as_text=True)
    assert "Turn off the lights." in page and "Tip by OpenAI" in page and "What is sent to the AI" in page


def test_coach_page_shows_error_label_when_openai_fails(user, monkeypatch):
    from app.s4 import ai_coach

    class BrokenClient:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    raise RuntimeError("no network")
    monkeypatch.setattr(ai_coach, "client", BrokenClient)
    page = user.post("/coach", data={"building_id": 1, "period": MONTH}).get_data(as_text=True)
    assert "OpenAI could not be reached" in page
