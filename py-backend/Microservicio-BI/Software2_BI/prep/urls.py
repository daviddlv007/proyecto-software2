from django.urls import path
from .views import (
    prep_schema_index_view,
    prep_table_picker_view,
    prep_editor_view,
    get_table_data,
    rename_columns,
    cast_columns,
    handle_nulls,
    add_calculated,
    aggregate_preview,
    save_table,
    update_rows,
    delete_rows,
    insert_rows,
    nulls_action,
    calc_newcol,
    ai_cleaning_suggest, ai_cleaning_apply
)

app_name = "prep"

urlpatterns = [
    path("", prep_schema_index_view, name="schema_index"),  # ← NUEVO
    path("<str:schema>/", prep_table_picker_view, name="picker"),
    path("<str:schema>/<str:table>/", prep_editor_view, name="editor"),

    path("api/<slug:schema>/<slug:table>/data/", get_table_data, name="data"),
    path("api/<slug:schema>/<slug:table>/update/", update_rows, name="update"),
    path("api/<slug:schema>/<slug:table>/delete/", delete_rows, name="delete"),
    path("api/<slug:schema>/<slug:table>/insert/", insert_rows, name="insert"),
    path("<str:schema>/<str:table>/ai/suggest", ai_cleaning_suggest, name="ai_suggest"),
    path("<str:schema>/<str:table>/ai/apply", ai_cleaning_apply, name="ai_apply"),
    # ya tienes:
    path("api/<slug:schema>/<slug:table>/rename/", rename_columns, name="rename"),
    path("api/<slug:schema>/<slug:table>/cast/", cast_columns, name="cast"),
    path("api/<slug:schema>/<slug:table>/nulls/", nulls_action, name="nulls"),
    path("api/<slug:schema>/<slug:table>/calc/", calc_newcol, name="calc"),
    path("api/<slug:schema>/<slug:table>/aggregate/", aggregate_preview, name="aggregate"),
    path("api/<slug:schema>/<slug:table>/save/", save_table, name="save"),
]
