from dash import Dash
from dashboard.assets.external import external_stylesheets

app = Dash(
    __name__,
    #meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    external_stylesheets=external_stylesheets,
)

app.title = "План поставок запчастей"