import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

class CustomException(Exception):
    pass

def buscar_palabra_en_sopa(sopa, palabra):
    n = len(sopa)
    m = len(sopa[0])
    len_palabra = len(palabra)

    # Buscar horizontalmente
    for i in range(n):
        for j in range(m - len_palabra + 1):
            if sopa[i][j:j + len_palabra] == list(palabra):
                return [(i, j + k) for k in range(len_palabra)]

    # Buscar verticalmente
    for j in range(m):
        for i in range(n - len_palabra + 1):
            if all(sopa[i + k][j] == palabra[k] for k in range(len_palabra)):
                return [(i + k, j) for k in range(len_palabra)]

    # Buscar diagonalmente (principal)
    for i in range(n - len_palabra + 1):
        for j in range(m - len_palabra + 1):
            if all(sopa[i + k][j + k] == palabra[k] for k in range(len_palabra)):
                return [(i + k, j + k) for k in range(len_palabra)]

    # Buscar diagonalmente (invertida)
    for i in range(n - len_palabra + 1):
        for j in range(len_palabra - 1, m):
            if all(sopa[i + k][j - k] == palabra[k] for k in range(len_palabra)):
                return [(i + k, j - k) for k in range(len_palabra)]

    raise CustomException(f"Palabra '{palabra}' no encontrada en la sopa de letras.")

# Función para resolver la sopa de letras
def resolver_sopa_de_letras(data):
    sopa = data["sopa"]
    palabras = data["palabras"]
    resultados = {}

    for palabra in palabras:
        try:
            posiciones = buscar_palabra_en_sopa(sopa, palabra)
            resultados[palabra] = posiciones
        except CustomException as e:
            print(f"Error: {e}")

    return resultados

def generar_pdf_sopa_de_letras(sopa, resultados, output_filename):
    pdf = canvas.Canvas(output_filename, pagesize=letter)
    pdf.setTitle("Sopa de Letras Resuelta")
    pdf.setFont("Helvetica", 12)

    # Colores para las palabras
    colores = [colors.red, colors.green, colors.blue, colors.yellow,
               colors.pink, colors.orange, colors.cyan, colors.magenta]

    # Coordenadas iniciales y tamaño de cada cuadro
    x_inicial = 100
    y_inicial = 700
    tam_cuadro = 20

    # Dibujar la sopa de letras con cuadros coloreados
    for fila in range(len(sopa)):
        for columna in range(len(sopa[0])):
            letra = sopa[fila][columna]
            color = None
            for idx, (palabra, posiciones) in enumerate(resultados.items()):
                if (fila, columna) in posiciones:
                    color = colores[idx % len(colores)]
                    break
            if color:
                pdf.setFillColor(color)
            else:
                pdf.setFillColor(colors.white)
            x = x_inicial + columna * tam_cuadro
            y = y_inicial - fila * tam_cuadro
            pdf.rect(x, y, tam_cuadro, tam_cuadro, fill=1)
            pdf.setFillColor(colors.black)
            pdf.drawString(x + 5, y + 5, letra)

    # Imprimir las palabras encontradas en el PDF
    pdf.showPage()
    pdf.setFillColor(colors.black)
    pdf.drawString(250, 770, "Palabras Encontradas")
    for idx, palabra in enumerate(resultados.keys()):
        pdf.drawString(100, 750 - idx * 20, f"{palabra}")

    pdf.save()
    print(f"PDF generado: {output_filename}")

if __name__ == "__main__":
    try:
        # Cargar datos desde el archivo JSON
        with open('sopa_letras.json') as f:
            data = json.load(f)

        # Resolver la sopa de letras
        resultados = resolver_sopa_de_letras(data)

        # Generar el PDF con la sopa resuelta
        generar_pdf_sopa_de_letras(data['sopa'], resultados, 'sopa_resuelta.pdf')

    except FileNotFoundError:
        print("Error: Archivo JSON no encontrado.")
    except json.JSONDecodeError:
        print("Error: El archivo JSON no es válido.")
    except Exception as e:
        print(f"Error inesperado: {e}")
