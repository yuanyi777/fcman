import sys
import shlex
import xml.sax

class xml_reader(xml.sax.ContentHandler):

	def __init__(self):
		self.game_list = list()

		self.in_game = False

	def read_dat(self, filename):
		xml.sax.parse(filename, self)
		return self.game_list

	def startElement(self, tag, attributes):
		if tag == 'game':
			self.in_game = True
			self.game = dict()
			self.game['name'] = attributes['name']
		elif self.in_game:
			if tag == 'rom':
				try:
					self.game['crc'] = attributes['crc']
				except:
					self.game['crc'] = ''
				try:
					self.game['header'] = attributes['header']
				except:
					self.game['header'] = ''

	def endElement(self, tag):
		if tag == 'game':
			self.in_game = False
			self.game_list.append(self.game)


class cmdat_reader:

	def __init__(self):
		self.tokens = list()
		self.token_idx = 0
		self.game_list = list()

	def read_dat(self, filename):
		self.__read_tokens(filename)

		while self.__cur_tok() != None:
			if self.__cur_tok() == 'game':
				self.__handle_game()
			else:
				self.__advance()
		return self.game_list

	def __read_tokens(self, filename):
		fin = open(filename, 'r')
		for line in fin:
			while len(line) > 0 and (line[-1] == '\r' or line[-1] == '\n'):
				line = line[0:-1]
			t = shlex.split(line)
			for i in range(len(t)):
				if t[i] != '':
					self.tokens.append(t[i])
		fin.close()

	def __handle_game(self):
		self.__advance()
		if self.__cur_tok() == '(':
			game = dict()
			self.__advance()
			while self.__cur_tok() != None and self.__cur_tok() != ')':
				if self.__cur_tok() == 'name':
					self.__handle_name(game)
				elif self.__cur_tok() == 'description':
					self.__handle_description(game)
				elif self.__cur_tok() == 'rom':
					self.__handle_rom(game)
				else:
					self.__advance()
			self.__advance()
			self.game_list.append(game)

	def __handle_name(self, game):
		self.__advance()
		game['name'] = self.__cur_tok()
		self.__advance()

	def __handle_description(self, game):
		self.__advance()
		self.__advance()

	def __handle_rom(self, game):
		self.__advance()
		if self.__cur_tok() == '(':
			self.__advance()
			while self.__cur_tok() != None and self.__cur_tok() != ')':
				if self.__cur_tok() == 'crc':
					self.__advance()
					game['crc'] = self.__cur_tok()
				self.__advance()
			self.__advance()

	def __cur_tok(self):
		if self.token_idx < 0 or self.token_idx >= len(self.tokens):
			return None
		return self.tokens[self.token_idx]

	def __advance(self):
		self.token_idx += 1

if __name__ == '__main__':
	if len(sys.argv) > 1:
		#reader = cmdat_reader()
		reader = xml_reader()
		gl = reader.read_dat(sys.argv[1])
		print(gl)

