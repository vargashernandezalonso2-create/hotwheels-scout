import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# aaa archivo para guardar la database -bynd
HOTLIST_FILE = "hotlist.json"

# ey marcas JDM -bynd
JDM_BRANDS = [
    "nissan", "skyline", "gtr", "silvia", "fairlady", "datsun",
    "toyota", "supra", "ae86", "celica", "mr2", "trueno",
    "honda", "civic", "nsx", "integra", "s2000", "crx",
    "mazda", "rx-7", "rx7", "miata", "mx-5", "rx-8",
    "subaru", "wrx", "sti", "brz",
    "mitsubishi", "evo", "lancer", "eclipse", "3000gt",
    "acura", "lexus"
]

# vavavava marcas premium -bynd
PREMIUM_BRANDS = [
    "porsche", "ferrari", "lamborghini", "mclaren", "bugatti",
    "koenigsegg", "pagani", "aston martin", "bentley", "rolls-royce"
]

# chintrolas marcas muscle -bynd
MUSCLE_BRANDS = [
    "camaro", "mustang", "challenger", "charger", "cuda", "barracuda",
    "corvette", "firebird", "trans am", "gto", "chevelle", "impala"
]

def fetch_2024_lineup():
    # q chidoteee scrapeamos el lineup 2024 -bynd
    console.print("[yellow]🔍 Descargando lineup 2024 de Hot Wheels...[/yellow]")
    
    url = "https://hwcollectorsnews.com/2024-hot-wheels-mainline-by-number/"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # aaa buscamos el contenido -bynd
        content = soup.find('div', class_='entry-content')
        if not content:
            console.print("[red]No se pudo encontrar el contenido[/red]")
            return []
        
        cars = []
        lines = content.get_text().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # ey parseamos cada línea -bynd
            # formato: "199 Porsche 911 GT3 – – – FACTORY FRESH"
            match = re.match(r'^(\d+)\s+(.+?)\s+–\s+–\s+–\s+(.+)$', line)
            if match:
                number = match.group(1)
                name = match.group(2).strip()
                series = match.group(3).strip()
                
                # chintrolas detectamos TH y STH -bynd
                is_th = "Treasure Hunt" in line
                is_sth = "$uper Treasure Hunt" in line or "Super Treasure Hunt" in line
                
                # fokeis limpiamos el nombre -bynd
                name = name.replace('![$uper Treasure Hunt]', '').replace('![Treasure Hunt]', '').strip()
                
                cars.append({
                    "number": number,
                    "name": name,
                    "series": series,
                    "year": 2024,
                    "is_th": is_th,
                    "is_sth": is_sth
                })
        
        return cars
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return []

def fetch_2025_lineup():
    # vavavava lo mismo para 2025 -bynd
    console.print("[yellow]🔍 Descargando lineup 2025 de Hot Wheels...[/yellow]")
    
    # aaa por ahora usamos data simulada porque el sitio no tiene la lista completa -bynd
    # ey cuando salga completa se puede scrapear igual que 2024 -bynd
    
    sample_2025 = [
        {"number": "1", "name": "Custom Ford Bronco", "series": "HW DREAM GARAGE", "year": 2025, "is_th": False, "is_sth": False},
        {"number": "2", "name": "Lamborghini Revuelto", "series": "HW EXOTICS", "year": 2025, "is_th": False, "is_sth": False},
        {"number": "3", "name": "MG Metro 6R4", "series": "RALLY", "year": 2025, "is_th": False, "is_sth": False},
        {"number": "4", "name": "'83 Chevy Silverado", "series": "HW HOT TRUCKS", "year": 2025, "is_th": False, "is_sth": False},
    ]
    
    console.print("[dim]💡 Usando data de ejemplo para 2025 (lineup completo aún no disponible)[/dim]")
    return sample_2025

def classify_car(car):
    # ey aquí clasificamos cada carro -bynd
    name_lower = car["name"].lower()
    
    classifications = {
        "is_jdm": False,
        "is_premium": False,
        "is_muscle": False,
        "brand": "Unknown",
        "category": []
    }
    
    # chintrolas detectamos JDM -bynd
    for brand in JDM_BRANDS:
        if brand in name_lower:
            classifications["is_jdm"] = True
            classifications["category"].append("JDM")
            break
    
    # aaa detectamos premium -bynd
    for brand in PREMIUM_BRANDS:
        if brand in name_lower:
            classifications["is_premium"] = True
            classifications["category"].append("Premium")
            break
    
    # fokeis detectamos muscle -bynd
    for brand in MUSCLE_BRANDS:
        if brand in name_lower:
            classifications["is_muscle"] = True
            classifications["category"].append("Muscle")
            break
    
    # vavavava detectamos marca -bynd
    if "porsche" in name_lower:
        classifications["brand"] = "Porsche"
    elif "ferrari" in name_lower:
        classifications["brand"] = "Ferrari"
    elif "lamborghini" in name_lower:
        classifications["brand"] = "Lamborghini"
    elif "nissan" in name_lower or "skyline" in name_lower or "gtr" in name_lower:
        classifications["brand"] = "Nissan"
    elif "toyota" in name_lower or "supra" in name_lower:
        classifications["brand"] = "Toyota"
    elif "honda" in name_lower:
        classifications["brand"] = "Honda"
    elif "mazda" in name_lower:
        classifications["brand"] = "Mazda"
    elif "chevrolet" in name_lower or "chevy" in name_lower or "camaro" in name_lower or "corvette" in name_lower:
        classifications["brand"] = "Chevrolet"
    elif "ford" in name_lower or "mustang" in name_lower:
        classifications["brand"] = "Ford"
    elif "dodge" in name_lower or "challenger" in name_lower or "charger" in name_lower:
        classifications["brand"] = "Dodge"
    elif "mclaren" in name_lower:
        classifications["brand"] = "McLaren"
    elif "bmw" in name_lower:
        classifications["brand"] = "BMW"
    elif "mercedes" in name_lower:
        classifications["brand"] = "Mercedes-Benz"
    elif "audi" in name_lower:
        classifications["brand"] = "Audi"
    
    # ey agregamos TH/STH a categorías -bynd
    if car.get("is_sth"):
        classifications["category"].append("STH")
    elif car.get("is_th"):
        classifications["category"].append("TH")
    
    return classifications

def build_hotlist():
    # q chidoteee construimos la hotlist completa -bynd
    console.clear()
    console.print("[bold cyan]🔥 GENERANDO HOTLIST[/bold cyan]\n")
    
    all_cars = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("[cyan]Descargando datos...", total=2)
        
        # aaa obtenemos ambos lineups -bynd
        cars_2024 = fetch_2024_lineup()
        progress.update(task, advance=1)
        
        cars_2025 = fetch_2025_lineup()
        progress.update(task, advance=1)
    
    all_cars = cars_2024 + cars_2025
    
    if not all_cars:
        console.print("[red]No se pudieron obtener datos[/red]")
        return []
    
    console.print(f"\n[green]✓ {len(all_cars)} carritos encontrados[/green]")
    console.print("[yellow]🏷️  Clasificando...[/yellow]\n")
    
    # chintrolas clasificamos cada uno -bynd
    hotlist = []
    for car in all_cars:
        classification = classify_car(car)
        
        hotlist_entry = {
            "id": f"{car['year']}-{car['number']}",
            "number": f"{car['number']}/{250 if car['year'] == 2024 else 250}",
            "name": car["name"],
            "series": car["series"],
            "year": car["year"],
            "brand": classification["brand"],
            "categories": classification["category"],
            "is_jdm": classification["is_jdm"],
            "is_premium": classification["is_premium"],
            "is_muscle": classification["is_muscle"],
            "is_th": car.get("is_th", False),
            "is_sth": car.get("is_sth", False)
        }
        
        hotlist.append(hotlist_entry)
    
    # vavavava guardamos -bynd
    save_hotlist(hotlist)
    
    console.print(f"[green]✓ Hotlist generada con {len(hotlist)} carritos[/green]")
    return hotlist

def save_hotlist(hotlist):
    # ey guardamos la hotlist -bynd
    data = {
        "generated_at": datetime.now().isoformat(),
        "total_cars": len(hotlist),
        "cars": hotlist
    }
    
    with open(HOTLIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_hotlist():
    # aaa cargamos la hotlist -bynd
    try:
        with open(HOTLIST_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("cars", [])
    except FileNotFoundError:
        return []

def search_hotlist(query, filters=None):
    # chintrolas búsqueda en la hotlist -bynd
    hotlist = load_hotlist()
    
    if not hotlist:
        console.print("[yellow]No hay hotlist. Genera una primero (opción 1)[/yellow]")
        return []
    
    query_lower = query.lower()
    results = []
    
    for car in hotlist:
        # ey filtrado básico por nombre -bynd
        if query_lower in car["name"].lower():
            # aaa aplicamos filtros adicionales -bynd
            if filters:
                if filters.get("jdm") and not car["is_jdm"]:
                    continue
                if filters.get("premium") and not car["is_premium"]:
                    continue
                if filters.get("th") and not (car["is_th"] or car["is_sth"]):
                    continue
                if filters.get("sth") and not car["is_sth"]:
                    continue
                if filters.get("brand") and car["brand"].lower() != filters["brand"].lower():
                    continue
            
            results.append(car)
    
    return results

def show_hotlist_stats():
    # vavavava estadísticas de la hotlist -bynd
    hotlist = load_hotlist()
    
    if not hotlist:
        console.print("[yellow]No hay hotlist. Genera una primero (opción 1)[/yellow]")
        return
    
    console.clear()
    console.print("[bold cyan]📊 ESTADÍSTICAS DE HOTLIST[/bold cyan]\n")
    
    total = len(hotlist)
    jdm_count = sum(1 for c in hotlist if c["is_jdm"])
    premium_count = sum(1 for c in hotlist if c["is_premium"])
    muscle_count = sum(1 for c in hotlist if c["is_muscle"])
    th_count = sum(1 for c in hotlist if c["is_th"])
    sth_count = sum(1 for c in hotlist if c["is_sth"])
    
    console.print(f"[bold]Total de carritos:[/bold] {total}")
    console.print(f"[cyan]🇯🇵 JDM:[/cyan] {jdm_count} ({jdm_count/total*100:.1f}%)")
    console.print(f"[yellow]⭐ Premium:[/yellow] {premium_count} ({premium_count/total*100:.1f}%)")
    console.print(f"[red]💪 Muscle:[/red] {muscle_count} ({muscle_count/total*100:.1f}%)")
    console.print(f"[green]🏆 TH:[/green] {th_count}")
    console.print(f"[magenta]💎 STH:[/magenta] {sth_count}")
    console.print()
    
    # chintrolas top marcas -bynd
    brands = {}
    for car in hotlist:
        brand = car["brand"]
        brands[brand] = brands.get(brand, 0) + 1
    
    sorted_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)[:10]
    
    table = Table(title="🏷️ TOP 10 MARCAS", border_style="blue")
    table.add_column("Marca", style="cyan")
    table.add_column("Cantidad", justify="center", style="green")
    
    for brand, count in sorted_brands:
        table.add_row(brand, str(count))
    
    console.print(table)
    console.print()
    input("Presiona Enter para continuar...")

def format_hotlist_entry(car):
    # ey formato bonito para mostrar -bynd
    tags = []
    
    if car["is_sth"]:
        tags.append("[magenta]STH[/magenta]")
    elif car["is_th"]:
        tags.append("[green]TH[/green]")
    
    if car["is_jdm"]:
        tags.append("[cyan]JDM[/cyan]")
    
    if car["is_premium"]:
        tags.append("[yellow]Premium[/yellow]")
    
    if car["is_muscle"]:
        tags.append("[red]Muscle[/red]")
    
    tags_str = " ".join(tags) if tags else ""
    
    return f"{car['number']} {car['series']} {car['name']} {tags_str}"

if __name__ == "__main__":
    # aaa ejemplo de uso -bynd
    console.print("[bold cyan]Hot Wheels Database Module[/bold cyan]\n")
    console.print("Este módulo se usa desde el programa principal")
    console.print("Pero puedes probarlo aquí:\n")
    
    hotlist = build_hotlist()
    
    if hotlist:
        console.print("\n[bold]Ejemplos de búsqueda:[/bold]\n")
        
        # fokeis algunos ejemplos -bynd
        porsche_results = search_hotlist("porsche")
        console.print(f"[cyan]Porsches encontrados:[/cyan] {len(porsche_results)}")
        
        jdm_results = [c for c in hotlist if c["is_jdm"]]
        console.print(f"[cyan]JDM encontrados:[/cyan] {len(jdm_results)}")
        
        th_results = [c for c in hotlist if c["is_th"] or c["is_sth"]]
        console.print(f"[cyan]Treasure Hunts encontrados:[/cyan] {len(th_results)}")