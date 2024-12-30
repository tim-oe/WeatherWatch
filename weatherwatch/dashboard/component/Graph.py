from typing import List

import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import dcc
from entity.OutdoorSensor import OutdoorSensor


class Graph(dbc.Container):
    """
    plotting graph
    https://plotly.com/python/graph-objects/
    """

    def __init__(self, title: str, data_title: str, data_units: str, data_key: str, data: List):
        """
        ctor
        :param self: this
        :param title: graph title
        :param data_title: graph data title
        :param data_units: graph data unit
        :param data_key: graph data key to pull from data
        :param data: graph data
        """
        super().__init__(
            children=dcc.Graph(figure=self.build_graph(title, data_title, data_units, data_key, data), animate=False)
        )

    def build_graph(self, title: str, data_title: str, data_units: str, data_key: str, data: List):
        """
        build actual graph
        :param self: this
        :param title: graph title
        :param data_title: graph data title
        :param data_units: graph data unit
        :param data_key: graph data key to pull from data
        :param data: graph data
        """

        val = []
        time = []

        min_val = getattr(data[0], data_key)
        max_val = getattr(data[0], data_key)

        r: OutdoorSensor
        for r in data:
            v = getattr(r, data_key)
            time.append(r.read_time)
            val.append(v)
            min_val = min(min_val, v)
            max_val = max(max_val, v)

        delta = int(max_val - min_val)
        if delta > 100:
            min_val = int(min_val - 10)
            max_val = int(max_val + 10)
        elif delta > 20:
            min_val = int(min_val - 5)
            max_val = int(max_val + 5)
        else:
            min_val = int(min_val - 1)
            max_val = int(max_val + 1)

        fig = go.Figure()

        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text=f"<b>{data_title} {data_units}</b>", range=(min_val, max_val))

        fig.update_layout(title_text=title, height=400, template="plotly_dark")

        fig.add_trace(go.Scatter(x=time, y=val, mode="lines+markers"))

        return fig
