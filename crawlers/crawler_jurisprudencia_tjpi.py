import sys, re, time
from bs4 import BeautifulSoup
from common.conexao_local import cursorConexao
from common_nlp.parse_texto import busca
from crawler_jurisprudencia_tj import crawler_jurisprudencia_tj
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from common.conexao_local import cursorConexao

class crawler_jurisprudencia_tjpi():
	"""Crawler especializado em retornar textos da jurisprudência de segunda instância do Piauí"""
	def __init__(self):
		crawler_jurisprudencia_tj.__init__(self)
		self.link_inicial = 'http://www.tjpi.jus.br/e-tjpi/home/jurisprudencia'
		self.pesquisa_livre = '//*[@id="palavras_chave"]'
		self.botao_pesquisar = '//*[@id="wrapper"]/div/div[2]/div/div[1]/div/form/fieldset/div/div/button'
		self.botao_proximoXP = '//*[@id="wrapper"]/div/div[2]/div/nav/ul/li[4]/a/span/i'
		self.tabela_colunas = 'justica_estadual.jurisprudencia_pi (ementas)'

	def download_tj(self):
		cursor = cursorConexao()
		driver = webdriver.Chrome(self.chromedriver)
		driver.get(self.link_inicial)
		driver.find_element_by_xpath(self.pesquisa_livre).send_keys('ementa')
		driver.find_element_by_xpath(self.botao_pesquisar).click()
		loop_counter = 0
		while True:
			try:
				texto = crawler_jurisprudencia_tj.extrai_texto_html(self,(driver.page_source).replace('"',''))
				cursor.execute('INSERT INTO %s value ("%s");' % (self.tabela_colunas,texto))
				driver.find_element_by_xpath(self.botao_proximoXP).click()
				time.sleep(2)
			except:
				if input('ajude-me'):
					break
		driver.close()

	def parser_acordaos(self,texto,cursor):
		decisoes = re.split(r'\n\s*?Temporariamente indisponível.',texto)
		for d in range(len(decisoes)):
			numero = busca(r'\d{7}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}', decisoes[d],ngroup=0)
			ementa = busca(r'\nEMENTA\:(.+)', decisoes[d], args = re.DOTALL | re.IGNORECASE)
			classe = busca(r'\nClasse\:(.+)', decisoes[d])
			data_disponibilizacao = busca(r'\nJulgamento\:\s*?(\d{2}/\d{2}/\d{4})', decisoes[d])
			orgao_julgador = busca(r'\n.rgão\:(.+)', decisoes[d])
			julgador = busca(r'\nRelator.*?\:(.+)', decisoes[d])
			cursor.execute('INSERT INTO jurisprudencia_2_inst.jurisprudencia_2_inst (tribunal, numero, classe, data_decisao, orgao_julgador, julgador, texto_decisao) values ("%s","%s","%s","%s","%s","%s","%s");' % ('pi',numero, classe, data_disponibilizacao, orgao_julgador, julgador, ementa))


if __name__ == '__main__':
	c = crawler_jurisprudencia_tjpi()
	# print('comecei ',c.__class__.__name__)
	# try:
	# 	c.download_tj()
	# except:
	# 	print('finalizei com erro\n')

	cursor = cursorConexao()
	cursor.execute('SELECT ementas from justica_estadual.jurisprudencia_pi limit 1000000')
	dados = cursor.fetchall()
	for dado in dados:
		c.parser_acordaos(dado[0], cursor)