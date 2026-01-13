# 🎯 Hot Wheels Scout

Una herramienta para encontrar las mejores tiendas donde buscar Hot Wheels, basada en análisis de tranquilidad y probabilidad de encontrar stock fresco.

## 🌟 Características

- **100% Gratis**: Usa OpenStreetMap API, sin necesidad de API keys ni tarjetas de crédito
- **Análisis Inteligente**: Calcula score de tranquilidad basado en múltiples factores
- **🔥 HOTLIST**: Base de datos actualizable de Hot Wheels 2024-2025 con clasificación automática
- **Búsqueda Avanzada**: Busca por JDM, Premium, Treasure Hunts, STH, marcas específicas
- **Sistema de Caché**: Guarda resultados por 7 días para consultas rápidas
- **Historial de Visitas**: Registra tus búsquedas y estadísticas de éxito
- **Plan de Ruta**: Sugiere el mejor orden para visitar tiendas
- **Personalizable**: Ajusta los pesos del algoritmo según tu experiencia

## 📋 Requisitos

```bash
pip install requests rich beautifulsoup4
```

## 🚀 Instalación

1. Descarga ambos archivos:
   - `hotwheels_scout_osm.py` (programa principal)
   - `hotwheels_database.py` (módulo de hotlist)

2. Instala dependencias:
```bash
pip install requests rich beautifulsoup4
```

3. Ejecuta:
```bash
python hotwheels_scout_osm.py
```

## 🎯 Cómo Funciona

El algoritmo analiza tiendas basándose en:

### Penalizaciones (reducen score):
- **Escuelas cercanas** (-15 puntos por escuela): Más gente = menos probabilidad
- **Avenida principal** (-10 puntos): Tiendas concurridas = revisadas frecuentemente
- **Rating alto** (-8 puntos): Popular = mucha gente
- **Muchas reseñas** (-12 puntos): Muy visitada = menos stock

### Bonificaciones (aumentan score):
- **Farmacias** (+20 puntos): Menos competencia por juguetes
- **Tienda aburrida** (+15 puntos): Poca gente = más oportunidades
- **Zona residencial** (+12 puntos): Menos tráfico de coleccionistas
- **Abre temprano** (+10 puntos): Ventaja de llegar primero

## 📊 Menú Principal

1. **🔍 Analizar tiendas**: Busca y analiza tiendas en tu área
2. **📊 Ver ranking completo**: Muestra todas las tiendas ordenadas por score
3. **🔥 Ver Hotlist**: Lista completa de Hot Wheels 2024-2025 con filtros
4. **📈 Estadísticas Hotlist**: Stats de JDM, Premium, TH, STH, marcas top
5. **🔎 Buscar en Hotlist**: Busca carritos específicos por nombre o marca
6. **⚙️ Ajustar pesos**: Personaliza el algoritmo según tu experiencia
7. **📅 Plan de ruta óptimo**: Sugiere mejor orden de visita
8. **📝 Registrar visita**: Guarda tus resultados de búsqueda
9. **📜 Ver historial**: Revisa tus visitas pasadas y estadísticas
10. **🔧 Configuración**: Cambia ubicación, radio, actualiza hotlist
11. **🗑️ Limpiar caché**: Fuerza nueva búsqueda de datos
12. **🚪 Salir**: Cierra la aplicación

## ⚙️ Configuración

### Cambiar tu ubicación

1. Ve a Google Maps
2. Haz click derecho en tu ubicación
3. Copia las coordenadas (aparecen como: 19.4326, -99.1332)
4. En el menú: Configuración → Cambiar ubicación

### Ajustar radio de búsqueda

Por defecto busca en 6 km a la redonda. Puedes ajustarlo en:
- Configuración → Cambiar radio de búsqueda

### Personalizar pesos

Si encuentras que ciertos factores son más/menos importantes en tu experiencia:
1. Menú → Ajustar pesos
2. Selecciona el factor a modificar
3. Ingresa el nuevo valor

## 💡 Tips de Uso

### La Hotlist - Qué Buscar

La Hotlist te muestra todos los Hot Wheels del lineup actual (2024-2025) con clasificación automática:

**Clasificaciones disponibles:**
- 🇯🇵 **JDM**: Nissan, Toyota, Honda, Mazda, etc.
- ⭐ **Premium**: Porsche, Ferrari, Lamborghini, McLaren, etc.
- 💪 **Muscle**: Camaro, Mustang, Challenger, Corvette, etc.
- 🏆 **TH**: Treasure Hunt
- 💎 **STH**: Super Treasure Hunt

**Filtros de búsqueda:**
- Ver todo el lineup completo
- Filtrar solo JDM para fans japoneses
- Solo Premium para exóticos
- Solo Treasure Hunts para cazadores
- Por marca específica (ej: "Porsche", "Honda")

**Ejemplo de entrada:**
```
199/250 FACTORY FRESH Porsche 911 GT3 [⭐Premium]
```

### Actualizar la Hotlist

Ve a Configuración → Actualizar Hotlist para obtener los datos más recientes del lineup oficial.

### Mejor momento para buscar
- **8:45 - 10:30 AM**: Menos gente, stock fresco de la noche
- **Martes/Miércoles**: Días más tranquilos que fines de semana

### Interpretación de Scores
- **70-100**: Excelente opción, alta probabilidad
- **50-69**: Buena opción, vale la pena intentar  
- **0-49**: Baja probabilidad, solo si estás cerca

### Registra tus visitas
Mantén un registro de tus búsquedas para:
- Ver qué tiendas funcionan mejor
- Calcular tu tasa de éxito
- Identificar patrones

## 🗂️ Archivos Generados

- `config.json`: Tu configuración personal
- `cache.json`: Caché de tiendas (válido 7 días)
- `history.json`: Historial de visitas
- `hotlist.json`: Base de datos de Hot Wheels 2024-2025

## 🔧 Solución de Problemas

### No encuentra tiendas
- Verifica tu ubicación en configuración
- Aumenta el radio de búsqueda
- Asegúrate de tener conexión a internet

### Error de API
- Espera unos segundos y reintenta
- La API de OpenStreetMap es gratis pero tiene límites de tasa
- El programa respeta automáticamente estos límites

### Caché desactualizado
- Usa la opción "Limpiar caché" para forzar nueva búsqueda
- El caché se renueva automáticamente después de 7 días

## 🌍 Datos de OpenStreetMap

Este proyecto usa datos de OpenStreetMap, una plataforma colaborativa de mapas:
- **Totalmente gratuito**
- **Sin límites estrictos**
- **Datos actualizados por la comunidad**

## 📝 Notas

- Los scores son estimaciones basadas en heurísticas
- Ajusta los pesos según tu experiencia local
- El éxito también depende de suerte y timing
- ¡Registra tus visitas para mejorar tus estrategias!

## 🎨 Créditos

Desarrollado para cazadores de Hot Wheels que quieren optimizar sus búsquedas.

---

**¡Feliz caza! 🎯🏎️**