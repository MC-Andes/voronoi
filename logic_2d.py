import random
import math


def calcular_circuncentro (a1:tuple, a2:tuple, a3:tuple):

    x1, y1 = a1
    x2, y2 = a2
    x3, y3 = a3

    D = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    
    if D == 0:
        raise ValueError("Los puntos no forman un triángulo valido.")

    Ux = ((x1**2 + y1**2) * (y2 - y3) + 
          (x2**2 + y2**2) * (y3 - y1) + 
          (x3**2 + y3**2) * (y1 - y2)) / D

    Uy = ((x1**2 + y1**2) * (x3 - x2) + 
          (x2**2 + y2**2) * (x1 - x3) + 
          (x3**2 + y3**2) * (x2 - x1)) / D

    return ((Ux, Uy), ((Ux - x1)**2 + (Uy - y1)**2)**0.5)
    
def punto_circuncirculo (a1:tuple, circuncentro:tuple, radio:float):
    distancia_cuadrada = (a1[0] - circuncentro[0])**2 + (a1[1] - circuncentro[1])**2
    return distancia_cuadrada <= radio**2

def punto_nuevo (a:tuple, lista:list, bad_lista:list):
    for tri in lista:
        p1, p2, p3 = tri
        cir, rad = calcular_circuncentro(p1, p2, p3)
        if punto_circuncirculo(a, cir, rad):
            bad_lista.append(tri)
    for tri in bad_lista:
        lista.remove(tri)
        
def obtener_aristas_borde(bad_lista):
    aristas_conteo = []
    
    for tri in bad_lista:
        p1, p2, p3 = tri
        tri_aristas = [
            (p1, p2),
            (p2, p3),
            (p3, p1)
        ]
        
        for arista in tri_aristas:

            arista_norm = tuple(sorted(arista))
            
            encontrada = False
            for item in aristas_conteo:
                if item[0] == arista_norm:
                    item[1] += 1  
                    encontrada = True
                    break
            

            if not encontrada:
                aristas_conteo.append([arista_norm, 1])

    borde = []
    for item in aristas_conteo:
        arista, conteo = item
        if conteo == 1:
            borde.append(arista)
            
    return borde

def completar_triangulacion(punto_nuevo, aristas_borde, lista_principal):
    for arista in aristas_borde:
        pA, pB = arista
        nuevo_triangulo = (pA, pB, punto_nuevo)
        lista_principal.append(nuevo_triangulo)
        
def generar_espacio_perturbado(num_particulas=100, ancho_total=100, alto_total=100):
    
    aspect_ratio = ancho_total / alto_total
    cols = round(math.sqrt(num_particulas * aspect_ratio))
    rows = math.ceil(num_particulas / cols)
    
    espaciado_x = ancho_total / cols
    espaciado_y = alto_total / rows
    
    posi = []
    contador = 0
    
    for i in range(cols):
        for j in range(rows):
            if contador >= num_particulas:
                break
            
            # Posición base en la subgrilla
            base_x = i * espaciado_x + (espaciado_x / 2)
            base_y = j * espaciado_y + (espaciado_y / 2)
            
            # Perturbación proporcional al espaciado local
            pert_x = random.uniform(-0.3, 0.3) * espaciado_x
            pert_y = random.uniform(-0.3, 0.3) * espaciado_y
            
            posi.append((base_x + pert_x, base_y + pert_y))
            contador += 1
            
        if contador >= num_particulas:
            break
        
    return posi


def delaunay_triangulation():
    supa_triangulo = [(-4000, -4000), (4000, -4000), (0, 4000)]
    
    points = generar_espacio_perturbado()
    

    lista_principal =  [tuple(supa_triangulo)]
    
    for p in points:
        bad_lista = []
        
        punto_nuevo(p, lista_principal, bad_lista)
        
        borde = obtener_aristas_borde(bad_lista)
        
        completar_triangulacion(p, borde, lista_principal)
        
    # --- FILTRADO DE TRIANGULOS DEL SUPER-TRIÁNGULO ---
    triangulos_limpios = []
    for tri in lista_principal:
        # Verificamos si NINGUNO de los vértices del triángulo pertenece al super-triángulo
        comparte_super = any(vertice in supa_triangulo for vertice in tri)
        if not comparte_super:
            triangulos_limpios.append(tri)
        
    return triangulos_limpios, points

def recortar_contra_borde(poligono, xmin, xmax, ymin, ymax):
    # 1. Recortar contra la pared IZQUIERDA (x >= xmin)
    output = []
    if len(poligono) > 0:
        s = poligono[-1]
        for p in poligono:
            if p[0] >= xmin:  # p está adentro
                if s[0] < xmin:  # s estaba afuera, calculamos intersección
                    # intersección con x = xmin
                    y_int = s[1] + (p[1] - s[1]) * (xmin - s[0]) / (p[0] - s[0]) if p[0] != s[0] else s[1]
                    output.append((xmin, y_int))
                output.append(p)
            elif s[0] >= xmin:  # s estaba adentro, p está afuera
                y_int = s[1] + (p[1] - s[1]) * (xmin - s[0]) / (p[0] - s[0]) if p[0] != s[0] else s[1]
                output.append((xmin, y_int))
            s = p
        poligono = output

    # 2. Recortar contra la pared DERECHA (x <= xmax)
    output = []
    if len(poligono) > 0:
        s = poligono[-1]
        for p in poligono:
            if p[0] <= xmax:
                if s[0] > xmax:
                    y_int = s[1] + (p[1] - s[1]) * (xmax - s[0]) / (p[0] - s[0]) if p[0] != s[0] else s[1]
                    output.append((xmax, y_int))
                output.append(p)
            elif s[0] <= xmax:
                y_int = s[1] + (p[1] - s[1]) * (xmax - s[0]) / (p[0] - s[0]) if p[0] != s[0] else s[1]
                output.append((xmax, y_int))
            s = p
        poligono = output

    # 3. Recortar contra la pared INFERIOR (y >= ymin)
    output = []
    if len(poligono) > 0:
        s = poligono[-1]
        for p in poligono:
            if p[1] >= ymin:
                if s[1] < ymin:
                    x_int = s[0] + (p[0] - s[0]) * (ymin - s[1]) / (p[1] - s[1]) if p[1] != s[1] else s[0]
                    output.append((x_int, ymin))
                output.append(p)
            elif s[1] >= ymin:
                x_int = s[0] + (p[0] - s[0]) * (ymin - s[1]) / (p[1] - s[1]) if p[1] != s[1] else s[0]
                output.append((x_int, ymin))
            s = p
        poligono = output

    # 4. Recortar contra la pared SUPERIOR (y <= ymax)
    output = []
    if len(poligono) > 0:
        s = poligono[-1]
        for p in poligono:
            if p[1] <= ymax:
                if s[1] > ymax:
                    x_int = s[0] + (p[0] - s[0]) * (ymax - s[1]) / (p[1] - s[1]) if p[1] != s[1] else s[0]
                    output.append((x_int, ymax))
                output.append(p)
            elif s[1] <= ymax:
                x_int = s[0] + (p[0] - s[0]) * (ymax - s[1]) / (p[1] - s[1]) if p[1] != s[1] else s[0]
                output.append((x_int, ymax))
            s = p
        poligono = output

    return poligono

def contraer(poligono, semilla):
    px, py = semilla
    factor = random.uniform(0.75, 0.9)
    poligono_reducido = []
    for x, y in poligono:
        nuevo_x = px + factor * (x - px)
        nuevo_y = py + factor * (y - py)
        poligono_reducido.append((nuevo_x, nuevo_y))
    return poligono_reducido
    

def voronoi(caras:tuple):
    
    cota_inf, cota_sup = caras 
    
    triangulos, points = delaunay_triangulation()
    poliedros = []
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    
    margen = 5.0 
    xmin, xmax = min(xs) - margen, max(xs) + margen
    ymin, ymax = min(ys) - margen, max(ys) + margen
    
    for p in points:
        lista_lados = []
        for tri in triangulos:
            if p in tri:
                circuncentro, _ = calcular_circuncentro(tri[0], tri[1], tri[2])
                x, y = circuncentro
                x1, y1 = p
                ang = math.atan2(y - y1, x - x1)
                res = (circuncentro, ang)
                lista_lados.append(res)
        
        lista_lados.sort(key=lambda x: x[1])
        brutos = [lado[0] for lado in lista_lados]
        poliedro = recortar_contra_borde(brutos, xmin, xmax, ymin, ymax)
        if len(poliedro) >= cota_inf and len(poliedro) <= cota_sup:
            poliedro_separado = contraer(poliedro, p)
            poliedros.append(poliedro_separado)
            
    return poliedros, points
