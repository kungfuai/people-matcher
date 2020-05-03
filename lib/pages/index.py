import dash
import dash_core_components as dcc
import dash_html_components as html
import dash
import dash_table
from dash.dependencies import Input, State, Output
import json
import pandas as pd
from lib.components.person_table import mentees_table, mentors_table
from lib import recommender, db
from lib.dash_app import app
from lib.data_utils import parse_uploaded_content


__store__ = recommender.DataStore()

tabs_styles = {"height": "1.8rem"}
tab_style = {
    "borderBottom": "1px solid #d6d6d6",
    "padding": "6px",
    "fontWeight": "bold",
}

tab_selected_style = {
    "borderTop": "1px solid #d6d6d6",
    "borderBottom": "1px solid #d6d6d6",
    "backgroundColor": "#119DFF",
    "color": "white",
    "padding": "6px",
}


def matches_sorted_container():
    return html.Div(
        children=[
            dcc.Tabs(
                id="matches-tabs",
                value="suggested",
                children=[
                    dcc.Tab(
                        label="Sugggested",
                        value="suggested",
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        label="Confirmed",
                        value="confirmed",
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        label="Rejected",
                        value="rejected",
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                ],
                className="mt-2",
            ),
            html.H2(id="match-area-title", children="", className="text-center"),
            html.Div(
                children=[
                    html.Div(
                        id=f"match-row-{i}",
                        className="row",
                        children=[
                            html.Div(id=f"mentee-card-{i}", className="card col-4"),
                            html.Div(
                                className="col-4",
                                children=[
                                    html.Button(
                                        "👍",
                                        id=f"btn-suggestion-thumbup-{i}",
                                        className="btn btn-sm",
                                        style={"fontSize": "2rem"},
                                    ),
                                    html.Button(
                                        "👎",
                                        id=f"btn-suggestion-thumbdown-{i}",
                                        className="btn btn-sm",
                                        style={"fontSize": "2rem"},
                                    ),
                                ],
                            ),
                            html.Div(id=f"mentor-card-{i}", className="card col-4"),
                        ],
                    )
                    for i in range(3)
                ],
                id="matches-sorted-container",
                className="container text-center",
            ),
        ],
    )


def get_layout():
    return html.Div(
        id="app",
        className="container",
        children=[
            dcc.Input(id="thumb_btn_timestamp", value=""),
            html.Div(id="thumb_btn_timestamp_debug"),
            html.Section(
                className="jumbotron text-center",
                children=[
                    html.H1(
                        "People Matcher", className="text-center jumbotron-heading"
                    ),
                ],
            ),
            html.Div(className="row", children=[mentees_table(), mentors_table()]),
            html.Section(
                className="jumbotron",
                children=[
                    html.Div(
                        className="form text-center",
                        children=[
                            # html.Button("Suggest All Matches", id="btn-suggest"),
                            # html.Button("Get Specific Matches", id="btn-suggest-specific"),
                            # html.Button("Download CSV File", id="down-csv-file"),
                            dcc.Link(
                                "Download CSV file", href="/download", refresh=True
                            ),
                        ],
                    ),
                    html.Div(
                        children=[
                            html.Label("Sort By"),
                            dcc.Dropdown(
                                style={"textAlign": "center",},
                                options=[
                                    {"label": "Mentor Name", "value": "mentorName"},
                                    {"label": "Mentee Name", "value": "menteeName"},
                                    {"label": "Score", "value": "score"},
                                    {"label": "Distance", "value": "distance"},
                                    {"label": "Ethinicity Match", "value": "ethnicity"},
                                ],
                                id="SORTBY",
                                placeholder="Select",
                            ),
                            html.Label("Filter By"),
                            dcc.RadioItems(
                                options=[
                                    {"label": "By Mentor", "value": "mentorName"},
                                    {"label": "By Mentee", "value": "menteeName"},
                                    {"label": "By Score", "value": "score"},
                                    {"label": "Max Distance", "value": "distance"},
                                    {"label": "Ethnicity Match", "value": "ethnicity"},
                                    {"label": "None", "value": "none"},
                                ],
                                id="FILTER",
                            ),
                            html.Div(
                                children=[
                                    html.H3("Used For Filtering:"),
                                    dcc.Input(
                                        id="get-specifics",
                                        value="Enter Here",
                                        type="text",
                                    ),
                                ],
                                id="get-specifics-container",
                                className="col text-center",
                            ),
                            # dcc.Input(id='get-specifics', value='initial value', type='text'),
                            html.Div(
                                html.Button("Get Matches", id="btn-filter"),
                                className="col text-center",
                            ),
                        ]
                    ),
                    matches_sorted_container(),
                    # The original downloading button I made, container
                    # html.Div(
                    #     className="row",
                    #     children=[
                    #         html.Div(
                    #             children=[],
                    #             id="dowloading-container",
                    #             className="col text-center",
                    #         )
                    #     ],
                    # ),
                ],
            ),
        ],
    )


@app.callback(
    Output("mentees-table", "children"),
    [Input("mentees-mock-checklist", "value"), Input("mentees-uploader", "contents")],
    [State("mentees-table", "children")],
)
def update_mentees_table(value_list, file_content, existing_state):
    if "mentees-use-mock-data" in value_list:
        df = recommender.load_mock_mentees()
        __store__.set_mentees(df)
        return dash_table.DataTable(
            id="mentees-data-table",
            columns=[dict(name=c, id=c) for c in df.columns.tolist()],
            data=df.to_dict("records"),
        )
    elif file_content is not None:
        try:
            df = parse_uploaded_content(file_content)
            __store__.set_mentees(df)
            return dash_table.DataTable(
                id="mentees-data-table",
                columns=[dict(name=c, id=c) for c in df.columns.tolist()],
                data=df.to_dict("records"),
            )
        except:
            return html.Div(
                "Cannot understand the uploaded file.", className="text-danger"
            )


@app.callback(
    Output("mentors-table", "children"),
    [Input("mentors-mock-checklist", "value"), Input("mentors-uploader", "contents")],
    [State("mentors-table", "children")],
)
def update_mentors_table(value_list, file_content, existing_state):
    if "mentors-use-mock-data" in value_list:
        df = recommender.load_mock_mentors()
        __store__.set_mentors(df)
        return dash_table.DataTable(
            id="mentors-data-table",
            columns=[dict(name=c, id=c) for c in df.columns.tolist()],
            data=df.to_dict("records"),
        )
    elif file_content is not None:
        try:
            df = parse_uploaded_content(file_content)
            __store__.set_mentors(df)
            return dash_table.DataTable(
                id="mentors-data-table",
                columns=[dict(name=c, id=c) for c in df.columns.tolist()],
                data=df.to_dict("records"),
            )
        except:
            return html.Div(
                "Cannot understand the uploaded file.", className="text-danger"
            )


def suggestion_to_dash(s, index, hidden=False):
    features = json.loads(s.features)
    return html.Div(
        id=f"suggestion-{index}",
        className="container",
        style={"display": "none" if hidden else "block"},
        children=html.Div(
            children=[
                html.Div(
                    className="card col-4",
                    children=[
                        html.H3("Mentee: " + str(s.mentee_name)),
                        html.Div(s.mentee_address),
                    ],
                ),
                html.Div(
                    className="card col-4",
                    children=[
                        html.Div(f"Score: {s.score:.3f}"),
                        html.Div(
                            f"{features.get('distance_in_miles', 1000):.1f} miles"
                        ),
                        html.Div(f"ethnicity match: {features.get('ethnicity_match')}"),
                        html.Button(
                            "👍",
                            id=f"btn-suggestion-thumbup-{index}",
                            className="btn btn-sm",
                            value=f"{s.mentor_id},{s.mentee_id}",
                            style={"fontSize": "2rem"},
                        ),
                        html.Button(
                            "👎",
                            id=f"btn-suggestion-thumbdown-{index}",
                            className="btn btn-sm",
                            value=f"{s.mentor_id},{s.mentee_id}",
                            style={"fontSize": "2rem"},
                        ),
                    ],
                ),
                html.Div(
                    className="card col-4",
                    children=[
                        html.H3("Mentor: " + str(s.mentor_name)),
                        html.Div(s.mentor_address),
                    ],
                ),
            ],
            className="row",
        ),
    )


def get_matches():
    return __store__.matches()


@app.callback(
    Output("get-specifics-container", "children"),
    [Input("FILTER", "value")],
    [State("get-specifics-container", "children")],
)
def get_specifics_filtering(value_in, existing_state):
    if value_in is None:
        return existing_state

    if value_in == "mentorName":
        return [
            html.H3("Enter Mentor Name:"),
            dcc.Input(id="get-specifics", value="Enter Here", type="text"),
        ]

    if value_in == "menteeName":
        return [
            html.H3("Enter Mentee Name:"),
            dcc.Input(id="get-specifics", value="Enter Here", type="text"),
        ]

    if value_in == "score":
        return [
            html.H3("Enter Minimum Score:"),
            dcc.Input(id="get-specifics", value="Enter Here", type="text"),
        ]

    if value_in == "distance":
        return [
            html.H3("Enter Maximum Distance:"),
            dcc.Input(id="get-specifics", value="Enter Here", type="text"),
        ]

    if value_in == "ethnicity":
        return [
            html.H3("Only Display Matches with the Same Ethnicity"),
            dcc.Input(id="get-specifics", value="Ethnicity Matches Only", type="text"),
        ]
    if value_in == "none":
        return [
            html.H3("No Filtering"),
            dcc.Input(id="get-specifics", value="None", type="text"),
        ]


def matches_table(
    store,
    status,
    value_in_sort,
    value_in_filter_type,
    value_in_specific,
    existing_state,
):
    if store.mentors is None or store.mentees is None:
        return [
            html.Div(
                ["Please upload or use mock data for both mentors and mentees."],
                className="alert alert-warning alert-dismissible fade show",
            )
        ]

    final_matches = __store__.matches_to_show(
        status=status,
        sort_by=value_in_sort,
        filter_key=value_in_filter_type,
        filter_value=value_in_specific,
    )

    # final_matches = []
    # if (
    #     value_in_filter_type is None or value_in_filter_type == "none"
    # ) and value_in_sort is not None:
    #     final_matches = recommender.sort_by(get_matches(), value_in_sort)
    # elif value_in_filter_type is not None and value_in_sort is not None:
    #     final_matches = recommender.sort_by(get_matches(), value_in_sort)
    #     final_matches = recommender.filter_by(
    #         final_matches, value_in_filter_type, value_in_specific
    #     )
    # elif value_in_filter_type is not None and value_in_sort is None:
    #     final_matches = recommender.filter_by(
    #         get_matches(), value_in_filter_type, value_in_specific
    #     )
    # elif (
    #     value_in_filter_type is None or value_in_filter_type == "none"
    # ) and value_in_sort is None:
    #     final_matches = recommender.sort_by(get_matches(), "score")

    return [
        suggestion_to_dash(s, i) for i, (_, s) in enumerate(final_matches.iterrows())
    ]


@app.callback(
    Output("thumb_btn_timestamp_debug", "children"),
    [Input("thumb_btn_timestamp", "value")],
)
def thumb_btn_timestamp_debug(v):
    return v


@app.callback(
    [
        Output("match-area-title", "children"),
        Output("match-row-0", "children"),
        Output("match-row-1", "children"),
        Output("match-row-2", "children"),
    ],
    [
        Input("btn-filter", "n_clicks_timestamp"),
        Input("matches-tabs", "value"),
        Input("thumb_btn_timestamp", "value"),
    ],
    [
        State("SORTBY", "value"),
        State("FILTER", "value"),
        State("get-specifics", "value"),
        State("matches-sorted-container", "children"),
    ],
)
def update_matches_view(
    btn_filter_timestamp,
    tab,
    thumb_btn_timestamp,
    value_in_sort,
    value_in_filter_type,
    value_in_specific,
    existing_state,
):
    title = f"{tab} Matches"
    title = title[0].upper() + title[1:]

    rows = matches_table(
        __store__,
        tab,
        value_in_sort,
        value_in_filter_type,
        value_in_specific,
        existing_state,
    )

    rows = {i: r for i, r in enumerate(rows)}

    class EmptySuggestion:
        score = 0
        mentor_id = ""
        mentor_name = ""
        mentor_address = ""
        mentee_id = ""
        mentee_name = ""
        mentee_address = ""
        features = json.dumps({})

    empty_suggestion = EmptySuggestion()
    return [
        title,
        rows.get(0, suggestion_to_dash(empty_suggestion, 0, hidden=True)),
        rows.get(1, suggestion_to_dash(empty_suggestion, 1, hidden=True)),
        rows.get(2, suggestion_to_dash(empty_suggestion, 2, hidden=True)),
    ]


@app.callback(
    Output("thumb_btn_timestamp", "value"),
    [Input(f"btn-suggestion-thumbup-{i}", "n_clicks_timestamp") for i in range(3)]
    + [Input(f"btn-suggestion-thumbdown-{i}", "n_clicks_timestamp") for i in range(3)],
    [State(f"btn-suggestion-thumbup-{i}", "value") for i in range(3)]
    + [State(f"btn-suggestion-thumbdown-{i}", "value") for i in range(3)],
)
def on_thumbup_or_thumbdown(*inputs):
    thumbup_click_timestamps = inputs[:3]
    thumbdown_click_timestamps = inputs[3:6]
    thumbup_btn_values = inputs[6:9]
    thumbdown_btn_values = inputs[9:12]
    thumbup_click_timestamps = [
        0 if t is None else float(t) for t in thumbup_click_timestamps
    ]
    thumbdown_click_timestamps = [
        0 if t is None else float(t) for t in thumbdown_click_timestamps
    ]
    most_recently_clicked_thumbup_idx = sorted(
        enumerate(thumbup_click_timestamps), key=lambda x: -x[1]
    )[0][0]
    most_recently_clicked_thumbdown_idx = sorted(
        enumerate(thumbdown_click_timestamps), key=lambda x: -x[1]
    )[0][0]

    most_recently_clicked_timestamp = max(
        thumbup_click_timestamps + thumbdown_click_timestamps
    )
    print("on thumbup or thumbdown")
    print(thumbup_btn_values)
    if most_recently_clicked_timestamp == 0:
        return -1
    is_thumbup = max(thumbup_click_timestamps) >= max(thumbdown_click_timestamps)
    if is_thumbup:
        btn_value = thumbup_btn_values[most_recently_clicked_thumbup_idx]
        mentor_id, mentee_id = tuple(btn_value.split(","))
        __store__.confirm_match(mentor_id, mentee_id)
    else:
        btn_value = thumbdown_btn_values[most_recently_clicked_thumbdown_idx]
        mentor_id, mentee_id = tuple(btn_value.split(","))
        __store__.reject_match(mentor_id, mentee_id)

    return most_recently_clicked_timestamp
