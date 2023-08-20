from django.shortcuts import render
from charts.echarts import line_chart, Colors


def dashboard_view(request):

    total_page_views = {
        "x": ["mon", "tue", "wed", "thur", "fri", "sat", "sun"],
        "y": [8, 20, 15, 20, 50, 30, 35],
        "chart_title": "Total Page Views",
    }

    unique_visitors = {
        "x": ["mon", "tue", "wed", "thur", "fri", "sat", "sun"],
        "y": [3, 4, 10, 12, 30, 20, 33],
        "chart_title": "Unique Visitors",
    }
    signups = {
        "x": ["mon", "tue", "wed", "thur", "fri", "sat", "sun"],
        "y": [3, 4, 10, 12, 30, 20, 33],
        "chart_title": "Signups",
    }
    charts = [
        line_chart(total_page_views),
        line_chart(unique_visitors, Colors.yellow),
        line_chart(signups, Colors.green)
    ]

    context = {
        "charts": charts
    }

    return render(request, "dashboard.html", context)
