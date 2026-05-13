import os

from dashboard.content import app

server = app.server
if __name__ == "__main__":
    debug = os.getenv("DASH_DEBUG", "false").lower() == "true"
    host = os.getenv("DASH_HOST", "0.0.0.0")
    port = int(os.getenv("DASH_PORT", "8050"))
    app.run_server(host=host, port=port, debug=debug)