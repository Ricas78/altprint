from abc import ABC, abstractmethod
import numpy as np


# definição da classe base HeightMethod. A classe HeightMethod herda de ABC, o que a torna uma classe abstrata.
class HeightMethod(ABC):
    """Generates the height values on which the object will be sliced in"""

    @abstractmethod
    # método abstrato, como é decorado com @abstractmethod, qualquer classe concreta que herde de HeightMethod deve fornecer uma implementação para este método
    def get_heights(self, bounds) -> list[float]:
        pass


# definição da classe StandartHeightMethod, que herda de HeightMethod
class StandartHeightMethod(HeightMethod):
    """Evenly spaced layers"""

    # método construtor da classe, ele aceita um parâmetro layer_height com um valor padrão de 0.2
    def __init__(self, layer_height: float = 0.2):
        self.layer_height = layer_height

    # método que calcula as alturas das camadas com base nos limites fornecidos e na altura da camada definida no construtor, recebe um parâmetro bounds e retorna uma lista de números de ponto flutuante
    def get_heights(self, bounds) -> list[float]:
        # zi é definido como a coordenada Z do primeiro elemento de bounds (ou seja, o limite inferior no eixo z) mais a altura da camada
        zi = bounds[0][2] + self.layer_height
        # zf é definido como a coordenada Z do segundo elemento de bounds (ou seja, o limite superior no eixo z)
        zf = bounds[1][2]
        h = zf - zi  # h é definido como a diferença entre zf e zi, que é a altura total da peça
        # lista de alturas de camada. A função np.linspace é usada para gerar um número de valores igualmente espaçados entre zi e zf. O número de valores é determinado pela altura total h dividida pela altura da camada, arredondada para o número inteiro mais próximo, mais 1 (para incluir a camada que foi subtraída no cáclulo de h)
        heights = list(np.linspace(zi, zf, round(h/self.layer_height)+1))
        # pequeno valor é subtraído da última altura na lista heights. Isso é feito para garantir que a última camada seja incluída na fatia
        heights[-1] = heights[-1]-0.001
        # valores em heights são arredondados para três casas decimais usando a função np.around
        heights = list(np.around(heights, decimals=3))
        return heights  # retorna a lista com as alturas de cada camada


# definição da classe que também herda de HeightMethod
class CopyHeightsFromFileMethod(HeightMethod):
    """Get Heights from a premade gcode file"""

    # construtor da classe. Ele aceita um parâmetro gcode_file_name que é o nome do arquivo G-code a ser lido
    def __init__(self, gcode_file_name: str):
        self.gcode_file_name = gcode_file_name

    # definição do método, ele aceita um parâmetro opcional bounds e retorna uma lista de números de ponto flutuante
    def get_heights(self, bounds=None) -> list[float]:
        heights = []  # lista vazia, será usada para armazenar as alturas das camadas extraídas do arquivo gcode
        # O arquivo gcode com o nome armazenado no atributo gcode_file_name da instância é aberto para leitura ('r'). O arquivo aberto é referenciado pela variável f
        with open(self.gcode_file_name, "r") as f:
            lines = f.readlines()  # método readlines é chamado no objeto do arquivo para ler todas as linhas do arquivo. O resultado é uma lista de strings, onde cada string é uma linha do arquivo. Esta lista é atribuída à variável lines
        for line in lines:  # loop é iniciado que percorre todas as linhas no arquivo
            if line.startswith("; ALTPRINT"):  # Se a linha atual começar com "; ALTPRINT", A linha é dividida em palavras usando o espaço como delimitador. A última palavra (ou seja, o último elemento da lista resultante) é convertida em um número de ponto flutuante e adicionada à lista heights
                heights.append(float(line.split(' ')[-1]))
        return heights  # a lista é retornada contendo as alturas das camadas extraídas do arquivo gcode


if __name__ == "__main__":  # condição que é verdadeira se o módulo estiver sendo executado diretamente. Isso permite que você tenha partes do código que são executadas apenas quando o módulo é executado diretamente, e não quando é importado
    # instância da classe CopyHeightsFromFileMethod é criada com o nome do arquivo “teste.gcode”. Esta instância é atribuída à variável cp
    cp = CopyHeightsFromFileMethod("teste.gcode")
    print(cp.get_heights())  # método get_heights é chamado no objeto cp e o resultado é impresso. Este método lê o arquivo gcode especificado no construtor da classe e extrai as alturas das camadas do arquivo
