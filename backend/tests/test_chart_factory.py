from backend.app.charts.factory import build_chart
from backend.app.models.chart_request import ChartInputRef, ChartRequest


def test_build_composite_chart_smoke():
    a = ChartInputRef(
        name="partner_a",
        data={
            "birthDate": "1990-01-01",
            "birthTime": "12:00",
            "birthPlace": "Istanbul",
        },
    )
    b = ChartInputRef(
        name="partner_b",
        data={
            "birthDate": "1992-06-15",
            "birthTime": "08:30",
            "birthPlace": "Istanbul",
        },
    )
    req = ChartRequest(kind="composite", tz="Europe/Istanbul", a=a, b=b)
    result = build_chart(req)
    assert result.meta.kind == "composite"
    assert result.bodies
