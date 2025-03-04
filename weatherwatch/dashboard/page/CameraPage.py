from datetime import date, datetime, timedelta
from pathlib import Path

import dash_bootstrap_components as dbc
import dash_player as dp
import piexif
from conf.CameraConfig import CameraConfig
from conf.TimelapseConfig import TimelapseConfig
from dash import html
from dashboard.page.BasePage import BasePage


class CameraPage(BasePage):
    """
    camera dash page
    https://community.plotly.com/t/how-to-embed-images-into-a-dash-app/61839
    https://stackoverflow.com/questions/68747552/how-to-show-a-local-image-in-an-interactive-dash-with-python
    """  # noqa

    PATH = "/Camera"

    # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    DATE_FORMAT = "%Y:%m:%d %H:%M:%S"

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__()

        self._camera_config: CameraConfig = self._app_config.camera
        self._timelapse_config: TimelapseConfig = self._app_config.timelapse

    def content(self, **kwargs) -> dbc.Container:
        """
        render page content
        :param self: this
        :param kwargs: additional arguments
        """

        curr_image: Path = self._camera_config.current_file

        exif_dict = piexif.load(str(curr_image))

        img_date: datetime = datetime.strptime(
            exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal].decode(), CameraPage.DATE_FORMAT
        )
        curr_date: str = img_date.strftime("%Y-%m-%d %H-%M-%S")

        d = date.today() - timedelta(days=1)
        stamp = d.strftime("%Y-%m-%d")

        return dbc.Container(
            children=[
                dbc.Row(
                    children=dbc.Col(children=html.Center(html.H1(f"time: {curr_date}"))),
                ),
                dbc.Row(children=dbc.Col(children=html.Hr())),
                dbc.Row(children=html.Img(src=f"/cam/{curr_image.name}")),
                dbc.Row(children=dbc.Col(children=html.Hr())),
                dbc.Row(
                    children=dbc.Col(children=html.Center(html.H1(stamp))),
                ),
                dbc.Row(children=dbc.Col(children=html.Hr())),
                dbc.Row(
                    children=dbc.Col(
                        children=dp.DashPlayer(
                            id="player",
                            url=f"/vid/{stamp}{self._timelapse_config.extension}",
                            controls=True,
                            width="100%",
                            height="750px",
                        ),
                    )
                ),
            ]
        )
