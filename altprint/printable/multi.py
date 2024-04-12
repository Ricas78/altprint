from altprint.printable.base import BasePrint
from altprint.layer import Layer
from altprint.gcode import GcodeExporter


class MultiProcess():  # definição da classe responsável por controlar alguns dos parâmetros de impressão, visto que pressupõe que "parts" já contém o fatiamento e a geração das trajetórias das camadas já feitos

    # método construtor da classe, aceita um número arbitrário de argumentos de palavra-chave
    def __init__(self, **kwargs):
        # dicionário criado que contém os valores padrão para alguns parâmetros que serão usadas no processo de impressão
        prop_defaults = {
            "parts": [],
            "gcode_exporter": GcodeExporter,
            "start_script": "",
            "end_script": "",
            "offset": (0, 0, 0),
            "verbose": True,
        }

        # loop que percorre todos os itens do dicionário "prop_defaults". Para cada item, ele usa a função "setattr" para definir um atributo na instância atual com o nome "prop" e o valor correspondente de kwargs se ele existir, caso contrário, ele usa o valor padrão default.
        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))


class MultiPrint(BasePrint):  # definição da classe responsável por converter as camadas individuais de cada peça em camadas comuns às peças e realizar a exportação do gcode de um arquivo com várias peças CAD em stl para ser enviado a impreesora 3D

    _height = float  # variável float que armazena altura da camada
    # dicionário que contém a altura de cada camada
    _layers_dict = dict[_height, Layer]

    def __init__(self, process):  # método construtor da classe, recebe um parâmetro "process" que é uma instância da classe "MultiProcess" (deveria ser). O construtor inicializa três atributos de instância
        # atributo que recebe as configurações dos parâmetros de impressão fornecidado pela classe "MultiProcess"
        self.process = process
        # dicionário vazio que armazena as alturas referente a cada camada
        self.layers: _layers_dict = {}

    def slice(self):  # esse método não realiza nada aqui
        pass

    # método que junta todas as camadas das peças, já com suas trajetórias geradas no arquivo "flex.py", em uma única lista
    def make_layers(self):
        if self.process.verbose is True:  # linha de verificação fornecida dentro das configurações do próprio arquivo yml
            # mensagem quando executa essa função do programa
            print("Making the layers for the multipart ...")
        heights = []
        for part in self.process.parts:  # todas as alturas das camadas de todas as partes serão coletadas em uma única lista
            # Para cada parte, as chaves do dicionário layers dessa parte são estendidas à lista heights
            heights.extend(list(part.layers.keys()))

        # A lista "heights" é convertida em um conjunto (usando set()) para remover quaisquer duplicatas.
        heights = list(set(heights))
        heights.sort()  # lista é ordenada em ordem crescente

        for h in heights:  # Para cada altura h na lista heights, um novo objeto Layer é criado e atribuído à variável layer
            layer = Layer(None, None, None, None, None)
            for part in self.process.parts:  # para cada "part" que é uma peça contida no arquivo de configuração representado pelo objeto process
                if h in part.layers.keys():  # verifica-se se a altura h está nas chaves do dicionário layers dessa "part"

                    # Se estiver, os caminhos de preenchimento e perímetro dessa altura são estendidos aos caminhos de preenchimento e perímetro do objeto layer
                    # Isso significa que está adicionando todas as trajetórias de cada camada das peças, que antes eram individuais por peça, como camadas gerais para todas as peças
                    layer.infill.extend(part.layers[h].infill)
                    layer.perimeter.extend(part.layers[h].perimeter)
            # a camada atual é adicionada ao dicionário "layers" com a chave "h" referente a altura desta camada
            self.layers[h] = layer

    def export_gcode(self, filename):
        if self.process.verbose is True:  # linha de verificação fornecida dentro das configurações do próprio arquivo yml
            # mensagem quando executa essa função do programa
            print("exporting gcode to {}".format(filename))

        # cria uma instância "gcode_exporter" da classe "GcodeExporter" que recebe os parãmetros referentes ao script cabeçalho inicial e final do modelo da impressora utilizada fornecido pelo arquivo yml
        gcode_exporter = self.process.gcode_exporter(start_script=self.process.start_script,  # noqa: E501
                                                     end_script=self.process.end_script)
        # utiliza o método "make_gcode" da classe "GcodeExporter" para gerar o gcode de todas as camadas da peça 3D
        gcode_exporter.make_gcode(self)
        # utiliza o método "export_gcode" da classe "GcodeExporter" para salvar todas as linhas do gcode gerado, fornecidas por uma lista, em um arquivo com o nome fornecido pelo usuário
        gcode_exporter.export_gcode(filename)
