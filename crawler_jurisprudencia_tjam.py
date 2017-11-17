import sys, re
from crawlerJus import crawlerJus
from bs4 import BeautifulSoup

class crawler_jurisprudencia_tjam():
	"""Crawler especializado em retornar textos da jurisprudência de segunda instância do Amazonas"""
	def __init__(self):
		crawlerJus.__init__(self)
		self.link_inicial = 'http://consultasaj.tjam.jus.br/cjsg/consultaCompleta.do'
		self.pesquisa_livre = '//*[@id="iddados.buscaInteiroTeor"]'
		self.data_julgamento_inicialXP = '//*[@id="iddados.dtJulgamentoInicio"]'
		self.data_julgamento_finalXP = '//*[@id="iddados.dtJulgamentoFim"]'
		self.botao_pesquisar = '//*[@id="pbSubmit"]'
		self.botao_proximo_ini = '//*[@id="paginacaoSuperior-A"]/table/tbody/tr[1]/td[2]/div/a[5]'
		self.botao_proximo = '//*[@id="paginacaoSuperior-A"]/table/tbody/tr[1]/td[2]/div/a[6]'
		self.tabela_colunas = 'jurisprudencia_estadual.jurisprudencia_am (ementas)'


if __name__ == '__main__':
	# só vai baixar as ementas
	c = crawler_jurisprudencia_tjam()
	print('comecei ',c.__class__.__name__)
	for l in c.lista_anos:
		try:
			print(l[0],'  ',l[1])
			crawler_jurisprudencia_tj.download_tj_ESAJ(c,crawler_jurisprudencia_tj,l[0],l[1])
		except:
			print('finalizei o ano',l[0],'  ',l[1])