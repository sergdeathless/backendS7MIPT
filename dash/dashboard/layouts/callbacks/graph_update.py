from __future__ import annotations

import plotly.graph_objects as go
from dash import no_update
from dash.dependencies import Input, Output, State

from dashboard.api_client import APIError, fetch_delivery_forecast, login, register
from dashboard.index import app


def _empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        autosize=True,
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis=dict(visible=False, range=[0, 1]),
        yaxis=dict(visible=False, range=[0, 1]),
        annotations=[
            dict(
                text=message,
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                font=dict(size=16, color="#666"),
            )
        ],
    )
    return fig


@app.callback(
    Output("auth-token-store", "data"),
    Output("auth-status", "children"),
    Input("auth-login-btn", "n_clicks"),
    Input("auth-register-btn", "n_clicks"),
    State("auth-username", "value"),
    State("auth-password", "value"),
    prevent_initial_call=True,
)
def handle_auth(login_clicks, register_clicks, username, password):
    from dash import callback_context

    if not callback_context.triggered:
        return no_update, no_update
    triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]

    if not username or not password:
        return no_update, "Username and password are required."

    try:
        if triggered_id == "auth-register-btn":
            register(username, password)
            return no_update, "User registered. You can log in now."
        token = login(username, password)
        return token, f"Logged in as {username}."
    except APIError as exc:
        return no_update, str(exc)


@app.callback(
    Output("delivery-heatmap", "figure"),
    Output("forecast-status", "children"),
    Input("auth-token-store", "data"),
    Input("anchor-date", "date"),
    prevent_initial_call=False,
)
def graph_update(token, anchor_date):
    if not token:
        return _empty_figure("Войдите, чтобы увидеть матрицу поставок."), ""

    anchor_raw = ""
    if anchor_date:
        s = str(anchor_date).strip()
        anchor_raw = s.split("T")[0] if "T" in s else s

    try:
        payload = fetch_delivery_forecast(token, anchor_date=anchor_raw or None)
    except APIError as exc:
        return _empty_figure("Не удалось загрузить данные."), str(exc)

    m = payload["matrix"]
    parts = m["parts"]
    regions = m["regions"]
    z = m["lead_days"]
    text = [[str(v) for v in row] for row in z]

    uirevision = str(payload["anchor_date"])

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=parts,
            y=regions,
            text=text,
            texttemplate="%{text}",
            colorscale="Blues",
            hovertemplate="%{y} / %{x}<br>через %{z} дн.<extra></extra>",
            colorbar=dict(title="Дней до поставки"),
        )
    )
    fig.update_layout(
        autosize=True,
        margin=dict(l=100, r=72, t=96, b=110),
        uirevision=uirevision,
        title=dict(
            text=f"Дата заказа: {payload['anchor_date']}",
            x=0.5,
            xanchor="center",
        ),
    )
    fig.update_xaxes(side="top", tickangle=-40)

    return fig, ""
