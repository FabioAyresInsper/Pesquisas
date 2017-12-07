import sys, re, os, time
from crawler_jurisprudencia_tj import crawler_jurisprudencia_tj
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from common.conexao_local import cursorConexao

class crawler_jurisprudencia_tjes():
	"""Crawler especializado em retornar textos da jurisprudência de segunda instância de São Paulo"""
	def __init__(self):
		crawler_jurisprudencia_tj.__init__(self)
		self.link_inicial = 'http://aplicativos.tjes.jus.br/sistemaspublicos/consulta_jurisprudencia/cons_jurisp.cfm'
		self.pesquisa_livre = 'edPesquisaJuris'
		self.data_julgamento_inicialID = 'edIni'
		self.data_julgamento_finalID = 'edFim'
		self.botao_pesquisar = 'Pesquisar'
		self.tabela_colunas = 'justica_estadual.jurisprudencia_es (ementas)'
		self.botao_proximoXP = '//*[@id="conteudo"]/table[2]/tbody/tr[1]/td[2]/a[1]'

	def download_tj(self,data_ini,data_fim):
		cursor = cursorConexao()
		driver = webdriver.Chrome(self.chromedriver)
		driver.get(self.link_inicial)
		driver.find_element_by_id(self.pesquisa_livre).send_keys('ementa')
		driver.find_element_by_id(self.data_julgamento_inicialID).send_keys(data_ini)
		driver.find_element_by_id(self.data_julgamento_finalID).send_keys(data_fim)
		driver.find_element_by_id(self.botao_pesquisar).click()
		loop_counter = 0
		while True:
			try:
				texto = crawler_jurisprudencia_tj.extrai_texto_html(self,(driver.page_source).replace('"',''))
				cursor.execute('INSERT INTO %s value ("%s");' % (self.tabela_colunas,texto))
				driver.find_element_by_xpath(self.botao_proximoXP).click()
				time.sleep(2)
			except:
				loop_counter += 1
				time.sleep(5)
				if loop_counter > 3:
					break
		driver.close()

if __name__ == '__main__':
	c = crawler_jurisprudencia_tjes()
	print('comecei ',c.__class__.__name__)
	for l in c.lista_anos:
		try:
			print(l[0], '  ',l[1])
			c.download_tj(l[0],l[1])
		except:
			print('finalizei com erro o ano ',l[0],'  ',l[1])