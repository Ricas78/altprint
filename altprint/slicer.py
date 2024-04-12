from abc import ABC, abstractmethod
import trimesh
from shapely.geometry import MultiPolygon
from altprint.height_method import HeightMethod

# este arquivo tem como funcionalidade, ler um arquivo em stl, movimentar a peça e depois fatiar ela em planos associados a cada camada (STLslicer), isso é armazenado em um objeto que recebe essas informações e armazena a altura de cada camada, a geometria de cada camada e os limites superior e inferior da peça (SlicedPlanes)


class SlicedPlanes:
    """Represents the section plans obtained from the slicing of an object"""

    _height = float  # altura float da secção do plano
    # Um dicionário com alturas como chaves e geometrias MultiPolygon como valores
    _planes_dict = dict[_height, MultiPolygon]
    # Uma tupla de três floats que representam as coordenadas do plano 3D
    _coord = tuple[float, float, float]
    # Uma tupla de 2 coordenadas em que essas coordenadas são os limites superior e inferior
    _bounds_coords = tuple[_coord, _coord]

    # método construtor que inicializa os atributos "planes" e "bounds" com base nos parâmetros fornecidos
    def __init__(self, planes: _planes_dict, bounds: _bounds_coords):

        self.planes = planes
        self.bounds = bounds

    def get_heights(self):  # método que retorna as camadas de altura do dicionário
        return list(self.planes.keys())


class Slicer(ABC):  # Classe abstrata
    """Slicer base object"""

    @abstractmethod
    def load_model(self, model_file: str):  # método para carregar um modelo 3D de um arquivo
        pass

    @abstractmethod
    # método ara aplicar uma translação ao modelo carregado
    def translate_model(self, translation):
        pass

    @abstractmethod
    # método para fatiar o modelo e retornar planos
    def slice_model(self) -> SlicedPlanes:
        pass

# Em resumo, a classe STLSlicer carrega um modelo STL, translada e o fatia em planos. Os planos resultantes são armazenados junto com suas alturas e os limites do modelo em um objeto SlicedPlanes
# Implementação concreta da classe Slicer, especificamente para fatiar arquivos CAD .stl


class STLSlicer(Slicer):
    """Slice .stl cad files"""

    # Método construtor tendo com argumento uma instância de HeightMethod
    def __init__(self, height_method: HeightMethod):
        self.height_method = height_method

    # Carrega uma malha STL do arquivo especificado. Ele usa a função trimesh.load_mesh() da biblioteca trimesh para ler os dados da malha do arquivo
    def load_model(self, model_file: str):
        self.model = trimesh.load_mesh(model_file)

    # O argumento "translation" especifica quanto o modelo deve ser movido no espaço 3D
    def translate_model(self, translation):
        # O método apply_translation() do objeto de malha modifica as coordenadas de todos os vértices pelo vetor de translação especificado
        self.model.apply_translation(translation)

    # esse método fatia o modelo carregado em planos de seção (paralelos ao plano XY) em alturas especificadas
    def slice_model(self, heights=None) -> SlicedPlanes:
        if not heights:  # Se as alturas não forem fornecidas, ele calcula as alturas
            heights = self.height_method.get_heights(self.model.bounds)
        # Ele usa a função section_multiplane() da biblioteca trimesh para obter as secções
        sections = self.model.section_multiplane([0, 0, 0], [0, 0, 1], heights)
        planes = {}  # lista vazia para armazenar os planos
        for i, section in enumerate(sections):  # For each section
            if section:  # Se a secção não estiver vazia, converte os polígonos da secção em um MultiPolygon e associa-o à altura correspondente
                planes[heights[i]] = MultiPolygon(list(section.polygons_full))
            # Se a seção estiver vazia (sem geometria), associa uma lista vazia à altura correspondente
            else:
                planes[heights[i]] = []

        # retorna um objeto da classe SlicedPlanes contendo os planos e os limites do modelo
        return SlicedPlanes(planes, self.model.bounds)
