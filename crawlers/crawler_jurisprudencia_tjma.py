import time, re
from bs4 import BeautifulSoup
from common.conexao_local import cursorConexao
from common_nlp.parse_texto import busca
from crawler_jurisprudencia_tj import crawler_jurisprudencia_tj
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class crawler_jurisprudencia_tjma():
	"""Crawler especializado em retornar textos da jurisprudência de segunda instância de Maranhão"""
	def __init__(self):
		crawler_jurisprudencia_tj.__init__(self)
		self.link_inicial = 'http://jurisconsult.tjma.jus.br/'
		self.pesquisa_livre = '//*[@id="txtChaveJurisprudencia"]'
		self.data_julgamento_inicial = 'dtaInicio'
		self.data_julgamento_final = 'dtaTermino'
		self.botao_pesquisar = 'btnConsultar'

	def download_tj(self, data_julg_ini, data_julg_fim, termo = 'acordam'):
		cursor = cursorConexao()
		driver = webdriver.Chrome(self.chromedriver)
		driver.get(self.link_inicial)
		driver.find_element_by_xpath(self.pesquisa_livre).send_keys(termo)
		driver.find_element_by_name(self.data_julgamento_inicial).send_keys(data_julg_ini)
		driver.find_element_by_name(self.data_julgamento_final).send_keys(data_julg_fim)
		driver.find_elements_by_name(self.botao_pesquisar)[2].click()
		texto = crawler_jurisprudencia_tj.extrai_texto_html(self,driver.page_source)
		tamanho = 5
		while True:
			try:
				time.sleep(3)
				links_proximos = driver.find_elements_by_class_name('linkQuery')
				texto = crawler_jurisprudencia_tj.extrai_texto_html(self,driver.page_source)
				cursor.execute('INSERT INTO justica_estadual.jurisprudencia_ma (ementas) value("%s")' % texto.replace('"',''))
				try:
					int(links_proximos[-1].text)
					driver.close()
					break
				except:
					driver.find_element_by_id('pagination').click()
			except Exception as e:
				driver.close()
				print(e)
				break

	def parser_acordaos(self,texto,cursor):
		numero = busca(r'\n(.*?)\(clique aqui para visualizar o processo\)', texto)
		data_disponibilizacao = busca(r'Data do registro do acordão\:\n(\d{2}/\d{2}/\d{4})',texto)
		julgador = busca(r'\nRelator.*?\:\n(.*?)\n',texto)
		orgao_julgador = busca(r'\n.rgão\:\n(.*?)\n',texto)
		if numero != '':
			cursor.execute('INSERT INTO jurisprudencia_2_inst.jurisprudencia_2_inst (tribunal, numero, data_decisao, orgao_julgador, julgador, texto_decisao) values ("%s","%s","%s","%s","%s","%s");' % ('ma',numero, data_disponibilizacao, orgao_julgador, julgador, texto.replace('"','').replace('/','').replace('\\','')))

if __name__ == '__main__':
	c = crawler_jurisprudencia_tjma()

	cursor = cursorConexao()
	cursor.execute('SELECT id, ementas from justica_estadual.jurisprudencia_ma;')
	dados = cursor.fetchall()
	for id_d, dado in dados:
		try:
			c.parser_acordaos(dado, cursor)
		except Exception as e:
			print(id_d, e)
		# try:
		# 	c.parser_acordaos(dado, cursor)
		# except Exception as e:
		# 	print(id_d,e)

	# try:
	# 	for a in c.lista_anos:
	# 		for m in range(len(c.lista_meses)):
	# 			c.download_tj('01'+c.lista_meses[m]+a,'28'+c.lista_meses[m]+a)
	# except Exception as e:
	# 	print(e)