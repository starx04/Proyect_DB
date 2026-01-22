/* Lógica para selectores de ubicación dinámicos */
document.addEventListener('DOMContentLoaded', function () {
    const provinciaSelect = document.getElementById('id_provincia');
    const ciudadSelect = document.getElementById('id_ciudad');

    if (provinciaSelect && ciudadSelect) {
        provinciaSelect.addEventListener('change', function () {
            const provinciaId = this.value;
            const url = '/locations/ajax/load-cities/';  // URL hardcoded o usar data-attribute

            fetch(`${url}?provincia_id=${provinciaId}`)
                .then(response => response.json())
                .then(data => {
                    ciudadSelect.innerHTML = '<option value="">---------</option>';
                    data.forEach(city => {
                        const option = document.createElement('option');
                        option.value = city.id;
                        option.textContent = city.nombre;
                        ciudadSelect.appendChild(option);
                    });
                })
                .catch(error => console.error('Error cargando ciudades:', error));
        });
    }
});
