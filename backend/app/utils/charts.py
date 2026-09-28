"""Chart data builders (Plotly / Matplotlib friendly)."""
from __future__ import annotations

from typing import Any, Dict, Sequence


def line_chart_data(x: Sequence[Any], y: Sequence[Any], name: str = "series") -> Dict[str, Any]:
    """Build a Plotly line chart payload."""
    return {
        "type": "line",
        "data": [{"x": list(x), "y": list(y), "name": name}],
    }


def bar_chart_data(
    categories: Sequence[Any], values: Sequence[Any], name: str = "series"
) -> Dict[str, Any]:
    """Build a Plotly bar chart payload."""
    return {
        "type": "bar",
        "data": [{"x": list(categories), "y": list(values), "name": name}],
    }


def pie_chart_data(labels: Sequence[str], values: Sequence[float]) -> Dict[str, Any]:
    """Build a Plotly pie chart payload."""
    return {
        "type": "pie",
        "data": [{"labels": list(labels), "values": list(values)}],
    }


def build_plotly_figure(chart: Dict[str, Any]) -> Any:
    """Return a Plotly Figure object from a chart payload (lazy import)."""
    import plotly.graph_objects as go

    fig = go.Figure()
    for trace in chart.get("data", []):
        if chart.get("type") == "line":
            fig.add_trace(go.Scatter(**trace))
        else:
            fig.add_trace(go.Bar(**trace))
    if chart.get("type") == "pie":
        fig = go.Figure(
            data=go.Pie(
                labels=chart["data"][0]["labels"],
                values=chart["data"][0]["values"],
            )
        )
    return fig