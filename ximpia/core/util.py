# coding: utf-8

# python
import os
from HTMLParser import HTMLParser

# django
from django.conf import settings

class AttrDict(dict):
	def __getattr__(self, attr):
		return self[attr]
	def __setattr__(self, attr, value):
		self[attr] = value
	def __getstate__(self):
		return self.__dict__

def get_class(kls_path):
	"""	
	Get class
	"""
	parts = kls_path.split('.')
	module = ".".join(parts[:-1])
	m = __import__( module )
	for comp in parts[1:]:
		m = getattr(m, comp)            
	return m

def get_project(app):
	dj_apps = settings.INSTALLED_APPS
	for dj_app in dj_apps:
		if dj_app.find('.' + app) != -1:
			return dj_app.split('.')[0]
	return None

def get_instances(args, ctx):
	"""
	We should inyect ctx into the parent of DAO or business, using super
	TODO: Need to change all context assignment in the parent clases: DAO, business
	"""
	from models import XpMsgException
	instances = []
	for arg in args:
		if not isinstance(arg, str):
			raise XpMsgException(AttributeError, _('List of instances must be string'))
		# get class in this application, path
		if arg.find('.') != -1:
			# we have path, just get class and instantiate with context
			cls = get_class(arg)
			if arg.find('.data.') != -1 or arg.find('DAO') != -1:
				instances.append(cls(ctx))
			else:
				instances.append(cls(ctx))
		else:
			if arg.find('DAO') != -1:
				# data class name and no path, resolve as data class in this app
				cls = get_class(ctx.app + '.data.' + arg)
				instances.append(cls(ctx))
			else:
				# business class
				cls = get_class(ctx.app + '.business.' + arg)
				instances.append(cls(ctx))
	return instances

# Import settings and logging
settings = get_class(os.getenv("DJANGO_SETTINGS_MODULE"))
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(__name__)

class TemplateParser(HTMLParser):
	__startTitle = False
	__startTitleBar = False
	__startContent = False
	__startButtons = False
	__startIdView = False
	__section = ''
	title = ''
	buttons = ''
	titleBar = ''
	content = ''
	id_view = ''
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
			if attr[1] != None:
				attrsStr += ' ' + attr[0] + '="' + attr[1] + '"'
			else:
				attrsStr += ' ' + attr[0]
		return attrsStr
	def handle_startendtag(self, tag, attrs):
		"""
		Handle start and end tags, of type <br/>, <img ... />, etc...
		"""
		if (self.__startTitleBar == True or self.__startContent == True or self.__startButtons == True) and tag != 'section':
			if len(attrs) != 0:
				self.__section += '<' + tag
				self.__section += self.__getAttrs(attrs)
				self.__section += '/>'
			else:
				self.__section += '<' + tag + '/>'
	def handle_starttag(self, tag, attrs):
		"""
		
		Handle template start tag: <section> and <title>
		
		<br/> -> <br></br>
		
		"""
		attrDict = {}
		for (name, value) in attrs:
			attrDict[name] = value
			if name == 'id' and value == 'id_view':
				self.__startIdView = True
		if self.__startIdView == True:
			self.__id_view = '<div'
			self.__id_view += self.__getAttrs(attrs)
			self.__id_view += '>'
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
		if tag == 'div':
			if self.__startIdView == True:
				self.__startIdView = False
				self.__id_view += ' </div>'
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
		
		if self.__startIdView == True:
			self.__id_view += data
		
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
	def get_id_view(self):
		return self.__id_view
	def set_id_view(self, value):
		self.__id_view = value
	def del_id_view(self):
		del self.__id_view

	title = property(get_title, set_title, del_title, "title's docstring")
	buttons = property(get_buttons, set_buttons, del_buttons, "buttons's docstring")
	titleBar = property(get_title_bar, set_title_bar, del_title_bar, "titleBar's docstring")
	content = property(get_content, set_content, del_content, "content's docstring")
	id_view = property(get_id_view, set_id_view, del_id_view, "id_view's docstring")

class AppTemplateParser(HTMLParser):
	"""
	Application template parser: Parses style, script and footer tags as well as link styles.
	
	Application must be set before calling feed method
	"""
	__app = ''
	__startFooter = False
	__startScript = False
	__startStyle = False
	__scripts = ''
	__styles = ''
	__footer = ''
	def feed_app(self, data, app):
		self.__app = app
		self.feed(data)
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
			if attr[1] != None:
				attrsStr += ' ' + attr[0] + '="' + attr[1] + '"'
			else:
				attrsStr += ' ' + attr[0]
		return attrsStr
	def __hasAttributeStylesheet(self, attrs):
		for attr in attrs:
			if attr[0] == 'rel' and attr[1].lower() == 'stylesheet':
				return True
		return False
	def handle_startendtag(self, tag, attrs):
		"""
		Handle start and end tags, of type <link rel="stylesheet" type="text/css" href="/static/jQueryThemes/base/jquery-ui.css" />
		"""
		logger.debug('AppTemplateParser.handle_startendtag :: app: %s' % (self.__app) )
		if tag == 'link' and self.__hasAttributeStylesheet(attrs):
			if len(attrs) != 0:
				self.__styles += '<' + tag
				self.__styles += self.__getAttrs(attrs)
				self.__styles += ' data-xp-app="' + self.__app + '"/>'
			else:
				self.__styles += '<' + tag + ' data-xp-app="' + self.__app + '/>'
	def handle_starttag(self, tag, attrs):
		"""
		Handle template start tag: <script></script> and <footer></footer>
		"""
		logger.debug('AppTemplateParser.handle_starttag :: app: %s' % (self.__app) )
		if tag == 'footer':
			self.__startFooter = True
			if len(attrs) != 0:
				self.__footer += '<' + tag
				self.__footer += self.__getAttrs(attrs)
				self.__footer += ' data-xp-app="' + self.__app + '" >'
			else:
				self.__footer += '<' + tag + ' data-xp-app="' + self.__app + '" >'
		elif tag == 'script':
			self.__startScript = True
			if len(attrs) != 0:
				self.__scripts += '<' + tag
				self.__scripts += self.__getAttrs(attrs)
				self.__scripts += ' data-xp-app="' + self.__app + '" >'
			else:
				self.__scripts += '<' + tag + ' data-xp-app="' + self.__app + '" >'
		elif tag == 'style':
			self.__startStyle = True
			if len(attrs) != 0:
				self.__styles += '<' + tag
				self.__styles += self.__getAttrs(attrs)
				self.__styles += ' data-xp-app="' + self.__app + '" >'
			else:
				self.__styles += '<' + tag + '>'
		else:
			if self.__startFooter == True:
				if len(attrs) != 0:
					self.__footer += '<' + tag
					self.__footer += self.__getAttrs(attrs)
					self.__footer += ' data-xp-app="' + self.__app + '" >'
				else:
					self.__footer += '<' + tag + ' data-xp-app="' + self.__app + '" >'
	def handle_endtag(self, tag):
		"""		
		Handle template end tag: <script></script> and <footer></footer>
		"""
		logger.debug('AppTemplateParser.handle_endtag :: app: %s' % (self.__app) )
		if tag == 'footer':
			self.__startFooter = False
			self.__footer += '</' + tag + '>'
		elif tag == 'script':
			self.__startScript = False
			self.__scripts += '</' + tag + '>'
		elif tag == 'style':
			self.__startStyle = False
			self.__styles += '</' + tag + '>'
		else:
			if self.__startFooter == True:
				self.__footer += '</' + tag + '>'
	def handle_data(self, data):
		"""
		Handle data for <script></script> and <footer></footer>
		"""
		if self.__startFooter == True:
			self.__footer += data
		elif self.__startStyle == True:
			self.__styles += data
		elif self.__startScript == True:
			self.__scripts += data

	def get_scripts(self):
		return self.__scripts
	def get_styles(self):
		return self.__styles
	def get_footer(self):
		return self.__footer
	def set_scripts(self, value):
		self.__scripts = value
	def set_styles(self, value):
		self.__styles = value
	def set_footer(self, value):
		self.__footer = value
	def del_scripts(self):
		del self.__scripts
	def del_styles(self):
		del self.__styles
	def del_footer(self):
		del self.__footer
	def get_app(self):
		return self.__app
	def set_app(self, value):
		self.__app = value
	def del_app(self):
		del self.__app
	
	scripts = property(get_scripts, set_scripts, del_scripts, "scripts's docstring")
	styles = property(get_styles, set_styles, del_styles, "styles's docstring")
	footer = property(get_footer, set_footer, del_footer, "footer's docstring")
	app = property(get_app, set_app, del_app, "app's docstring")
