from HTMLParser import HTMLParser

class TemplateParser(HTMLParser):
	__startTitle = False
	__startTitleBar = False
	__startContent = False
	__startButtons = False
	__section = ''
	title = ''
	buttons = ''
	titleBar = ''
	content = ''
	def __searchId(self, attrs):
		"""
		
		Get id from attributes
		
		**Attributes**
		
		* ``attrs`` : Attributes as tuple (name,value)
		
		**Returns**
		
		* ``nodeId`` : element id
		
		"""
		nodeId = None
		for data in attrs:
			name, value = data
			if name == 'id':
				nodeId = value
		return nodeId
	def __getAttrs(self, attrs):
		"""Get attributes in html element"""
		attrsStr = ''
		for attr in attrs:
			attrsStr += ' ' + attr[0] + '="' + attr[1] + '"'
		return attrsStr
	def handle_starttag(self, tag, attrs):
		"""
		
		Handle template start tag: <section> and <title>
		
		"""		
		if tag == 'section':
			self.__section = ''
			nodeId = self.__searchId(attrs)
			if nodeId != None:
				if nodeId == 'id_sectionTitle':
					self.__startTitleBar = True
				elif nodeId == 'id_content':
					self.__startContent = True
				elif nodeId == 'id_sectionButton':
					self.__startButtons = True
		if tag == 'title':
			self.__startTitle = True
		if (self.__startTitleBar == True or self.__startContent == True or self.__startButtons == True) and tag != 'section':
			if len(attrs) != 0:
				self.__section += '<' + tag
				self.__section += self.__getAttrs(attrs)
				self.__section += '>'
			else:
				self.__section += '<' + tag + '>'
	def handle_endtag(self, tag):
		"""
		
		Handle template end tag: <section> and <title>
		
		"""
		if tag == 'section':
			if self.__startTitleBar == True:
				self.__titleBar = self.__section
				self.__startTitleBar = False
			elif self.__startContent == True:
				self.__content = self.__section
				self.__startContent = False
			elif self.__startButtons == True:
				self.__buttons = self.__section
				self.__startButtons = False
			self.__section = ''
		if tag == 'title':
			self.__startTitle = False
		if (self.__startTitleBar == True or self.__startContent == True or self.__startButtons == True) and tag != 'section':
			self.__section += '</' + tag + '>'
	def handle_data(self, data):
		"""
		
		Handle data for <title> and <section>
		
		"""
		if self.__startTitle == True:
			self.__title = data
		
		if self.__startTitleBar == True or self.__startContent == True or self.__startButtons == True:
			self.__section += data
	def get_title(self):
		return self.__title
	def get_buttons(self):
		return self.__buttons
	def get_title_bar(self):
		return self.__titleBar
	def get_content(self):
		return self.__content
	def set_title(self, value):
		self.__title = value
	def set_buttons(self, value):
		self.__buttons = value
	def set_title_bar(self, value):
		self.__titleBar = value
	def set_content(self, value):
		self.__content = value
	def del_title(self):
		del self.__title
	def del_buttons(self):
		del self.__buttons
	def del_title_bar(self):
		del self.__titleBar
	def del_content(self):
		del self.__content
	title = property(get_title, set_title, del_title, "title's docstring")
	buttons = property(get_buttons, set_buttons, del_buttons, "buttons's docstring")
	titleBar = property(get_title_bar, set_title_bar, del_title_bar, "titleBar's docstring")
	content = property(get_content, set_content, del_content, "content's docstring")

def getClass( kls ):
	parts = kls.split('.')
	module = ".".join(parts[:-1])
	m = __import__( module )
	for comp in parts[1:]:
		m = getattr(m, comp)            
	return m
