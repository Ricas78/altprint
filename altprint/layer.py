from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString
import numpy as np
from altprint.flow import calculate

# Define como será feito o percurso do raster (trajetória extrudindo) e como será lógica da construção de camadas que é dividida em perimetro e prenchimento


class Raster:  # Esta classe representa um caminho raster na impressão

    # método que inicializa o raster com os seguintes parâmetros: path: Um LineString representando o caminho do bico da impressora, flow: O fator multiplicador de fluxo (calculado usando a função de cálculo), speed: A velocidade de impressão (valor escalar)
    def __init__(self, path: LineString, flow, speed):

        self.path = path  # "path" é armazenado como uma variável de instância

        # "speed" é usada para criar uma matriz de velocidades (uma para cada ponto coordenado no caminho)
        self.speed = np.ones(len(path.coords)) * speed
        # A matriz de extrusão é inicializada com zeros (para acumular valores de extrusão)
        self.extrusion = np.zeros(len(path.coords))
        x, y = path.xy  # Extrai as coordenadas X e Y de "path"
        # itera o laço a quantidade de vezes equivalente a quantiade de coordenadas armazenadas na array "path"
        for i in range(1, len(path.coords)):
            # distância entre a coordenada x atual e a anterior
            dx = abs(x[i] - x[i - 1])
            # distância entre a coordenada y atual e a anterior
            dy = abs(y[i] - y[i - 1])
            # array que armazena o valor da quantidade de filamento utilizada para cada "conjunto" de coordenadas XY que compõe a traetória do raster até o ponto atual
            self.extrusion[i] = np.sqrt(
                (dx**2) + (dy**2)) * flow * calculate() + self.extrusion[i-1]


# Classe que representa as trajetórias (contornos e preenchimento) dentro da camada da peça.
class Layer:
    """Layer Object that stores layer internal and external shapes, also perimeters and infill path"""  # noqa: E501

    # método construtor da camada
    def __init__(self, shape: MultiPolygon, perimeter_num, perimeter_gap, external_adjust, overlap):
        # A classe "MultiPolygon" representa a forma da camada (geometria) tanto interna quanto externa
        self.shape = shape
        self.perimeter_num = perimeter_num  # Número de perímetros da camada
        # Espaçamento entre perímetros(contornos)
        self.perimeter_gap = perimeter_gap
        # Fator de ajuste para a forma externa
        self.external_adjust = external_adjust
        # Quanto de sobreposião há entre os perímetros adjascentes
        self.overlap = overlap
        # Lista (inicializa vazia) para armazenar os caminhos dos perímetros individualmente
        self.perimeter_paths: List = []
        # Lista (inicializa vazia) para armazenar os perímetros completos individualmente
        self.perimeter: List = []
        # Lista (inicializa vazia) para armazenar o prenchimento completo individualmente
        self.infill: List = []
        # representa a borda da área de preenchimento
        self.infill_border: MultiPolygon = MultiPolygon()

    def make_perimeter(self):  # Este método constrói os caminhos de perímetro para uma camada erodindo a forma da camada e extraindo os segmentos de limite (externo) e furo (interno). Esses segmentos são armazenados no atributo perimeter_paths
        """Generates the perimeter based on the layer process"""

        # Lista vazia "perimeter_paths" para armazenar os segmentos de forma individual de cada perímetro
        perimeter_paths = []
        # O loop itera para cada secção (geometria) com a forma da camada (geoemetria) que é um MultiPolygon
        for section in self.shape.geoms:
            for i in range(self.perimeter_num):  # O loop itera o número de perímetros
                eroded_shape = section.buffer(- self.perimeter_gap*(i)
                                              - self.external_adjust/2, join_style=2)  # Calcula uma “forma erodida” protegendo a seção com uma distância negativa
                # A distância negativa é determinada subtraindo o produto de self.perimeter_gap * i e self.external_adjust / 2. O argumento join_style=2 especifica como o buffer deve lidar com interseções

                # Se a forma erodida estiver vazia (não tiver geometria), o loop será interrompido
                if eroded_shape.is_empty:
                    break
                # Se a forma erodida for um único polígono, será criada uma lista contendo esse polígono
                if type(eroded_shape) == Polygon:
                    polygons = [eroded_shape]
                # Se a forma erodida for um MultiPolygon, ele extrai os polígonos individuais dela
                elif type(eroded_shape) == MultiPolygon:
                    polygons = list(eroded_shape.geoms)

                # Para cada polígono (externo e interior)
                for poly in polygons:
                    for hole in poly.interiors:
                        # Adiciona os anéis internos (furos) como segmentos LineString individuais a perimet_paths
                        perimeter_paths.append(LineString(hole))
                for poly in polygons:
                    # Adiciona o anel externo (limite) como um segmento LineString a perimeter_paths
                    perimeter_paths.append(LineString(poly.exterior))
        # Atribui toda a lista perimeter_paths (composta por todos os segmentos) ao atributo self.perimeter_paths (que é um MultiLinestring)
        self.perimeter_paths = MultiLineString(perimeter_paths)

    def make_infill_border(self):  # O método constrói a borda de preenchimento para uma camada erodindo a forma da camada e extraindo os polígonos individuais que formam a borda. Esses polígonos são armazenados no atributo infill_border
        """Generates the infill border based on the layer process"""

        # lista vazia chamada infill_border_geoms para armazenar as geometrias individuais (polígonos) da borda de preenchimento
        infill_border_geoms = []
        # o loop percorre cada seção (geometria) dentro da forma da camada (que é um MultiPoligon)
        for section in self.shape.geoms:
            eroded_shape = section.buffer(- self.perimeter_gap
                                          * self.perimeter_num
                                          - self.external_adjust/2
                                          + self.overlap, join_style=2)  # Calcula uma “forma erodida” protegendo a seção com uma distância negativa
            if not eroded_shape.is_empty:  # Se a forma erodida não estiver vazia
                # Se a forma erodida for um único polígono, ela será anexada à lista infill_border_geoms
                if type(eroded_shape) == Polygon:
                    infill_border_geoms.append(eroded_shape)
                else:
                    # If the eroded shape is a MultiPolygon, it extends the list with the individual polygons extracted from it
                    infill_border_geoms.extend(eroded_shape.geoms)

        # Se a forma erodida for um MultiPolygon, ela estende a lista com os polígonos individuais extraídos dela
        self.infill_border = MultiPolygon(infill_border_geoms)
