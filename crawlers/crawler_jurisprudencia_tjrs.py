from bs4 import BeautifulSoup
from crawler_jurisprudencia_tj import crawler_jurisprudencia_tj
from crawlerJus import crawlerJus
from common_nlp.parse_texto import busca
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from common.conexao_local import cursorConexao
import sys, re, time

class crawler_jurisprudencia_tjrs():
	"""Crawler especializado em retornar textos da jurisprudência de segunda instância do Rio Grande do Sul"""
	def __init__(self):
		crawler_jurisprudencia_tj.__init__(self)
		self.link_inicial = 'http://www.tjrs.jus.br/busca/?tb=jurisnova&partialfields=tribunal%3ATribunal%2520de%2520Justi%25C3%25A7a%2520do%2520RS.(TipoDecisao%3Aac%25C3%25B3rd%25C3%25A3o|TipoDecisao%3Amonocr%25C3%25A1tica|TipoDecisao:null)&t=s&pesq=ementario.#main_res_juris'
		self.pesquisa_livre = '//*[@id="q"]'
		self.botao_pesquisar = '//*[@id="conteudo"]/form/div[1]/div/div/input'
		self.botao_proximo_iniXP = '//*[@id="main_res_juris"]/div/div[2]/span[1]/a'
		self.botao_proximoXP = '//*[@id="main_res_juris"]/div/div[2]/span[3]/a'
		self.data_iniXP = '//*[@id="dia1"]'
		self.data_fimXP = '//*[@id="dia2"]'
		self.tabela_colunas = 'justica_estadual.jurisprudencia_rs (ementas)'

	def download_tj(self,data_ini,data_fim):
		cursor = cursorConexao()
		driver = webdriver.Chrome(self.chromedriver)
		driver.get(self.link_inicial)
		driver.find_element_by_xpath(self.pesquisa_livre).send_keys('a')
		time.sleep(1)
		driver.find_element_by_xpath(self.data_iniXP).send_keys(data_ini)
		time.sleep(1)
		driver.find_element_by_xpath(self.data_fimXP).send_keys(data_fim)
		time.sleep(1)
		driver.find_element_by_xpath(self.botao_pesquisar).click()
		links_inteiro_teor = driver.find_elements_by_link_text('html')
		for l in links_inteiro_teor:
			try:
				texto = l.get_attribute('href')
				cursor.execute('INSERT INTO %s value ("%s");' % (self.tabela_colunas,texto))		
			except:
				pass
		try:
			driver.find_element_by_xpath(self.botao_proximo_iniXP).click()
		except:
			driver.close()
			return
		while True:
			time.sleep(1)
			links_inteiro_teor = driver.find_elements_by_link_text('html')
			for l in links_inteiro_teor:
				try:
					texto = l.get_attribute('href')
					cursor.execute('INSERT INTO %s value ("%s");' % (self.tabela_colunas,texto))		
				except:
					pass
			try:
				driver.find_element_by_xpath(self.botao_proximoXP).click()
			except:
				driver.close()
				return


	def download_2_inst(self, links):
		crawler = crawlerJus()
		for link in links:
			texto = crawler.baixa_texto_html(link).strip().replace('\\','').replace('/','').replace('"','')

	
	def parser_acordaos(self,links):
		cursor = cursorConexao()
		crawler = crawlerJus()
		contador = 1
		for id_p, link in links:
			try:
				texto = crawler.baixa_texto_html(link).strip().replace('\\','').replace('/','').replace('"','')
				if texto != '':
					numero = busca(r'\n?Nº\s*?(.*?)\n', texto)
					cursor.execute('INSERT INTO justica_estadual.jurisprudencia_rs_2 (numero, texto_decisao) values ("%s","%s");' % (numero, texto))
				print(contador)
				contador += 1
			except Exception as e:
				print(id_p,e)

if __name__ == '__main__':
	c = crawler_jurisprudencia_tjrs()

	cursor = cursorConexao()
	cursor.execute('SELECT id, ementas from justica_estadual.jurisprudencia_rs;')
	links = cursor.fetchall()
	c.parser_acordaos(links)

	# print('comecei ',c.__class__.__name__)
	# try:
	# 	for l in range(1,len(c.lista_anos)):
	# 		print(c.lista_anos[l],'\n')
	# 		for m in range(len(c.lista_meses)):
	# 			for i in range(1,8):
	# 				try:
	# 					c.download_tj('0'+str(i)+c.lista_meses[m]+c.lista_anos[l],'0'+str(i+1)+c.lista_meses[m]+c.lista_anos[l])
	# 				except Exception as e:
	# 					print(e)		
	# 			for i in range(10,27):
	# 				try:
	# 					c.download_tj(str(i)+c.lista_meses[m]+c.lista_anos[l],str(i+1)+c.lista_meses[m]+c.lista_anos[l])
	# 				except Exception as e:
	# 					print(e)
	# except Exception as e:
	# 	print('finalizei o ano com erro ',e)

		

