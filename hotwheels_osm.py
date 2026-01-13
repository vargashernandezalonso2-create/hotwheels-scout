import os
import json
import math
import requests
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
import time

# aaa importamos el módulo de database -bynd
import hotwheels_database as hwdb

console = Console()

# ey archivos de configuración -bynd
CONFIG_FILE = "config.json"
CACHE_FILE = "cache.json"
HISTORY_FILE = "history.json"

# chintrolas configuración por defecto -bynd
DEFAULT_CONFIG = {
    "location": {"lat": 19.4326, "lng": -99.1332},  # cdmx por defecto -bynd
    "radius": 6000,  # 6km en metros -bynd
    "weights": {
        "nearby_schools": -15,
        "on_main_avenue": -10,
        "high_rating": -8,
        "many_reviews": -12,
        "pharmacy_bonus": 20,
        "boring_vibe": 15,
        "early_opening": 10,
        "residential": 12
    }
}

def load_config():
    # chintrolas cargamos la config o creamos una nueva -bynd
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()

def save_config(config):
    # ey guardamos la configuración -bynd
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def load_cache():
    # aaa cargamos el caché si existe -bynd
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
            # verificamos si el caché no es muy viejo (7 días) -bynd
            cache_date = datetime.fromisoformat(cache.get("timestamp", "2000-01-01"))
            if datetime.now() - cache_date < timedelta(days=7):
                return cache
    return {"timestamp": datetime.now().isoformat(), "stores": [], "schools": []}

def save_cache(cache):
    # vavavava guardamos el caché -bynd
    cache["timestamp"] = datetime.now().isoformat()
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def load_history():
    # fokeis cargamos historial de visitas -bynd
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_history(history):
    # ey guardamos historial -bynd
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def add_visit_to_history(store_name, found_hotwheels):
    # aaa agregamos visita al historial -bynd
    history = load_history()
    history.append({
        "store": store_name,
        "date": datetime.now().isoformat(),
        "found_hotwheels": found_hotwheels
    })
    save_history(history)

def fetch_osm_places(location, radius, amenity_types):
    # q chidoteee buscamos lugares con Overpass API -bynd
    # ey esta es la API gratis de OpenStreetMap -bynd
    
    url = "https://overpass-api.de/api/interpreter"
    
    # aaa armamos la query de Overpass QL -bynd
    lat, lng = location['lat'], location['lng']
    
    # chintrolas construimos filtros para cada tipo -bynd
    filters = []
    for amenity in amenity_types:
        filters.append(f'node["shop"="{amenity}"](around:{radius},{lat},{lng});')
        filters.append(f'way["shop"="{amenity}"](around:{radius},{lat},{lng});')
    
    query = f"""
    [out:json][timeout:25];
    (
      {' '.join(filters)}
    );
    out body;
    >;
    out skel qt;
    """
    
    try:
        response = requests.post(url, data={"data": query}, timeout=30)
        response.raise_for_status()
        return response.json().get("elements", [])
    except Exception as e:
        console.print(f"[red]Error al buscar lugares: {e}[/red]")
        return []

def fetch_osm_schools(location, radius=1000):
    # vavavava buscamos escuelas cercanas -bynd
    url = "https://overpass-api.de/api/interpreter"
    
    lat, lng = location['lat'], location['lng']
    
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="school"](around:{radius},{lat},{lng});
      way["amenity"="school"](around:{radius},{lat},{lng});
    );
    out body;
    """
    
    try:
        response = requests.post(url, data={"data": query}, timeout=30)
        response.raise_for_status()
        return response.json().get("elements", [])
    except Exception as e:
        console.print(f"[red]Error al buscar escuelas: {e}[/red]")
        return []

def count_nearby_schools(location, radius=1000):
    # ey contamos cuántas escuelas hay cerca -bynd
    schools = fetch_osm_schools(location, radius)
    return len(schools)

def calculate_distance(loc1, loc2):
    # chintrolas calculamos distancia entre dos puntos -bynd
    # usando fórmula de haversine -bynd
    lat1, lon1 = loc1["lat"], loc1["lng"]
    lat2, lon2 = loc2["lat"], loc2["lng"]
    
    R = 6371  # radio de la tierra en km -bynd
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def get_element_location(element):
    # aaa extraemos ubicación de un elemento OSM -bynd
    if 'lat' in element and 'lon' in element:
        return {"lat": element['lat'], "lng": element['lon']}
    elif 'center' in element:
        return {"lat": element['center']['lat'], "lng": element['center']['lon']}
    return None

def get_element_name(element):
    # ey sacamos el nombre del elemento -bynd
    tags = element.get('tags', {})
    return tags.get('name', tags.get('brand', 'Sin nombre'))

def analyze_store(store, config):
    # aaa analizamos una tienda específica -bynd
    location = get_element_location(store)
    
    if not location:
        return None
    
    # contamos escuelas cercanas -bynd
    nearby_schools = count_nearby_schools(location)
    
    # chintrolas inferimos tipo de tienda -bynd
    tags = store.get('tags', {})
    shop_type = tags.get('shop', 'supermarket')
    
    store_type = "supermarket"
    if shop_type in ["chemist", "pharmacy"]:
        store_type = "pharmacy"
    elif shop_type in ["department_store", "mall"]:
        store_type = "department_store"
    
    # ey estimamos rating basado en si tiene nombre conocido -bynd
    name = get_element_name(store).lower()
    brand_names = ["walmart", "chedraui", "soriana", "bodega", "farmacia guadalajara", "ahorro"]
    rating = 4.0 if any(brand in name for brand in brand_names) else 3.5
    
    # fokeis estimamos reviews basado en el tipo -bynd
    reviews = 500 if store_type == "pharmacy" else 300
    if any(brand in name for brand in ["walmart", "chedraui"]):
        reviews = 1200
    
    # vavavava inferimos el vibe -bynd
    if nearby_schools < 2:
        store_vibe = "residential"
    elif reviews < 400:
        store_vibe = "boring"
    else:
        store_vibe = "busy"
    
    return {
        "osm_id": store.get("id"),
        "name": get_element_name(store),
        "type": store_type,
        "location": location,
        "rating": rating,
        "user_ratings_total": reviews,
        "nearby_schools": nearby_schools,
        "on_main_avenue": reviews > 500,
        "opening_hour": 8,
        "store_vibe": store_vibe,
        "distance_km": calculate_distance(config["location"], location)
    }

def calculate_tranquility_score(store, weights):
    # ey aquí calculamos el score de tranquilidad -bynd
    score = 50  # empezamos en 50 base -bynd
    
    # penalizaciones -bynd
    score += store["nearby_schools"] * weights["nearby_schools"]
    
    if store["on_main_avenue"]:
        score += weights["on_main_avenue"]
    
    if store["rating"] > 4.0:
        score += weights["high_rating"]
    
    if store["user_ratings_total"] > 1000:
        score += weights["many_reviews"]
    
    # bonificaciones -bynd
    if store["type"] == "pharmacy":
        score += weights["pharmacy_bonus"]
    
    if store["store_vibe"] == "boring":
        score += weights["boring_vibe"]
    
    if store["store_vibe"] == "residential":
        score += weights["residential"]
    
    if store["opening_hour"] <= 7:
        score += weights["early_opening"]
    
    # aaa mantenemos el score entre 0 y 100 -bynd
    return max(0, min(100, int(score)))

def show_header():
    # q chidoteee el header -bynd
    header = Text()
    header.append("🎯 HOT WHEELS SCOUT 🎯", style="bold cyan")
    console.print(Panel(header, border_style="cyan"))
    console.print()

def show_main_menu():
    # vavavava el menú principal -bynd
    console.print("[bold yellow]OPCIONES:[/bold yellow]")
    console.print("[1] 🔍 Analizar tiendas")
    console.print("[2] 📊 Ver ranking completo")
    console.print("[3] 🔥 Ver Hotlist (qué buscar)")
    console.print("[4] 📈 Estadísticas Hotlist")
    console.print("[5] 🔎 Buscar en Hotlist")
    console.print("[6] ⚙️  Ajustar pesos")
    console.print("[7] 📅 Plan de ruta óptimo")
    console.print("[8] 📝 Registrar visita")
    console.print("[9] 📜 Ver historial")
    console.print("[10] 🔧 Configuración")
    console.print("[11] 🗑️  Limpiar caché")
    console.print("[12] 🚪 Salir")
    console.print()

def fetch_and_analyze_stores(config, use_cache=True):
    # chintrolas función principal para buscar y analizar -bynd
    
    # ey primero intentamos usar caché -bynd
    if use_cache:
        cache = load_cache()
        if cache["stores"]:
            console.print("[dim]📦 Usando datos en caché...[/dim]")
            return cache["stores"]
    
    console.print("[yellow]🔍 Buscando tiendas en OpenStreetMap...[/yellow]")
    console.print("[dim]💚 100% Gratis, sin API key necesaria[/dim]\n")
    
    # aaa definimos tipos de tiendas que buscamos -bynd
    amenity_types = ["supermarket", "convenience", "chemist", "pharmacy", "department_store"]
    
    console.print("[cyan]Consultando Overpass API...[/cyan]")
    stores_data = fetch_osm_places(config["location"], config["radius"], amenity_types)
    
    if not stores_data:
        console.print("[red]No se encontraron tiendas. Intenta aumentar el radio.[/red]")
        input("\nPresiona Enter para continuar...")
        return []
    
    console.print(f"[green]✓[/green] {len(stores_data)} lugares encontrados")
    console.print("[yellow]🏫 Analizando escuelas cercanas...[/yellow]")
    
    # aaa analizamos cada tienda -bynd
    analyzed_stores = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("[cyan]Analizando tiendas...", total=len(stores_data))
        
        for store in stores_data:
            analyzed = analyze_store(store, config)
            if analyzed:  # fokeis algunos elementos pueden no tener ubicación -bynd
                analyzed["score"] = calculate_tranquility_score(analyzed, config["weights"])
                analyzed_stores.append(analyzed)
            progress.update(task, advance=1)
            time.sleep(0.1)  # ey respetamos la API -bynd
    
    # vavavava ordenamos por score -bynd
    analyzed_stores.sort(key=lambda x: x["score"], reverse=True)
    
    # guardamos en caché -bynd
    save_cache({"stores": analyzed_stores})
    
    return analyzed_stores

def analyze_stores(config):
    # ey función principal de análisis -bynd
    console.clear()
    show_header()
    
    scored_stores = fetch_and_analyze_stores(config)
    
    if not scored_stores:
        return []
    
    console.print("\n[green]✓ Análisis completado[/green]\n")
    
    # chintrolas mostramos top 3 -bynd
    table = Table(title="🏆 MEJORES OPCIONES HOY", border_style="green")
    table.add_column("Pos", style="cyan", justify="center")
    table.add_column("Tienda", style="magenta")
    table.add_column("Score", justify="center", style="green")
    table.add_column("Distancia", justify="center")
    table.add_column("Razón Principal", style="yellow")
    
    for i, store in enumerate(scored_stores[:3], 1):
        reason = get_main_reason(store)
        score_color = "green" if store["score"] >= 70 else "yellow" if store["score"] >= 50 else "red"
        table.add_row(
            f"{i}",
            store["name"],
            f"[{score_color}]{store['score']}[/{score_color}]",
            f"{store['distance_km']:.1f} km",
            reason
        )
    
    console.print(table)
    console.print()
    
    # fokeis alerta si hoy no vale la pena -bynd
    if scored_stores[0]["score"] < 60:
        console.print(Panel(
            "[red]⚠️  HOY NO ES BUEN DÍA[/red]\nTodas las tiendas tienen score bajo.\nMejor espera a otro día 😿",
            border_style="red"
        ))
    
    console.print()
    input("Presiona Enter para continuar...")
    return scored_stores

def get_main_reason(store):
    # ey aquí explicamos por qué una tienda es buena -bynd
    reasons = []
    
    if store["type"] == "pharmacy":
        reasons.append("Es farmacia")
    
    if store["nearby_schools"] == 0:
        reasons.append("0 escuelas cerca")
    
    if not store["on_main_avenue"]:
        reasons.append("No en avenida")
    
    if store["store_vibe"] == "boring":
        reasons.append("Tienda aburrida")
    
    if store["store_vibe"] == "residential":
        reasons.append("Zona residencial")
    
    return ", ".join(reasons[:2]) if reasons else "Varias razones"

def show_full_ranking(scored_stores):
    # vavavava ranking completo -bynd
    console.clear()
    show_header()
    
    if not scored_stores:
        console.print("[yellow]No hay datos disponibles. Analiza tiendas primero (opción 1)[/yellow]")
        input("\nPresiona Enter para continuar...")
        return
    
    table = Table(title="📊 RANKING COMPLETO", border_style="blue")
    table.add_column("#", style="cyan", justify="center")
    table.add_column("Tienda", style="magenta")
    table.add_column("Tipo", style="blue")
    table.add_column("Score", justify="center")
    table.add_column("Dist", justify="center")
    table.add_column("Escuelas", justify="center")
    table.add_column("Rating", justify="center")
    
    for i, store in enumerate(scored_stores, 1):
        score_color = "green" if store["score"] >= 70 else "yellow" if store["score"] >= 50 else "red"
        table.add_row(
            f"{i}",
            store["name"][:30],
            store["type"][:10],
            f"[{score_color}]{store['score']}[/{score_color}]",
            f"{store['distance_km']:.1f}km",
            f"{'⚠️' if store['nearby_schools'] > 2 else ''}{store['nearby_schools']}",
            f"{store['rating']}⭐"
        )
    
    console.print(table)
    console.print()
    input("Presiona Enter para continuar...")

def view_hotlist():
    # q chidoteee mostramos la hotlist -bynd
    console.clear()
    show_header()
    
    hotlist = hwdb.load_hotlist()
    
    if not hotlist:
        console.print("[yellow]No hay hotlist generada[/yellow]")
        if Confirm.ask("¿Quieres generar la hotlist ahora?"):
            hotlist = hwdb.build_hotlist()
        else:
            input("\nPresiona Enter para continuar...")
            return
    
    console.print("[bold cyan]🔥 HOTLIST - QUÉ BUSCAR EN LAS TIENDAS[/bold cyan]\n")
    console.print(f"[dim]Total: {len(hotlist)} carritos[/dim]\n")
    
    # aaa filtros disponibles -bynd
    console.print("[yellow]Filtros:[/yellow]")
    console.print("[1] Ver todo")
    console.print("[2] Solo JDM 🇯🇵")
    console.print("[3] Solo Premium ⭐")
    console.print("[4] Solo Treasure Hunts 🏆")
    console.print("[5] Solo STH 💎")
    console.print("[6] Por marca")
    console.print()
    
    filter_choice = Prompt.ask("Filtro", choices=["1", "2", "3", "4", "5", "6"])
    
    filtered_list = hotlist
    
    if filter_choice == "2":
        filtered_list = [c for c in hotlist if c["is_jdm"]]
    elif filter_choice == "3":
        filtered_list = [c for c in hotlist if c["is_premium"]]
    elif filter_choice == "4":
        filtered_list = [c for c in hotlist if c["is_th"] or c["is_sth"]]
    elif filter_choice == "5":
        filtered_list = [c for c in hotlist if c["is_sth"]]
    elif filter_choice == "6":
        brand = Prompt.ask("Nombre de marca")
        filtered_list = [c for c in hotlist if brand.lower() in c["brand"].lower()]
    
    if not filtered_list:
        console.print("[red]No se encontraron resultados con ese filtro[/red]")
        input("\nPresiona Enter para continuar...")
        return
    
    # chintrolas mostramos la tabla -bynd
    table = Table(title=f"🔥 HOTLIST ({len(filtered_list)} resultados)", border_style="cyan")
    table.add_column("#", style="cyan", justify="center", width=8)
    table.add_column("Serie", style="blue", width=18)
    table.add_column("Nombre", style="magenta", width=35)
    table.add_column("Tags", style="yellow", width=25)
    
    for car in filtered_list[:50]:  # fokeis solo primeros 50 -bynd
        tags = []
        if car["is_sth"]:
            tags.append("💎STH")
        elif car["is_th"]:
            tags.append("🏆TH")
        if car["is_jdm"]:
            tags.append("🇯🇵JDM")
        if car["is_premium"]:
            tags.append("⭐Premium")
        
        table.add_row(
            car["number"],
            car["series"][:18],
            car["name"][:35],
            " ".join(tags)
        )
    
    console.print(table)
    
    if len(filtered_list) > 50:
        console.print(f"\n[dim]Mostrando primeros 50 de {len(filtered_list)}[/dim]")
    
    console.print()
    input("Presiona Enter para continuar...")

def search_in_hotlist():
    # ey búsqueda en la hotlist -bynd
    console.clear()
    show_header()
    
    hotlist = hwdb.load_hotlist()
    
    if not hotlist:
        console.print("[yellow]No hay hotlist. Genera una primero (opción 3)[/yellow]")
        input("\nPresiona Enter para continuar...")
        return
    
    console.print("[bold cyan]🔎 BUSCAR EN HOTLIST[/bold cyan]\n")
    
    query = Prompt.ask("Buscar (nombre o marca)")
    
    results = hwdb.search_hotlist(query)
    
    if not results:
        console.print(f"\n[red]No se encontró '{query}'[/red]")
        input("\nPresiona Enter para continuar...")
        return
    
    console.print(f"\n[green]✓ {len(results)} resultados[/green]\n")
    
    for car in results[:20]:
        console.print(hwdb.format_hotlist_entry(car))
    
    if len(results) > 20:
        console.print(f"\n[dim]Mostrando primeros 20 de {len(results)}[/dim]")
    
    console.print()
    input("Presiona Enter para continuar...")

def show_route_plan(scored_stores):
    # ey aquí armamos el plan óptimo -bynd
    console.clear()
    show_header()
    
    if not scored_stores:
        console.print("[yellow]No hay datos disponibles. Analiza tiendas primero (opción 1)[/yellow]")
        input("\nPresiona Enter para continuar...")
        return
    
    now = datetime.now()
    day_name = now.strftime("%A")
    
    # aaa solo mostramos top 3 para no hacer ruta muy larga -bynd
    best_stores = scored_stores[:3]
    
    console.print(Panel(
        f"[bold cyan]PLAN DE RUTA ÓPTIMO[/bold cyan]\n"
        f"📅 Día: {day_name}\n"
        f"⏰ Hora sugerida: 8:45 - 10:30",
        border_style="cyan"
    ))
    console.print()
    
    total_distance = sum(store["distance_km"] for store in best_stores)
    
    for i, store in enumerate(best_stores, 1):
        console.print(f"[bold yellow]{i}️⃣  {store['name']}[/bold yellow]")
        console.print(f"   Score: [green]{store['score']}[/green]")
        console.print(f"   Distancia: {store['distance_km']:.1f} km")
        console.print(f"   Motivo: {get_main_reason(store)}")
        console.print(f"   Abre: {store['opening_hour']}:00 AM")
        console.print()
    
    console.print(f"[bold]Distancia total aproximada: {total_distance:.1f} km[/bold]")
    console.print("[dim]💡 Tip: Visita en este orden para optimizar ruta[/dim]")
    console.print()
    input("Presiona Enter para continuar...")

def register_visit(scored_stores):
    # chintrolas registramos una visita -bynd
    console.clear()
    show_header()
    
    if not scored_stores:
        console.print("[yellow]No hay tiendas analizadas aún[/yellow]")
        input("\nPresiona Enter para continuar...")
        return
    
    console.print("[bold]Selecciona la tienda que visitaste:[/bold]\n")
    
    for i, store in enumerate(scored_stores[:10], 1):
        console.print(f"[{i}] {store['name']}")
    
    console.print("[0] Otra tienda")
    console.print()
    
    choice = IntPrompt.ask("Número de tienda", default=0)
    
    if choice > 0 and choice <= min(10, len(scored_stores)):
        store_name = scored_stores[choice - 1]["name"]
    else:
        store_name = Prompt.ask("Nombre de la tienda")
    
    found = Confirm.ask("¿Encontraste Hot Wheels?")
    
    add_visit_to_history(store_name, found)
    
    emoji = "🎉" if found else "😿"
    console.print(f"\n[green]{emoji} Visita registrada[/green]")
    input("\nPresiona Enter para continuar...")

def show_history():
    # ey mostramos historial de visitas -bynd
    console.clear()
    show_header()
    
    history = load_history()
    
    if not history:
        console.print("[yellow]No hay visitas registradas aún[/yellow]")
        input("\nPresiona Enter para continuar...")
        return
    
    table = Table(title="📜 HISTORIAL DE VISITAS", border_style="purple")
    table.add_column("Fecha", style="cyan")
    table.add_column("Tienda", style="magenta")
    table.add_column("Resultado", justify="center")
    
    for visit in history[-20:]:  # aaa últimas 20 visitas -bynd
        date = datetime.fromisoformat(visit["date"]).strftime("%Y-%m-%d %H:%M")
        result = "[green]✓ Encontró[/green]" if visit["found_hotwheels"] else "[red]✗ No encontró[/red]"
        table.add_row(date, visit["store"], result)
    
    console.print(table)
    console.print()
    
    # vavavava estadísticas -bynd
    total = len(history)
    found = sum(1 for v in history if v["found_hotwheels"])
    rate = (found / total * 100) if total > 0 else 0
    
    console.print(f"[bold]Estadísticas:[/bold]")
    console.print(f"Total de visitas: {total}")
    console.print(f"Encontrados: {found} ({rate:.1f}%)")
    console.print()
    input("Presiona Enter para continuar...")

def adjust_weights(config):
    # chintrolas aquí ajustamos los pesos -bynd
    console.clear()
    show_header()
    
    console.print("[yellow]⚙️  AJUSTAR PESOS DEL ALGORITMO[/yellow]")
    console.print()
    console.print("[dim]Valores negativos = penalización, positivos = bonificación[/dim]")
    console.print()
    
    weights = config["weights"]
    
    table = Table(border_style="blue")
    table.add_column("#", style="cyan", justify="center")
    table.add_column("Factor", style="yellow")
    table.add_column("Peso Actual", justify="center", style="green")
    
    weight_keys = list(weights.keys())
    for i, key in enumerate(weight_keys, 1):
        table.add_row(
            str(i),
            key.replace("_", " ").title(),
            str(weights[key])
        )
    
    console.print(table)
    console.print()
    
    if Confirm.ask("¿Quieres ajustar algún peso?"):
        choice = IntPrompt.ask("¿Cuál? (1-8)", choices=[str(i) for i in range(1, 9)])
        key = weight_keys[choice - 1]
        
        current = weights[key]
        console.print(f"\n[yellow]Peso actual de '{key}': {current}[/yellow]")
        new_value = IntPrompt.ask("Nuevo valor", default=current)
        
        weights[key] = new_value
        save_config(config)
        
        console.print(f"\n[green]✓ Peso actualizado[/green]")
    
    input("\nPresiona Enter para continuar...")

def show_settings(config):
    # ey pantalla de configuración -bynd
    console.clear()
    show_header()
    
    console.print("[bold yellow]🔧 CONFIGURACIÓN[/bold yellow]\n")
    
    console.print("[green]✓ Usando OpenStreetMap (Gratis)[/green]")
    console.print(f"Ubicación: {config['location']['lat']:.4f}, {config['location']['lng']:.4f}")
    console.print(f"Radio: {config['radius']/1000:.1f} km")
    console.print()
    
    console.print("[1] Cambiar ubicación")
    console.print("[2] Cambiar radio de búsqueda")
    console.print("[3] Actualizar Hotlist")
    console.print("[4] Volver")
    console.print()
    
    choice = Prompt.ask("Opción", choices=["1", "2", "3", "4"])
    
    if choice == "1":
        console.print("\n[yellow]Ingresa nueva ubicación:[/yellow]")
        lat = float(Prompt.ask("Latitud", default=str(config['location']['lat'])))
        lng = float(Prompt.ask("Longitud", default=str(config['location']['lng'])))
        config["location"] = {"lat": lat, "lng": lng}
        save_config(config)
        console.print("[green]✓ Ubicación actualizada[/green]")
        
    elif choice == "2":
        radius_km = IntPrompt.ask("Radio en km", default=int(config['radius']/1000))
        config["radius"] = radius_km * 1000
        save_config(config)
        console.print("[green]✓ Radio actualizado[/green]")
        
    elif choice == "3":
        hwdb.build_hotlist()
    
    if choice != "4":
        input("\nPresiona Enter para continuar...")

def clear_cache():
    # fokeis limpiamos el caché -bynd
    console.clear()
    show_header()
    
    if Confirm.ask("¿Seguro que quieres limpiar el caché?"):
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        console.print("\n[green]✓ Caché eliminado[/green]")
    
    input("\nPresiona Enter para continuar...")

def main():
    # vavavava función principal -bynd
    config = load_config()
    scored_stores = []
    
    while True:
        console.clear()
        show_header()
        
        console.print(f"[dim]📍 Ubicación: {config['location']['lat']:.4f}, {config['location']['lng']:.4f}[/dim]")
        console.print(f"[dim]📏 Radio: {config['radius']/1000:.1f} km[/dim]")
        console.print(f"[dim]💚 OpenStreetMap API (100% Gratis)[/dim]")
        console.print()
        
        show_main_menu()
        
        choice = Prompt.ask("Elige opción", choices=[str(i) for i in range(1, 13)])
        
        if choice == "1":
            scored_stores = analyze_stores(config)
        elif choice == "2":
            show_full_ranking(scored_stores)
        elif choice == "3":
            view_hotlist()
        elif choice == "4":
            hwdb.show_hotlist_stats()
        elif choice == "5":
            search_in_hotlist()
        elif choice == "6":
            adjust_weights(config)
        elif choice == "7":
            show_route_plan(scored_stores)
        elif choice == "8":
            register_visit(scored_stores)
        elif choice == "9":
            show_history()
        elif choice == "10":
            show_settings(config)
        elif choice == "11":
            clear_cache()
        elif choice == "12":
            console.print("\n[cyan]Bye! 😸[/cyan]\n")
            break

if __name__ == "__main__":
    main()