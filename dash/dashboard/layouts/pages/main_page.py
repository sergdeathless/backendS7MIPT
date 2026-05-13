from dash import dcc, html


def _auth_panel() -> html.Div:
    return html.Div(
        id="auth-panel",
        style={"padding": "10px 0"},
        children=[
            html.H3("Authentication", style={"marginBottom": 8}),
            dcc.Input(
                id="auth-username",
                type="text",
                placeholder="username",
                style={"marginRight": 8},
            ),
            dcc.Input(
                id="auth-password",
                type="password",
                placeholder="password",
                style={"marginRight": 8},
            ),
            html.Button("Register", id="auth-register-btn", n_clicks=0,
                        style={"marginRight": 8}),
            html.Button("Login", id="auth-login-btn", n_clicks=0),
            html.Div(id="auth-status", style={"marginTop": 8, "color": "#444"}),
            dcc.Store(id="auth-token-store"),
        ],
    )


def _forecast_panel() -> html.Div:
    return html.Div(
        id="forecast-panel",
        style={"padding": "10px 0"},
        children=[
            html.H3("Матрица сроков поставки", style={"marginBottom": 8}),
            html.P(
                "Число в ячейке — через сколько календарных дней ожидается поставка "
                "после выбранной даты заказа. График обновляется при смене даты.",
                style={"maxWidth": "min(960px, 92vw)", "color": "#444", "marginBottom": 12},
            ),
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "flexWrap": "wrap",
                    "gap": "14px",
                    "marginBottom": 12,
                    "minHeight": 40,
                },
                children=[
                    html.Span(
                        "День заказа:",
                        style={"fontWeight": 500, "lineHeight": "36px", "whiteSpace": "nowrap"},
                    ),
                    html.Div(
                        className="delivery-date-picker-wrapper",
                        children=[
                            dcc.DatePickerSingle(
                                id="anchor-date",
                                date=None,
                                display_format="DD.MM.YYYY",
                                placeholder="Выберите дату",
                                clearable=True,
                                first_day_of_week=1,
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(id="forecast-status", style={"marginTop": 8, "color": "#a00"}),
            html.Div(
                style={
                    "width": "100%",
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "stretch",
                },
                children=[
                    dcc.Graph(
                        id="delivery-heatmap",
                        config={"responsive": True, "displayModeBar": True},
                        style={
                            "width": "100%",
                            "maxWidth": "min(1920px, 98vw)",
                            "height": "calc(100vh - 240px)",
                            "minHeight": 480,
                        },
                    ),
                ],
            ),
        ],
    )


def get_main_page() -> html.Div:
    return html.Div(
        id="parent",
        style={
            "width": "min(1920px, 98vw)",
            "maxWidth": "98vw",
            "margin": "0 auto",
            "padding": "16px 1vw 24px",
            "boxSizing": "border-box",
        },
        children=[
            html.H1(
                id="H1",
                children="Прогноз сроков поставки по регионам",
                style={"textAlign": "center", "marginTop": 20, "marginBottom": 30},
            ),
            _auth_panel(),
            html.Hr(),
            _forecast_panel(),
        ],
    )
