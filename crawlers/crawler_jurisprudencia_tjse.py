import sys, re, time
from bs4 import BeautifulSoup
from common.conexao_local import cursorConexao
from common_nlp.parse_texto import busca
from crawler_jurisprudencia_tj import crawler_jurisprudencia_tj
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from common.conexao_local import cursorConexao

class crawler_jurisprudencia_tjse():
	"""Crawler especializado em retornar textos da jurisprudência de segunda instância de Santa Catarina"""
	def __init__(self):
		crawler_jurisprudencia_tj.__init__(self)
		self.link_inicial = 'http://www.tjse.jus.br/Dgorg/paginas/jurisprudencia/consultarJurisprudencia.tjse'
		self.pesquisa_livre = '//*[@id="itTermos"]'
		self.botao_pesquisar = '//*[@id="btPesquisarVoto"]'
		self.tabela_colunas = 'justica_estadual.jurisprudencia_se (ementas)'
		self.botao_proximoXP = '//*[@id="dgResultadoJurisprudencia2_paginator_top"]/a[3]'

	def download_tj(self):
		cursor = cursorConexao()
		driver = webdriver.Chrome(self.chromedriver)
		driver.get(self.link_inicial)
		time.sleep(1)
		driver.find_element_by_xpath(self.pesquisa_livre).send_keys('processo')
		if input('Resolva o captcha do Google e digite um número diferente de zero:\n'):
			pass
		contador_loop = 0
		while True:
			try:
				time.sleep(1)
				texto = crawler_jurisprudencia_tj.extrai_texto_html(self,driver.page_source).replace('"','')
				cursor.execute('INSERT INTO %s value ("%s");' % (self.tabela_colunas,texto))
				driver.find_element_by_xpath(self.botao_proximoXP).click()
			except Exception as e:
				print(e)
				time.sleep(2)
				if contador_loop > 2:
					break
				contador_loop += 1
		driver.close()
		time.sleep(1)

	def parser_acordaos(self,texto,cursor):
		decisoes = re.split(r'\nCopiar\s*?\-',texto)
		for d in range(1,len(decisoes)):
			numero = busca(r'\d{7}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}', decisoes[d],ngroup=0)
			ementa = busca(r'^(.+)\nSessão\:', decisoes[d], args=re.DOTALL)
			classe = busca(r'\nClasse\:\n\s*?(.+)', decisoes[d])
			assunto = busca(r'\nAssuntos\:\n\s*?(.+)', decisoes[d])
			julgador = busca(r'\n\s*?Relator.*?\:\n\s*?(.*?)\(', decisoes[d])
			orgao_julgador = busca(r'\n\s*?.rgão julgador\:\n\s*?\n\s*?(.+)', decisoes[d])
			data_disponibilizacao = busca(r'\n\s*?Data de julgamento\:\n\s*?(\d{2}/\d{2}/\d{4})', decisoes[d])
			polo_ativo = busca(r'\n\s*?P.lo ativo\:\n\s*?(.+)', decisoes[d])
			polo_passivo = busca(r'\n\s*?P.lo passivo\:\n\s*?(.+)', decisoes[d])
			cursor.execute('INSERT INTO jurisprudencia_2_inst.jurisprudencia_2_inst (tribunal, numero, assunto, classe, data_decisao, orgao_julgador, julgador, polo_ativo, polo_passivo, texto_decisao) values ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s");' % ('se',numero, assunto, classe, data_disponibilizacao, orgao_julgador, julgador, polo_ativo, polo_passivo, ementa))

def main():
	pass

if __name__ == '__main__':
	c = crawler_jurisprudencia_tjse()
	# print('comecei ',c.__class__.__name__)
	# try:
	# 	c.download_tj()
	# except Exception as e:
	# 	print(e)

	cursor = cursorConexao()
	cursor.execute('SELECT ementas from justica_estadual.jurisprudencia_se limit 1000000')
	dados = cursor.fetchall()
	for dado in dados:
		c.parser_acordaos(dado[0], cursor)