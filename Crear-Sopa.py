import random
import string
import requests
from urllib3.exceptions import HTTPError, TimeoutError, MaxRetryError
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, red, green, blue, yellow, pink, orange, cyan, magenta, white
import json

# Función para obtener palabras de una API
def obtener_palabras(api_url):
    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        palabras = []
        descripciones = []
        if api_url == "https://restcountries.com/v3.1/lang/spanish":
            random_countries = random.sample(data, 3)
            for country in random_countries:
                palabras.append(country['name']['common'].replace(" ", "").upper()[:15])
                descripciones.append(country['name']['official'])
        elif api_url == "https://rickandmortyapi.com/api/character":
            random_rick = random.sample(data['results'], 3)
            for character in random_rick:
                palabras.append(character['name'].replace(" ", "").upper()[:15])
                descripciones.append(character['species'])
        elif api_url == "https://digimon-api.vercel.app/api/digimon":
            random_digimon = random.sample(data, 3)
            for digimon in random_digimon:
                palabras.append(digimon['name'].replace(" ", "").upper()[:15])
                descripciones.append(digimon['level'])
        else:
            raise ValueError("API no reconocida")
        
        return palabras, descripciones
    except (HTTPError, TimeoutError, MaxRetryError) as e:
        print(f"Error al conectar con la API: {e}")
        return [], []
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return [], []

# Función para colocar palabras en la sopa de letras
def colocar_palabras(sopa, palabras):
    direcciones = [(0, 1), (1, 0), (1, 1), (1, -1)]
    soluciones = {}
    for palabra in palabras:
        palabra_colocada = False
        while not palabra_colocada:
            fila = random.randint(0, len(sopa) - 1)
            columna = random.randint(0, len(sopa[0]) - 1)
            direccion = random.choice(direcciones)
            if puede_colocar_palabra(sopa, palabra, fila, columna, direccion):
                soluciones[palabra] = []
                for i, letra in enumerate(palabra):
                    nueva_fila = fila + i * direccion[0]
                    nueva_columna = columna + i * direccion[1]
                    sopa[nueva_fila][nueva_columna] = letra
                    soluciones[palabra].append((nueva_fila, nueva_columna))
                palabra_colocada = True
    return soluciones

# Función para verificar si una palabra puede ser colocada en una posición y dirección específicas
def puede_colocar_palabra(sopa, palabra, fila, columna, direccion):
    for i, letra in enumerate(palabra):
        nueva_fila = fila + i * direccion[0]
        nueva_columna = columna + i * direccion[1]
        if (nueva_fila < 0 or nueva_fila >= len(sopa) or
                nueva_columna < 0 or nueva_columna >= len(sopa[0]) or
                sopa[nueva_fila][nueva_columna] not in (letra, ' ')):
            return False
    return True

# Función para rellenar la sopa de letras con letras aleatorias
def rellenar_sopa(sopa):
    letras = string.ascii_uppercase
    for fila in range(len(sopa)):
        for columna in range(len(sopa[0])):
            if sopa[fila][columna] == ' ':
                sopa[fila][columna] = random.choice(letras)

# Función para generar el PDF
def generar_pdf(sopa, palabras, descripciones, soluciones):
    pdf = canvas.Canvas("sopa_letras_colores.pdf", pagesize=letter)
    pdf.setFont("Helvetica", 12)
    
    # Colores para las palabras
    colores = [red, green, blue, yellow, pink, orange, cyan, magenta]
    
    # Coordenadas iniciales y tamaño de cada cuadro
    x_inicial = 100
    y_inicial = 700
    tam_cuadro = 20
    
    # Dibujar la sopa de letras con cuadros coloreados
    for fila in range(len(sopa)):
        for columna in range(len(sopa[0])):
            letra = sopa[fila][columna]
            color = None
            for idx, palabra in enumerate(soluciones):
                if (fila, columna) in soluciones[palabra]:
                    color = colores[idx % len(colores)]
                    break
            if color:
                pdf.setFillColor(color)
            else:
                pdf.setFillColor(white)
            x = x_inicial + columna * tam_cuadro
            y = y_inicial - fila * tam_cuadro
            pdf.rect(x, y, tam_cuadro, tam_cuadro, fill=1)
            pdf.setFillColor('black')
            pdf.drawString(x + 5, y + 5, letra)
    
    # Imprimir las palabras y descripciones en el PDF
    pdf.showPage()
    pdf.setFillColor('black')
    pdf.drawString(250, 770, "Palabras a Buscar y Descripciones")
    for idx, palabra in enumerate(palabras):
        pdf.drawString(100, 750 - idx * 20, f"{palabra}: {descripciones[idx]}")
    
    pdf.save()

# Función para exportar a JSON
def exportar_a_json(sopa, palabras):
    datos = {
        'sopa': sopa,
        'palabras': palabras
    }
    with open('sopa_letras.json', 'w') as archivo:
        json.dump(datos, archivo)

# Programa principal
def main():
    apis = [
        "https://restcountries.com/v3.1/lang/spanish",
        "https://rickandmortyapi.com/api/character",
        "https://digimon-api.vercel.app/api/digimon"
    ]
    
    palabras = []
    descripciones = []
    
    # Obtener palabras y descripciones de las APIs
    for api in apis:
        palabras_api, descripciones_api = obtener_palabras(api)
        palabras.extend(palabras_api)
        descripciones.extend(descripciones_api)
    
    if len(palabras) < 9:
        print("No se obtuvieron suficientes palabras de las APIs.")
        return
    
    palabras = palabras[:9]
    descripciones = descripciones[:9]
    
    # Crear la sopa de letras vacía
    sopa = [[' ' for _ in range(15)] for _ in range(15)]
    
    # Colocar palabras en la sopa de letras
    soluciones = colocar_palabras(sopa, palabras)
    
    # Rellenar la sopa de letras con letras aleatorias
    rellenar_sopa(sopa)
    
    # Imprimir la sopa de letras y el vector de palabras
    for fila in sopa:
        print(' '.join(fila))
    print("Palabras a buscar:", palabras)
    
    # Generar el PDF
    generar_pdf(sopa, palabras, descripciones, soluciones)
    
    # Exportar a JSON
    exportar_a_json(sopa, palabras)

if __name__ == "__main__":
    main()