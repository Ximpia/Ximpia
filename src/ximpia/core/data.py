import traceback

from django.utils.translation import ugettext as _
from ximpia.core.models import XpMsgException, CoreParam, Application, UserSocial, Action, ApplicationAccess, CoreXmlMessage
from ximpia.core.models import Menu, MenuParam, View, ViewMenu, Workflow, WFParam, WFParamValue 

class CommonDAO(object):	

	_numberMatches = 0
	_ctx = None
	_model = None
	_relatedFields = ()
	_relatedDepth = None

	def __init__(self, ctx, relatedFields=(), relatedDepth=None, numberMatches=100):
		"""@param ctx: Context: 
		@param relatedFields: tuple containing the fields to fetch data in the same query
		@param relatedDepth: Number of depth relationships to follow. The higher the number, the bigger the query
		@param numberMatches: Number of rows for queries that support paging"""
		self._ctx = ctx
		self._relatedFields = relatedFields
		self._relatedDepth = relatedDepth
		self._numberMatches = numberMatches
		if relatedDepth != None and len(relatedFields) != 0:
			raise XpMsgException(None, _('relatedFields and relatedDepth cannot be combined. One of them must only be informed.'))
	
	def _processRelated(self):
		"""Process related objects using fields and depth, class attributes _relatedFields and _relatedDepth"""
		if len(self._relatedFields) != 0 or self._relatedDepth != None:
			if len(self._relatedFields) != 0:
				dbObj = self._model.objects.select_related(self._relatedFields)
			elif self._relatedDepth != None:
				dbObj = self._model.objects.select_related(depth=self._relatedDepth)
		else:
			dbObj = self._model.objects
		return dbObj
		
	def _cleanDict(self, dd):
		"""Clean dict removing xpXXX fields.
		@param dict: Dictionary
		@return: dictNew : New dictionary without xpXXX fields"""
		fields = dd.keys()
		dictNew = {}
		for sKey in fields:
			if sKey.find('xp') == 0:
				pass
			else:
				dictNew[sKey] = dict[sKey]
		return dictNew
	
	def _getPagingStartEnd(self, page, numberMatches):
		"""Get tuple (iStart, iEnd)"""
		iStart = (page-1)*numberMatches
		iEnd = iStart+numberMatches
		values = (iStart, iEnd)
		return values
	
	def getMap(self, idList):
		"""Get object map for a list of ids 
		@param idList: 
		@param bFull: boolean : Follows all foreign keys
		@return: Dict[id]: object"""
		dd = {}
		if len(idList) != 0:
			"""if useModel != None:
				dbObj = self.useModel.objects
			else:
				dbObj = self._model.objects
			if bFull == True:
				dbObj = dbObj.select_related()"""
			dbObj = self._processRelated()
			fields = dbObj.filter(id__in=idList)
			for obj in fields:
				dd[obj.id] = obj
		return dd
	
	def getById(self, fieldId, bFull=False):
		"""Get model object by id
		@param id: Object id
		@param bFull: boolean : Follows all foreign keys
		@return: Model object"""
		try:
			dbObj = self._processRelated()
			obj = dbObj.get(id=fieldId)
		except Exception as e:
			raise XpMsgException(e, _('Error in get object by id ') + str(id) + _(' in model ') + str(self._model))
		return obj
	
	def check(self, **qsArgs):
		"""Checks if object exists
		@param qsArgs: query arguments
		@return: Boolean"""
		try:
			dbObj = self._model.objects
			exists = dbObj.filter(**qsArgs).exists()
		except Exception as e:
			raise XpMsgException(e, _('Error in get object by id ') + str(id) + _(' in model ') + str(self._model))
		return exists
	
	def get(self, **qsArgs):
		"""Get object
		@param qsArgs: query arguments
		@return: Model Object"""
		try:
			dbObj = self._processRelated()
			data = dbObj.get(**qsArgs)
		except Exception as e:
			raise XpMsgException(e, _('Error in get object ') + str(id) + _(' in model ') + str(self._model))
		return data	
	
	def create(self, **qsArgs):
		"""Create object
		@param qsArgs: Query arguments
		@return: Data Object"""
		try:
			dbObj = self._model.objects
			data = dbObj.create(**qsArgs)
		except Exception as e:
			raise XpMsgException(e, _('Error in create object ') + str(id) + _(' in model ') + str(self._model))
		return data
	
	def getCreate(self, **qsArgs):
		"""Get or create object. If exists, gets the current value. If does not exist, creates data.
		@param qsArgs: Query arguments
		@return: tuple (Data Object, bCreated)"""
		try:
			dbObj = self._model.objects
			xpTuple = dbObj.get_or_create(**qsArgs)
		except Exception as e:
			raise XpMsgException(e, _('Error in get or create object ') + str(id) + _(' in model ') + str(self._model))
		return xpTuple
	
	def deleteById(self, xpId):
		"""Delete model object by id
		@param id: Object id
		@return: Model object"""
		try:
			xpList = self._model.objects.filter(id=xpId)
			xpObject = xpList[0]
			xpList.delete()
		except Exception as e:
			raise XpMsgException(e, _('Error delete object by id ') + str(id))
		return xpObject
	
	def filterData(self, **argsDict):
		"""Search a model table with ordering support and paging
		@param bFull: boolean : Follows all foreign keys
		@return: list : List of model objects"""
		try:
			iNumberMatches = self._numberMatches
			if argsDict.has_key('xpNumberMatches'):
				iNumberMatches = argsDict['xpNumberMatches']
			page = 1
			if argsDict.has_key('xpPage'):
				page = int(argsDict['xpPage'])
			iStart, iEnd = self._getPagingStartEnd(page, iNumberMatches)
			orderByTuple = ()
			if argsDict.has_key('xpOrderBy'):
				orderByTuple = argsDict['xpOrderBy']
			ArgsDict = self._cleanDict(argsDict)
			dbObj = self._processRelated()
			if len(orderByTuple) != 0:
				dbObj = self._model.objects.order_by(*orderByTuple)
			xpList = dbObj.filter(**ArgsDict)[iStart:iEnd]			
		except Exception as e:
			raise XpMsgException(e, _('Error in search table model ') + str(self._model))
		return xpList	
		
	def getAll(self):
		"""Get all rows from table
		@param bFull: boolean : Follows all foreign keys
		@return: list"""
		try:
			dbObj = self._processRelated()
			xpList = dbObj.all()
		except Exception as e:
			raise XpMsgException(e, _('Error in getting all fields from ') + str(self._model))
		return xpList
	
	def _getCtx(self):
		"""Get context"""
		return self._ctx

	def _doManyById(self, model, idList, field):
		"""Does request for map for list of ids (one query). Then processes map and adds to object obtained objects.
		@param idList: List
		@param object: Model"""
		xpDict = self.getMap(idList, userModel=model)
		for idTarget in xpDict.keys():
			addModel = xpDict[idTarget]
			field.add(addModel)
	
	def _doManyByName(self, model, nameList, field):
		"""Does request for map for list of ids (one query). Then processes map and adds to object obtained objects.
		@param idList: List
		@param object: Model"""
		for value in nameList:
			fields = model.objects.get_or_create(name=value)
			nameModel = fields[0]
			field.add(nameModel)

	ctx = property(_getCtx, None)

class CoreParameterDAO(CommonDAO):
	def __init__(self, ctx, *ArgsTuple, **ArgsDict):
		super(CoreParameterDAO, self).__init__(ctx, *ArgsTuple, **ArgsDict)
		self._model = CoreParam

class ApplicationDAO(CommonDAO):
	def __init__(self, ctx, *ArgsTuple, **ArgsDict):
		super(ApplicationDAO, self).__init__(ctx, *ArgsTuple, **ArgsDict)
		self._model = Application

class UserSocialDAO(CommonDAO):
	def __init__(self, ctx, *ArgsTuple, **ArgsDict):
		super(UserSocialDAO, self).__init__(ctx, *ArgsTuple, **ArgsDict)
		self._model = UserSocial

class ActionDAO(CommonDAO):
	def __init__(self, ctx, *ArgsTuple, **ArgsDict):
		super(ActionDAO, self).__init__(ctx, *ArgsTuple, **ArgsDict)
		self._model = Action

class ApplicationAccessDAO(CommonDAO):
	def __init__(self, ctx, *ArgsTuple, **ArgsDict):
		super(ApplicationAccessDAO, self).__init__(ctx, *ArgsTuple, **ArgsDict)
		self._model = ApplicationAccess

class CoreXMLMessageDAO(CommonDAO):
	def __init__(self, ctx, *ArgsTuple, **ArgsDict):
		super(CoreXMLMessageDAO, self).__init__(ctx, *ArgsTuple, **ArgsDict)
		self._model = CoreXmlMessage

class MenuDAO(CommonDAO):
	def __init__(self, ctx, *ArgsTuple, **ArgsDict):
		super(MenuDAO, self).__init__(ctx, *ArgsTuple, **ArgsDict)
		self._model = Menu

class MenuParamDAO(CommonDAO):
	def __init__(self, ctx, *ArgsTuple, **ArgsDict):
		super(MenuParamDAO, self).__init__(ctx, *ArgsTuple, **ArgsDict)
		self._model = MenuParam

class ViewDAO(CommonDAO):
	def __init__(self, ctx, *ArgsTuple, **ArgsDict):
		super(ViewDAO, self).__init__(ctx, *ArgsTuple, **ArgsDict)
		self._model = View

class ViewMenuDAO(CommonDAO):
	def __init__(self, ctx, *ArgsTuple, **ArgsDict):
		super(ViewMenuDAO, self).__init__(ctx, *ArgsTuple, **ArgsDict)
		self._model = ViewMenu

class WorkflowDAO(CommonDAO):
	def __init__(self, ctx, *ArgsTuple, **ArgsDict):
		super(WorkflowDAO, self).__init__(ctx, *ArgsTuple, **ArgsDict)
		self._model = Workflow

class WFParamDAO(CommonDAO):
	def __init__(self, ctx, *ArgsTuple, **ArgsDict):
		super(WFParamDAO, self).__init__(ctx, *ArgsTuple, **ArgsDict)
		self._model = WFParam

class WFParamValueDAO(CommonDAO):
	def __init__(self, ctx, *ArgsTuple, **ArgsDict):
		super(WFParamValueDAO, self).__init__(ctx, *ArgsTuple, **ArgsDict)
		self._model = WFParamValue
