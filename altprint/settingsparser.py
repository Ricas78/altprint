import yaml  # importa o módulo yaml, que permite trabalhar com arquivos YAML. YAML é um formato de serialização de dados legível, frequentemente usado para arquivos de configuração


class SettingsParser:  # classe que pega o arquivo de configs yml e converte ele para um dicionário para o python utilizar as configrações definidas de fato no código

    # método que leva o argumento "configfname", que representa o nome do arquivo de configuração yml para carregar
    def load_from_file(self, configfname):

        # abre o arquivo especificado (configfname) no modo de leitura ('r'). O objeto de arquivo é atribuído à variável "f"
        with open(configfname, 'r') as f:
            # yaml.safe_load() analisa os dados YAML e retorna um dicionário Python contendo as configurações carregadas. O dicionário resultante é atribuído à variável "params"
            params = yaml.safe_load(f)
        return params  # retorna o dicionário "params", que contém as configurações carregadas
