import random
import math
import numpy as np

def generar_espacio_perturbado(num_particulas=100, ancho_total=100, alto_total=100, profundo_total=100):
    
    volumen = ancho_total * alto_total * profundo_total
    s = (volumen / num_particulas) ** (1/3)
    
    cols = max(1, round(ancho_total / s))
    rows = max(1, round(alto_total / s))
    layers = max(1, round(profundo_total / s))
    
    espaciado_x = ancho_total / cols
    espaciado_y = alto_total / rows
    espaciado_z = profundo_total / layers
    
    posi = []
    contador = 0
    
    for i in range(cols):
        for j in range(rows):
            for k in range(layers):
                if contador >= num_particulas:
                    break
                
                base_x = i * espaciado_x + (espaciado_x / 2)
                base_y = j * espaciado_y + (espaciado_y / 2)
                base_z = k * espaciado_z + (espaciado_z / 2)

                pert_x = random.uniform(-0.3, 0.3) * espaciado_x
                pert_y = random.uniform(-0.3, 0.3) * espaciado_y
                pert_z = random.uniform(-0.3, 0.3) * espaciado_z

                posi.append((base_x + pert_x, base_y + pert_y, base_z + pert_z))
                contador += 1
                
            if contador >= num_particulas:
                break
        
        if contador >= num_particulas:
            break
        
    return posi

def esfera_circunscrita(tetra):
    A, B, C, D = np.array(tetra[0]), np.array(tetra[1]), np.array(tetra[2]), np.array(tetra[3])
    
    AB = B - A
    AC = C - A
    AD = D - A
    
    len_AB_sq = np.dot(AB, AB)
    len_AC_sq = np.dot(AC, AC)
    len_AD_sq = np.dot(AD, AD)
    

    cross_AC_AD = np.cross(AC, AD)
    cross_AD_AB = np.cross(AD, AB)
    cross_AB_AC = np.cross(AB, AC)

    denom = 2 * np.dot(AB, cross_AC_AD)
    
    if abs(denom) < 1e-10:
        return None, None  

    numerador = (len_AB_sq * cross_AC_AD + 
                 len_AC_sq * cross_AD_AB + 
                 len_AD_sq * cross_AB_AC)
    
    center = A + numerador / denom
    radius_squared = np.sum((A - center) ** 2)
    
    return center, radius_squared
    
    
def punto_circuncirculo(punto, tetra):
    center, radius_squared = esfera_circunscrita(tetra)
    
    if center is None:
        return False
        
    distancia_cuadrada = np.sum((np.array(punto) - center) ** 2)
    return distancia_cuadrada <= radius_squared

def punto_nuevo(punto, lista, bad_lista):
    for tetra in lista:
        if punto_circuncirculo(punto, tetra):
            bad_lista.append(tetra)
    
    for tetra in bad_lista:
        if tetra in lista:
            lista.remove(tetra)

def caras_borde(bad_lista):
    caras_conteo = []
    
    for tetra in bad_lista:
        A, B, C, D = tetra
        tetra_caras = [
            (A, B, C),
            (A, B, D),
            (A, C, D),
            (B, C, D)
        ]
        
        for cara in tetra_caras:
            cara_norm = tuple(sorted(cara, key=lambda pt: (pt[0], pt[1], pt[2])))
            
            encontrada = False
            for item in caras_conteo:
                if item[0] == cara_norm:
                    item[1] += 1
                    encontrada = True
                    break
            
            if not encontrada:
                caras_conteo.append([cara_norm, 1])
                
    borde = []
    for item in caras_conteo:
        cara, conteo = item
        if conteo == 1:
            borde.append(cara)
            
    return borde
            
def completar_triangulacion(punto_nuevo, caras_borde, lista_principal):
    for cara in caras_borde:
        pA, pB, pC = cara
        nuevo_tetraedro = (pA, pB, pC, punto_nuevo)
        lista_principal.append(nuevo_tetraedro)

def delaunay_3d():
    supa_tetra = [
        (-4000, -4000, -4000), 
        (4000, -4000, -4000), 
        (0, 4000, -4000), 
        (0, 0, 4000)
    ]
    
    points = generar_espacio_perturbado()
    lista_principal = [tuple(supa_tetra)]
    
    for p in points:
        bad_lista = []
        punto_nuevo(p, lista_principal, bad_lista)
        borde = caras_borde(bad_lista)
        completar_triangulacion(p, borde, lista_principal)
        
    tetraedros_limpios = []
    for tetra in lista_principal:
        comparte_super = any(vertice in supa_tetra for vertice in tetra)
        if not comparte_super:
            tetraedros_limpios.append(tetra)
            
    return tetraedros_limpios, points


