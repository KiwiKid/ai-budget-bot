

from pyecharts.charts import Bar, Line
from pyecharts.options import (
    AreaStyleOpts,
    AxisLineOpts,
    AxisOpts,
    AxisTickOpts,
    InitOpts,
    LabelOpts,
    LegendOpts,
    LineStyleOpts,
    TextStyleOpts,
    TitleOpts,
)


class Colors:
    default = "#818cf8"
    yellow = "#ffe5cb"
    green = "#d3fce7"


TITLE_TEXT_STYLE_OPTIONS = TextStyleOpts(
    color="#4b5562", font_size=16, font_weight="600"
)
TITLE_OPTS = {
    "pos_top": "0px",
    "pos_left": "2px",
    "item_gap": 10,
    "title_textstyle_opts": TITLE_TEXT_STYLE_OPTIONS,
}

AXIS_LINE_OPTS = AxisLineOpts(
    linestyle_opts=LineStyleOpts(color="#9ca3af")
)


def line_chart(data: dict, color=None):
    """Line chart"""

    color = color or Colors.default

    # create chart instance
    line = Line(init_opts=InitOpts(width="105%", height="300px"))

    # add y,x axis data
    line.add_xaxis(data["x"])
    line.add_yaxis(
        "",
        data["y"],
        is_smooth=False,
        areastyle_opts=AreaStyleOpts(opacity=0.1, color=color),
        label_opts=LabelOpts(is_show=False),
    )

    # add chart options
    line.set_colors([color])
    line.set_global_opts(
        title_opts=TitleOpts(title=data["chart_title"], **TITLE_OPTS),
        legend_opts=LegendOpts(is_show=False),
        yaxis_opts=AxisOpts(
            position="bottom",
            name_location="end",
            axisline_opts=AXIS_LINE_OPTS,
            axistick_opts=AxisTickOpts(is_show=False),
        ),
        xaxis_opts=AxisOpts(
            axisline_opts=AXIS_LINE_OPTS, axistick_opts=AxisTickOpts(
                is_show=False)
        ),
    )

    # finally prepare chart options for rendering.
    line._prepare_render()
    return line
