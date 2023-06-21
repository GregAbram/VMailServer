from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.get_vmail_list_html),

    path("add_vmail/", views.add_vmail),
    path("get_vmail/<str:uuid>/", views.get_vmail),

    path("insert_vmail_snapshot_after/<str:vmail>/<str:snapshot>/", views.insert_vmail_snapshot_after),
    
    path("get_first_snapshot_html/<str:vmail>/", views.get_first_snapshot_html),
    path("get_first_snapshot_json/<str:vmail>/", views.get_first_snapshot_json),
    path("get_last_snapshot_json/<str:vmail>/", views.get_last_snapshot_json),
    path("get_next_snapshot_json/<str:vmail>/<str:snapshot>/", views.get_next_snapshot_json),
    path("get_prev_snapshot_json/<str:vmail>/<str:snapshot>/", views.get_prev_snapshot_json),

    path("upload_media/<str:snapshot>/<str:ext>/", views.upload_media),
    path("upload_text/<str:snapshot>/", views.upload_text),

    path("get_vmail_list/", views.get_vmail_list),
    path("get_vmail_list_html/", views.get_vmail_list_html),
]
