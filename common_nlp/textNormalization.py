from nltk.tokenize import RegexpTokenizer
from gensim import corpora, models
import gensim, nltk

class textNormalization():
	"""Manipula topic models"""
	def __init__(self):
		pass

	def tokenizer(self):
		return RegexpTokenizer(r'\w+')

	def file_to_string(self,arq):
		arquivo = open(arq,'r')
		return ''.join([line for line in arquivo])

	def normalize_texts(self,texts,one_text = False):
		normal_texts = []
		tk = self.tokenizer()
		stopwords = nltk.corpus.stopwords.words('portuguese')
		if one_text:
			texts = [texts]
		for t in texts:
			texto_bruto = t.lower()
			tokens = tk.tokenize(texto_bruto)
			texto_processado = []
			for tkn in tokens:
				if tkn not in stopwords:
					texto_processado.append(tkn)
			normal_texts.append(texto_processado)
		if one_text:
			return texto_processado
		return normal_texts

	def dicionario_invertido_id_texto(self,dados):
		dicionario_i = {}
		for id_,texto in dados:
			dicionario_i_text = set(self.normalize_texts(texto,one_text=True))
			for w in dicionario_i_text:
				if w in dicionario_i:
					dicionario_i[w].append(id_)
				else:
					dicionario_i[w] = [id_]
		return dicionario_i