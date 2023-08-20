def chart_view_hx(request):
    """Returns chart options for echarts"""

    period = request.GET.get("period", "week")
    chart_id = request.GET.get("chart_id")
    chart_type = request.GET.get("chart_type")

    days_in_period = {
        "week": 7,
        "month": 30,
    }
    filter_by = days_in_period.get(period, "week")

    # simulate fetching this from your database
    chart_title = CHART_TYPES.get(chart_type, "page_views")
    chart_data = fake_chart_data(filter_by, chart_title)

    # render the chart and update options to include id
    chart = line_chart(chart_data)
    chart.options["id"] = chart_id
    chart._prepare_render()
    data = chart.json_contents

    response = HttpResponse(content=chart.json_contents)

    # optional
    # if using the django_htmx library you can attach any clientside
    # events here . For example

    # trigger_client_event(response, 'filterchanged', params={})
    return response
