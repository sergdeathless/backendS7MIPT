# content.py

from dashboard.index import app
import dashboard.layouts.callbacks.graph_update
from dashboard.layouts.pages.main_page import get_main_page


app.layout = get_main_page()