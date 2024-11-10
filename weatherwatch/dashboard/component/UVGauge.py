from decimal import Decimal
import dash_daq as daq
from dash import html


class UVGauge(html.Div):
    """
    uv index guage class
    https://www.who.int/news-room/questions-and-answers/item/radiation-the-ultraviolet-(uv)-index
    """

    def __init__(self, uv: Decimal):
        """
        ctor
        :param self: this
        """
        super().__init__(
            [
                daq.Gauge(
                    label="uv index",
                    value=round(uv, 1),
                    color={"gradient": True, "ranges": {"green": [0, 2], "yellow": [2, 7], "red": [7, 15]}},
                    max=15,
                    showCurrentValue=True,
                    units="uv index",
                )
            ]
        )
