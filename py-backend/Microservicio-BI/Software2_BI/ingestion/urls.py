from django.urls import path
from . import views 
from .views import (
    # Vistas existentes
    upload_dataset_view, list_sources_view, chart_view, user_data_summary_view, 
    delete_source, download_schema, prueba_chat_view, enviar_email_view,
    # Nuevas vistas para diagramas
    dashboard_view, chat_integrado_view, guardar_diagrama_view, 
    listar_diagramas_view, eliminar_diagrama_view, actualizar_diagrama_view, analyze_chart_view, drag_drop_view, dragdrop_run_api, dragdrop_schema_api, descargar_excel_view
)
from  .api_views import (api_list_datasets, diagramas_por_data_source)

app_name = "ingestion"
urlpatterns = [
    # URLs existentes (sin cambios)
    path("upload/", upload_dataset_view, name="upload"),
    path("list/", list_sources_view, name="list"),
    path("chart/<int:source_id>/", chart_view, name="chart"),
    path("summary/", user_data_summary_view, name="user_summary"), 
    path("delete-source/<int:source_id>/", delete_source, name="delete_source"),
    path("download-schema/<int:source_id>/", download_schema, name="download_schema"),

    path("prueba/", prueba_chat_view, name="prueba_chat"),
    path("enviar-email/", enviar_email_view, name="enviar_email"),
    
    # NUEVAS URLs para sistema de diagramas
    path("dashboard/<int:source_id>/", dashboard_view, name="dashboard_view"),
    path("api/chat-integrado/", chat_integrado_view, name="chat_integrado"),
    path("api/guardar-diagrama/", guardar_diagrama_view, name="guardar_diagrama"),
    path("diagramas/<int:source_id>/", listar_diagramas_view, name="listar_diagramas"),
    path("eliminar-diagrama/<int:diagrama_id>/", eliminar_diagrama_view, name="eliminar_diagrama"),
    path("api/actualizar-diagrama/<int:diagrama_id>/", actualizar_diagrama_view, name="actualizar_diagrama"),

    path("analyze-chart/", analyze_chart_view, name="analyze_chart"),
    path("api/datasets/<int:user_id>/", api_list_datasets, name="api_list_datasets"),
    
    path("drag-drop/<int:source_id>/", drag_drop_view, name="drag_drop"),
    path("drag-drop/<int:source_id>/schema/", dragdrop_schema_api, name="dragdrop_schema_api"),
    path("drag-drop/run/", dragdrop_run_api, name="dragdrop_run_api"),

    path(
        "api/diagramas/<int:data_source_id>/",
        diagramas_por_data_source,
        name="diagramas_por_data_source",
    ),
    path("descargar/<str:schema>/", descargar_excel_view, name="descargar_excel"),
    path('download-schema/<int:source_id>/', views.download_schema, name='download_schema'),

]

