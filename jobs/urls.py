from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # --- PANEL DE EMPRESA ---
    path('empresa/dashboard/', views.dashboard_empresa, name='dashboard_empresa'),
    path('empresa/perfil/editar/', views.editar_perfil_empresa, name='editar_perfil_empresa'),
    path('empresa/perfil/<int:empresa_id>/', views.perfil_publico_empresa, name='perfil_publico_empresa'),

    # --- GESTIÓN DE OFERTAS ---
    path('ofertas/crear/', views.crear_oferta, name='crear_oferta'),
    path('ofertas/editar/<int:oferta_id>/', views.editar_oferta, name='editar_oferta'),
    path('ofertas/eliminar/<int:oferta_id>/', views.eliminar_oferta, name='eliminar_oferta'),

    # --- GESTIÓN DE HABILIDADES ---
    path('ofertas/<int:oferta_id>/habilidades/', views.gestionar_habilidades, name='gestionar_habilidades'),
    path('habilidades/eliminar/<int:habilidad_id>/', views.eliminar_habilidad, name='eliminar_habilidad'),

<<<<<<< HEAD
    # --- FLUJO DE POSTULACIÓN (Candidato) ---
    path('', views.lista_ofertas, name='lista_ofertas'),
    path('oferta/<int:oferta_id>/', views.detallar_oferta, name='detallar_oferta'),
    path('oferta/<int:oferta_id>/postular/', views.postularse, name='postularse'),

    # --- GESTIÓN DE POSTULANTES (Empresa) ---
    path('empresa/oferta/<int:oferta_id>/postulantes/', views.ver_postulantes, name='ver_postulantes'),
    path('postulacion/<int:postulacion_id>/estado/', views.cambiar_estado_postulacion, name='cambiar_estado_postulacion'),
]
=======
    # --- POSTULACIONES ---
    path('ofertas/<int:oferta_id>/postular/', views.postular_oferta, name='postular_oferta'),
    path('ofertas/<int:oferta_id>/guardar/', views.guardar_oferta, name='guardar_oferta'),
    path('candidato/mis-postulaciones/', views.mis_postulaciones, name='mis_postulaciones'),

    # --- APLICANTES ---
    path('empresa/oferta/<int:oferta_id>/aplicantes/', views.gestion_aplicantes, name='gestion_aplicantes'),
]
>>>>>>> 2b27c6f510334cc8c614c95eaf1e687186ad6c70
