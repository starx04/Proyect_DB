from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'bolsa_empleo'

urlpatterns = [
    # ==================== HOME ====================
    path('', views.home_view, name='home'),
    
    # ==================== AUTENTICACIÓN ====================
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

    # ==================== CANDIDATOS ====================
    path('candidato/dashboard/', views.dashboard_candidato, name='dashboard_candidato'),
    path('candidato/perfil/editar/', views.perfil_candidato_step, name='editar_perfil'),
    path('candidato/perfil/<int:paso>/', views.wizard_perfil, name='wizard_perfil'),
    path('candidato/perfil/subir-cv/', views.subir_cv_view, name='subir_cv'),
    path('candidato/perfil/publico/<int:candidato_id>/', views.perfil_publico_candidato, name='perfil_publico_candidato'),
    path('candidato/mis-postulaciones/', views.mis_postulaciones, name='mis_postulaciones'),

    # ==================== EMPRESAS ====================
    path('empresa/dashboard/', views.dashboard_empresa, name='dashboard_empresa'),
    path('empresa/perfil/editar/', views.editar_perfil_empresa, name='editar_perfil_empresa'),
    path('empresa/perfil/<int:empresa_id>/', views.perfil_publico_empresa, name='perfil_publico_empresa'),

    # ==================== OFERTAS DE EMPLEO ====================
    path('ofertas/', views.lista_ofertas, name='lista_ofertas'),
    path('ofertas/crear/', views.crear_oferta, name='crear_oferta'),
    path('ofertas/<int:oferta_id>/', views.detallar_oferta, name='detallar_oferta'),
    path('ofertas/<int:oferta_id>/editar/', views.editar_oferta, name='editar_oferta'),
    path('ofertas/<int:oferta_id>/eliminar/', views.eliminar_oferta, name='eliminar_oferta'),
    path('ofertas/<int:oferta_id>/habilidades/', views.gestionar_habilidades, name='gestionar_habilidades'),
    path('ofertas/<int:oferta_id>/guardar/', views.guardar_oferta, name='guardar_oferta'),
    path('ofertas/<int:oferta_id>/postular/', views.postularse, name='postularse'),

    # ==================== HABILIDADES ====================
    path('habilidades/eliminar/<int:habilidad_id>/', views.eliminar_habilidad, name='eliminar_habilidad'),

    # ==================== POSTULACIONES ====================
    path('empresa/oferta/<int:oferta_id>/postulantes/', views.ver_postulantes, name='ver_postulantes'),
    path('postulacion/<int:postulacion_id>/estado/', views.cambiar_estado_postulacion, name='cambiar_estado_postulacion'),

    # ==================== UBICACIÓN (AJAX) ====================
    path('ajax/load-cities/', views.load_cities, name='ajax_load_cities'),
]
