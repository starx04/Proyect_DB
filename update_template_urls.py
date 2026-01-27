import os
import re

# Directorio de templates
templates_dir = r"c:\Proyect_DB\templates"

# Patrones a reemplazar
replacements = [
    # URLs de accounts
    (r"{% url 'registro'", r"{% url 'bolsa_empleo:registro'"),
    (r"{% url 'login'", r"{% url 'bolsa_empleo:login'"),
    (r"{% url 'logout'", r"{% url 'bolsa_empleo:logout'"),
    (r"{% url 'dashboard_candidato'", r"{% url 'bolsa_empleo:dashboard_candidato'"),
    (r"{% url 'wizard_perfil'", r"{% url 'bolsa_empleo:wizard_perfil'"),
    (r"{% url 'editar_perfil'", r"{% url 'bolsa_empleo:editar_perfil'"),
    (r"{% url 'perfil_publico_candidato'", r"{% url 'bolsa_empleo:perfil_publico_candidato'"),
    (r"{% url 'subir_cv'", r"{% url 'bolsa_empleo:subir_cv'"),
    
    # URLs de jobs con jobs:
    (r"{% url 'jobs:dashboard_empresa'", r"{% url 'bolsa_empleo:dashboard_empresa'"),
    (r"{% url 'jobs:editar_perfil_empresa'", r"{% url 'bolsa_empleo:editar_perfil_empresa'"),
    (r"{% url 'jobs:perfil_publico_empresa'", r"{% url 'bolsa_empleo:perfil_publico_empresa'"),
    (r"{% url 'jobs:crear_oferta'", r"{% url 'bolsa_empleo:crear_oferta'"),
    (r"{% url 'jobs:editar_oferta'", r"{% url 'bolsa_empleo:editar_oferta'"),
    (r"{% url 'jobs:eliminar_oferta'", r"{% url 'bolsa_empleo:eliminar_oferta'"),
    (r"{% url 'jobs:gestionar_habilidades'", r"{% url 'bolsa_empleo:gestionar_habilidades'"),
    (r"{% url 'jobs:eliminar_habilidad'", r"{% url 'bolsa_empleo:eliminar_habilidad'"),
    (r"{% url 'jobs:lista_ofertas'", r"{% url 'bolsa_empleo:lista_ofertas'"),
    (r"{% url 'jobs:detallar_oferta'", r"{% url 'bolsa_empleo:detallar_oferta'"),
    (r"{% url 'jobs:postularse'", r"{% url 'bolsa_empleo:postularse'"),
    (r"{% url 'jobs:guardar_oferta'", r"{% url 'bolsa_empleo:guardar_oferta'"),
    (r"{% url 'jobs:mis_postulaciones'", r"{% url 'bolsa_empleo:mis_postulaciones'"),
    (r"{% url 'jobs:ver_postulantes'", r"{% url 'bolsa_empleo:ver_postulantes'"),
    (r"{% url 'jobs:cambiar_estado_postulacion'", r"{% url 'bolsa_empleo:cambiar_estado_postulacion'"),
    
    # Actualizar rutas de templates
    (r"'accounts/", r"'bolsa_empleo/auth/"),
    (r"'candidatoPerfil/", r"'bolsa_empleo/candidato/"),
    (r"'jobs/", r"'bolsa_empleo/ofertas/"),
    (r'"accounts/', r'"bolsa_empleo/auth/'),
    (r'"candidatoPerfil/', r'"bolsa_empleo/candidato/wizard/'),
    (r'"jobs/', r'"bolsa_empleo/'),
]

def update_file(filepath):
    """Actualiza las referencias de URLs en un archivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Aplicar todos los reemplazos
        for pattern, replacement in replacements:
            content = content.replace(pattern, replacement)
        
        # Si hubo cambios, guardar el archivo
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
    except Exception as e:
        print(f"Error procesando {filepath}: {e}")
        return False

def process_directory(directory):
    """Procesa todos los archivos HTML en un directorio recursivamente"""
    updated_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                if update_file(filepath):
                    updated_files.append(filepath)
                    print(f"[OK] Actualizado: {filepath}")
    
    return updated_files

if __name__ == '__main__':
    print("Actualizando referencias de URLs en templates...")
    updated = process_directory(templates_dir)
    print(f"\n[OK] Completado! {len(updated)} archivos actualizados.")
