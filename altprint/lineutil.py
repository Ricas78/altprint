# A função split é usada para dividir geometrias (como LineStrings) em pontos especificados. Divide uma geometria por outra geometria e retorna uma coleção de geometrias
from shapely.ops import split
# Uma LineString é um tipo de geometria composto por um ou mais segmentos de linha (raster zig-zag). Ao contrário de LinearRing, LineString não é fechado. Um MultiLineString é uma coleção de um ou mais LineStrings (definidos por uma lista de pares de coordenadas (x, y) que definem os vértices da linha). Essas classes representam objetos geométricos no espaço 2D
from shapely.geometry import LineString, MultiLineString


def retract(path, ratio):  # Esta função recebe dois argumentos: path (um LineString) e ratio (um float)
    x, y = path.xy  # Extrai as coordenadas X e Y do caminho
    # Defina os pontos A e B como os pontos inicial e final do caminho
    A = (x[0], y[0])
    B = (x[-1], y[-1])
    # Calcule o ponto C que está no mesmo segmento de linha, mas a uma fração específica (dada pela razão) da distância de A a B
    C = (A[0] + ratio*(B[0]-A[0]), A[1] + ratio*(B[1]-A[1]))
    # Cria duas LineStrings: flex_path de A para C e retract_path de C para B
    flex_path = LineString([A, C])
    retract_path = LineString([C, B])
    return flex_path, retract_path  # Retorna ambas LineStrings


# quebra varios segmentos que estão dentro de um ou mais pontos em comum(spliter) em uma outra geometria
# Esta função recebe dois argumentos: lines (uma lista de LineStrings) e spliter (um LineString ou outra geometria)
def split_lines(lines, spliter):
    final = []  # cria uma lista
    for line in lines:  # Itera através de cada LineString em lines
        # Usa a função "split" para dividir LineString nos pontos de intersecção com "spliter"
        splited = split(line, spliter)
        for i in list(splited.geoms):
            if type(i) == LineString:  # Se a geometria for uma LineString
                # Adiciona as geometrias resultantes (LineStrings ou outros tipos) à lista final
                final.append(i)
            # Se uma geometria não for uma linestring, imprime “not linestring” (esta é uma etapa de depuração)
            else:
                print("not linestring")
    return final  # Retorna a lista de geometrias divididas

# quebra uma unica região, que contém todos segmentos dentro dela, em outras regiões (separar as regiões normal, flexivel e de recuperação)


# Esta função recebe dois argumentos: lines (uma MultiLineString) e regions (uma lista de LineStrings)
def split_by_regions(lines, regions):
    # cria uma lista de geometrias extraídas do MultiLineString (lines)
    final = list(lines.geoms)
    # Para cada região em "regions", chame a função "split_lines" na lista de geometrias "final" e divida as geometrias na região especificada
    for region in regions:
        # Atualização com as geometrias recém-divididas
        final = split_lines(final, region)
    # Retorna um objeto da classe MultiLineString composto pelas geometrias divididas acima
    return MultiLineString(final)
