import sys, re, time, pyautogui
from bs4 import BeautifulSoup
from crawler_jurisprudencia_tj import crawler_jurisprudencia_tj
from common.conexao_local import cursorConexao
from common_nlp.parse_texto import busca
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from common.conexao_local import cursorConexao

class crawler_jurisprudencia_tjro():
	"""Crawler especializado em retornar textos da jurisprudência de segunda instância de Rondônia"""
	def __init__(self):
		crawler_jurisprudencia_tj.__init__(self)
		self.link_inicial = 'http://webapp.tjro.jus.br/juris/consulta/consultaJuris.jsf'
		self.pesquisa_livreXP = '//*[@id="frmJuris:formConsultaJuris:iPesquisa"]'
		self.botao_pesquisarXP = '//*[@id="frmJuris:formConsultaJuris:btPesquisar"]'
		self.link_decisoesXP = '//*[@id="frmJuris:formDetalhesJuris:painelResultadosPesquisa_data"]/tr[1]/td/span/input'
		self.botao_proximoXP = '//*[@id="frmJuris:formDetalhesJuris:painelProcessosAcordaos_paginator_bottom"]/a[3]/span'
		self.ano_julgamentoXP = '//*[@id="frmJuris:formConsultaJuris:iAnoJulgamento"]'
		self.tabela_colunas = 'justica_estadual.jurisprudencia_ro (ementas)'

	def download_tj(self, ano):
		cursor = cursorConexao()
		driver = webdriver.Chrome(self.chromedriver)
		driver.get(self.link_inicial)
		driver.find_element_by_xpath(self.pesquisa_livreXP).send_keys('ementa')
		driver.find_element_by_xpath(self.ano_julgamentoXP).send_keys(ano)
		driver.find_element_by_xpath(self.botao_pesquisarXP).click()
		driver.find_element_by_xpath(self.link_decisoesXP).click()
		while True:
			try:
				time.sleep(1)
				links_inteiro_teor = driver.find_elements_by_class_name('botaoLink')
				for i in range(2,len(links_inteiro_teor)):
					try:
						links_inteiro_teor[i].click()
						driver.switch_to.window(driver.window_handles[-1])
						time.sleep(1)
						texto = crawler_jurisprudencia_tj.extrai_texto_html(self,driver.page_source).replace('"','')
						cursor.execute('INSERT INTO %s value ("%s");' % (self.tabela_colunas,texto))
						time.sleep(1)
						pyautogui.hotkey('ctrl','w')
						driver.switch_to.window(driver.window_handles[0])
					except:
						driver.switch_to.window(driver.window_handles[0])
				driver.find_element_by_xpath(self.botao_proximoXP).click()
				time.sleep(2)
			except Exception as e:
				print(e)
				break
		driver.close()

	def parser_acordaos(self,texto, cursor):
		numero = busca(r'\d{7}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}', texto, ngroup = 0)
		julgador = busca(r'\nRelator.*?\:\s*?(.*?)\n', texto)
		orgao_julgador = busca(r'\nOrigem\s*?\:\s*?(.*?)\n', texto)
		data_disponibilizacao = busca(r'\nData do julgamento\s*?\:(.*?)\n', texto)
		cursor.execute('INSERT INTO jurisprudencia_2_inst.jurisprudencia_2_inst (tribunal, numero, data_decisao, orgao_julgador, julgador, texto_decisao) values ("%s","%s","%s","%s","%s","%s");' % ('ro',numero, data_disponibilizacao, orgao_julgador, julgador, texto))

if __name__ == '__main__':
	c = crawler_jurisprudencia_tjro()

	cursor = cursorConexao()
	cursor.execute('SELECT ementas from justica_estadual.jurisprudencia_ro limit 1000000')
	dados = cursor.fetchall()
	for dado in dados:
		c.parser_acordaos(dado[0], cursor)

	# print('comecei ',c.__class__.__name__)
	# try:
	# 	for l in range(len(c.lista_anos)):
	# 		print(c.lista_anos[l])
	# 		try:
	# 			c.download_tj(c.lista_anos[l])
	# 		except Exception as e:
	# 			print(e)
	# except Exception as e:
	# 	print(e)