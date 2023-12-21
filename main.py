# Importações necessárias
import csv
from datetime import datetime
from collections import defaultdict
import os

class PMSFaturamento:
    def __init__(self):
        pass

    def processar_faturamento(self, entrada_csv, saida_csv):
        """
        Processa o faturamento abrindo o arquivo de entrada e gera um arquivo de saída.

        Args:
            entrada_csv (str): Caminho do arquivo de entrada CSV.
            saida_csv (str): Caminho do arquivo de saída CSV.

        Returns:
            None
        """
        # Verificar se o arquivo de entrada existe
        if not os.path.exists(entrada_csv):
            print(f"Arquivo de entrada '{entrada_csv}' não encontrado.")
            return

        # Abrir o arquivo de entrada
        with open(entrada_csv, 'r') as arquivo_entrada:
            # Criar um leitor CSV para percorrer o arquivo
            dados_entrada = csv.DictReader(arquivo_entrada, delimiter=';')

            # Lista para armazenar os dados processados
            dados_saida = []

            for linha in dados_entrada:
                try:

                    # Verificar se os campos necessários estão presentes

                    campos_entrada = {'ID_RESERVA', 'ID_PROPRIEDADE', 'ID_LOCADOR', 'ID_LOCATARIO', 'DATA_RESERVA',
                                      'DIAS_HOSPEDAGEM', 'VALOR_DIARIA', 'DESCONTO', 'ACRECIMOS', 'COMISSAO'}

                    for campo in campos_entrada:
                        if campo not in linha:
                            raise ValueError(f"Campo '{campo}' ausente no arquivo de entrada.")

                    # Calcular valor total e comissão
                    valor_total = (int(linha['DIAS_HOSPEDAGEM']) * float(linha['VALOR_DIARIA']) +
                                   float(linha['ACRECIMOS']) - float(linha['DESCONTO']))
                    comissao = valor_total * float(linha['COMISSAO'])

                    # Criar nova linha para o arquivo de saída
                    nova_linha = {
                        'ID_RESERVA': linha['ID_RESERVA'],
                        'ID_PROPRIEDADE': linha['ID_PROPRIEDADE'],
                        'ID_LOCADOR': linha['ID_LOCADOR'],
                        'ID_LOCATARIO': linha['ID_LOCATARIO'],
                        'DATA_RESERVA': linha['DATA_RESERVA'],
                        'DIAS_HOSPEDAGEM': linha['DIAS_HOSPEDAGEM'],
                        'VALOR_TOTAL': valor_total,
                        'VALOR_COMISSAO': comissao
                    }

                    # Adicionar a nova linha à lista de dados de saída
                    dados_saida.append(nova_linha)
                except ValueError as e:
                    print(f"Erro ao processar linha: {str(e)}")

        # Chamar função para escrever o arquivo de saída
        self.processar_saida(saida_csv, dados_saida)

    def somar_locador(self, entrada_csv, saida_csv):
        """
        Calcula a soma por mês e locador a partir de um arquivo de entrada
        e gera um arquivo de saída.

        Args:
            entrada_csv (str): Caminho do arquivo de entrada CSV.
            saida_csv (str): Caminho do arquivo de saída CSV.

        Returns:
            None
        """
        # Verificar se o arquivo de entrada existe
        if not os.path.exists(entrada_csv):
            print(f"Arquivo de entrada '{entrada_csv}' não encontrado.")
            return

        #soma por mês
        soma_mes = defaultdict(lambda: defaultdict(float))

        # Abrir o arquivo de entrada
        with open(entrada_csv, 'r') as arquivo_entrada:
            # Criar um leitor CSV para percorrer o arquivo
            dados_entrada = csv.DictReader(arquivo_entrada, delimiter=';')

            for linha in dados_entrada:
                try:
                    # Verificar se os campos necessários estão presentes
                    campos_necessarios = ['ID_RESERVA', 'ID_PROPRIEDADE', 'ID_LOCADOR', 'ID_LOCATARIO',
                                          'DATA_RESERVA', 'DIAS_HOSPEDAGEM', 'VALOR_TOTAL', 'VALOR_COMISSAO']
                    for campo in campos_necessarios:
                       if campo not in linha:
                           raise ValueError(f"Campo '{campo}' ausente no arquivo de entrada.")

                    # Obter o mês da data de reserva e o ID do locador
                    data_reserva = datetime.strptime(linha['DATA_RESERVA'], '%Y-%m-%d')
                    mes = data_reserva.strftime('%Y-%m')
                    id_locador = linha['ID_LOCADOR']

                    # REALIZA O SOMATORIO TOTAL E COMISSAO
                    soma_mes[id_locador][mes] += float(linha['VALOR_TOTAL'])

                except ValueError as e:
                    print(f"Erro ao processar linha: {str(e)}")

        # Lista para armazenar os dados de saída
        dados_saida = []


        for locador, soma_por_mes in soma_mes.items():
            for mes, valor_total in soma_por_mes.items():
                # Cria nova linha para o arquivo de saída
                nova_linha = {
                    'ID_LOCADOR': locador,
                    'MES': mes,
                    'VALOR_TOTAL': valor_total
                }

                # Adiciona nova linha de saída
                dados_saida.append(nova_linha)

        # Chama função para escrever o arquivo de saída
        self.processar_saida(saida_csv, dados_saida)

    def processar_saida(self, saida_csv, dados):
        """
        Escreve os dados em um arquivo de saída CSV.

        Args:
            saida_csv (str): Caminho do arquivo de saída CSV.
            dados (list): Lista de dicionários contendo os dados.

        Returns:
            None
        """

        with open(saida_csv, 'w', newline='') as arquivo_saida:
            # Obtem os campos do cabeçalho
            campos_saida = dados[0].keys() if dados else []

            # Escreve os dados no arquivo de saída
            escritor = csv.DictWriter(arquivo_saida, fieldnames=campos_saida, delimiter=';')

            # Cabeçalho no arquivo de saída
            escritor.writeheader()

            for linha in dados:
                # Escrever a linha no arquivo de saída
                escritor.writerow(linha)


if __name__ == "__main__":
    pms = PMSFaturamento()

    # Verifica se os diretórios existem
    for diretorio in ['file/bd', 'file/saida']:
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)

    # Processar faturamento analítico
    pms.processar_faturamento('file/bd/bd_entrada.csv', 'file/saida/bd_faturamento.csv')

    # Calcular as vendas e comissões por mês do locador
    pms.somar_locador('file/saida/bd_faturamento.csv', 'file/saida/bd_faturamento_locador.csv')
