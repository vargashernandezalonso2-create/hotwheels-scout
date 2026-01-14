import pandas as pd
import json
import re
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import os

console = Console()

# aaa archivos -bynd
HOTLIST_FILE = "hotlist.json"
CSV_2024_FILE = "hotwheels_2024.csv"
CSV_2025_FILE = "hotwheels_2025.csv"
CSV_2026_FILE = "hotwheels_2026.csv"

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

def scrape_year_to_csv(year):
    # q chidoteee scrapeamos un año específico -bynd
    console.print(f"[yellow]🔍 Scrapeando Hot Wheels {year} desde Fandom...[/yellow]")
    
    # ey URLs según el año -bynd
    if year == 2024:
        url = "https://hotwheels.fandom.com/wiki/List_of_2024_Hot_Wheels"
        csv_file = CSV_2024_FILE
    elif year == 2025:
        url = "https://hotwheels.fandom.com/wiki/List_of_2025_Hot_Wheels"
        csv_file = CSV_2025_FILE
    elif year == 2026:
        url = "https://hotwheels.fandom.com/wiki/List_of_2026_Hot_Wheels_(by_Series)"
        csv_file = CSV_2026_FILE
    else:
        console.print(f"[red]Año {year} no soportado[/red]")
        return None
    
    try:
        # aaa leemos las tablas -bynd
        tables = pd.read_html(url)
        
        if not tables:
            console.print(f"[red]No se encontraron tablas en {url}[/red]")
            return None
        
        # chintrolas la tabla principal suele ser la 1 o 2 -bynd
        df = None
        for i, table in enumerate(tables):
            # fokeis buscamos la tabla que tenga columnas relevantes -bynd
            if any(col in str(table.columns).lower() for col in ['name', 'series', 'number']):
                df = table
                console.print(f"[dim]Usando tabla #{i}[/dim]")
                break
        
        if df is None and len(tables) > 1:
            df = tables[1]  # vavavava fallback a la segunda tabla -bynd
        elif df is None:
            df = tables[0]
        
        # ey guardamos a CSV -bynd
        df.to_csv(csv_file, index=False, encoding='utf-8')
        console.print(f"[green]✓ Guardado en {csv_file}[/green]")
        console.print(f"[dim]Total de filas: {len(df)}[/dim]")
        
        return csv_file
        
    except Exception as e:
        console.print(f"[red]Error al scrapear {year}: {e}[/red]")
        return None

def csv_to_json(csv_file, year):
    # aaa convertimos CSV a formato JSON estructurado -bynd
    console.print(f"[yellow]📋 Procesando {csv_file}...[/yellow]")
    
    if not os.path.exists(csv_file):
        console.print(f"[red]Archivo {csv_file} no existe[/red]")
        return []
    
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        
        # chintrolas limpiamos el dataframe -bynd
        # fokeis removemos filas completamente vacías -bynd
        df = df.dropna(how='all')
        
        console.print(f"[dim]Columnas encontradas: {list(df.columns)}[/dim]")
        
        cars = []
        
        for idx, row in df.iterrows():
            # ey intentamos extraer info de diferentes formatos -bynd
            car_data = {}
            
            # vavavava buscamos el nombre en columnas posibles -bynd
            name = None
            possible_name_cols = [
                'Model Name', 'model name', 'Model', 'model', 
                'Name', 'name', 'Casting', 'casting', 'Car', 'car'
            ]
            
            for col in possible_name_cols:
                if col in df.columns and pd.notna(row[col]):
                    name = str(row[col]).strip()
                    if name and name != 'nan' and name != '':
                        break
            
            if not name or name == 'nan' or name == '':
                continue  # aaa skip si no tiene nombre -bynd
            
            # chintrolas serie -bynd
            series = "Unknown"
            possible_series_cols = [
                'Series', 'series', 'Segment', 'segment', 
                'Line', 'line', 'Collection', 'collection'
            ]
            
            for col in possible_series_cols:
                if col in df.columns and pd.notna(row[col]):
                    series = str(row[col]).strip()
                    if series and series != 'nan' and series != '':
                        break
            
            # ey número -bynd
            number = str(idx + 1)
            possible_num_cols = [
                'Toy #', 'toy #', '#', 'Col.#', 'col.#',
                'Number', 'number', 'No', 'no', 'Num', 'num',
                'Series #', 'series #'
            ]
            
            for col in possible_num_cols:
                if col in df.columns and pd.notna(row[col]):
                    num_val = str(row[col]).strip()
                    if num_val and num_val != 'nan' and num_val != '':
                        number = num_val
                        break
            
            # fokeis detectamos TH y STH -bynd
            is_th = False
            is_sth = False
            row_str = str(row.values).lower()
            if 'super treasure hunt' in row_str or 'sth' in row_str or '$th' in row_str:
                is_sth = True
                is_th = False
            elif 'treasure hunt' in row_str or ' th ' in row_str:
                is_th = True
            
            car_data = {
                "number": number,
                "name": name,
                "series": series,
                "year": year,
                "is_th": is_th,
                "is_sth": is_sth
            }
            
            cars.append(car_data)
        
        console.print(f"[green]✓ {len(cars)} carritos procesados de {year}[/green]")
        return cars
        
    except Exception as e:
        console.print(f"[red]Error procesando CSV: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return []

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
    
    # aaa scrapeamos los años disponibles -bynd
    years_to_scrape = [2024, 2025, 2026]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("[cyan]Descargando datos...", total=len(years_to_scrape))
        
        for year in years_to_scrape:
            csv_file = scrape_year_to_csv(year)
            if csv_file:
                cars = csv_to_json(csv_file, year)
                all_cars.extend(cars)
            progress.update(task, advance=1)
    
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
            "number": f"{car['number']}/{250}",
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
    console.print()
    input("Presiona Enter para continuar...")
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
        input("\nPresiona Enter para continuar...")
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
    
    # aaa stats por año -bynd
    years = {}
    for car in hotlist:
        year = car["year"]
        years[year] = years.get(year, 0) + 1
    
    console.print(f"\n[bold]Por Año:[/bold]")
    for year in sorted(years.keys()):
        console.print(f"  {year}: {years[year]} carritos")
    
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
