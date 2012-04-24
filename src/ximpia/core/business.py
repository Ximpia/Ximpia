import re
import traceback
import string
import simplejson as json
import types
import datetime

from django.http import HttpResponse
from django.core.mail import send_mail
from django.utils.translation import ugettext as _

from django.contrib.auth import login, authenticate, logout
from django.contrib.sessions.models import Session

from models import getResultOK, getResultERROR, XpMsgException, XpRegisterException, getBlankWfData
from models import View, Action, Application, ViewParamValue, Param, Workflow, WFParamValue, WorkflowView
from ximpia.util import ut_email
from ximpia.core.models import JsResultDict, Context as Ctx
from ximpia.core.constants import CoreConstants as K
from ximpia.core.data import WorkflowDataDAO, WorkflowDAO, WFParamValueDAO, ParamDAO, WFViewEntryParamDAO, ViewDAO, WorkflowViewDAO
from ximpia.core.choices import Choices
from ximpia.core.util import getClass

from ximpia.util.js import Form as _jsf

from ximpia import settings

class ComponentRegister(object):
	
	@staticmethod
	def registerView(appCode=None, viewName=None, myClass=None, method=None, **argsDict):
		"""Registers view
		@param appCode: Application code
		@param viewName: View name
		@param myClass: Class that shows view
		@param method: Method that shows view
		@param argsDict: Dictionary that contains the view entry parameters. Having format name => [value1, value2, ...]"""
		# TODO: Validate entry arguments: There is no None arguments, types, etc...
		# TODO: Register menus for view
		classPath = str(myClass).split("'")[1]
		app = Application.objects.get(code=appCode)
		view, created = View.objects.get_or_create(application=app, name=viewName)
		view.implementation = classPath + '.' + method
		view.save()
		# Parameters
		for name in argsDict:
			param = Param.objects.get(application=app, name=name)
			fields = argsDict[name]
			for value in fields:
				tuple = ViewParamValue.objects.get_or_create(view=view, name=param, operator='eq', value=value)
	
	@staticmethod
	def registerAction(appCode=None, actionName=None, myClass=None, method=None):
		"""Registers action
		@param appCode: Application code
		@param actionName: Action name
		@param myClass: Class for action
		@param method: Method that executes action"""
		classPath = str(myClass).split("'")[1]
		app = Application.objects.get(code=appCode)
		action, created = Action.objects.get_or_create(application=app, name=actionName)
		action.implementation = classPath + '.' + method
		action.save()
	
	@staticmethod
	def registerParam(appCode=None, name=None, title=None, paramType=None, isView=False, isWorkflow=False):
		"""Register view / workflow parameter
		@param appCode: Application code
		@param name: Parameter name
		@param title: Parameter title
		@param paramType: Parameter type
		@param view: Boolean if parameter used in view
		@param action: Boolean if parameter used in flow to resolve view"""
		app = Application.objects.get(code=appCode)
		param, created = Param.objects.get_or_create(application=app, name=name)
		if created:
			param.title = title
			param.paramType=paramType
			param.view = isView
			param.workflow = isWorkflow
			param.save()
		
	@staticmethod
	def registerFlow(appCode=None, flowCode=None, viewNameSource=None, viewNameTarget=None, actionName=None, order=10, 
			paramDict={}, viewParamDict={}):
		"""Reister flow
		@param appCode: Application code
		@param flowcode: Flow code
		@param viewNameSource: View name origin for flow
		@param viewNameTarget: View name destiny for flow
		@param actionName: Action name
		@param order: Order to evaluate view target resolution
		@param paramDict: Dictionary that contains the parameters to resolve views. Has the format name => (operator, value)"""
		app = Application.objects.get(code=appCode)
		viewSource = View.objects.get(application=app, name=viewNameSource)
		viewTarget = View.objects.get(application=app, name=viewNameTarget)
		action = Action.objects.get(application=app, name=actionName)
		flow, created = Workflow.objects.get_or_create(application=app, code=flowCode)
		flowView, created = WorkflowView.objects.get_or_create(flow=flow, viewSource=viewSource, viewTarget=viewTarget, 
								action=action, order=order)
		# Parameters
		for name in paramDict:
			operator, value = paramDict[name]
			wfParamValue, created = WFParamValue.objects.get_or_create(flow=flow, name=name, operator=operator, value=value)
		# Entry View parameters
		# TODO: Complete entry view parameters
	
	@staticmethod
	def registerMenu():
		"""Register menu item"""
		pass
	
	@staticmethod
	def registerAppOperation():
		"""Register application operation. It will be used in view search."""
		pass

class CommonBusiness(object):
	
	_ctx = None
	_request = None
	_errorDict = {}
	_resultDict = {}
	_form = None
	_postDict = {}
	_isBusinessOK = False
	_viewNameTarget = ''
	_isFormOK = None
	_views = {}
	_actions = {}
	_wf = None
	_f = None
	
	def __init__(self, ctx):
		self._ctx = ctx
		self._resultDict = getResultERROR([])
		self._postDict = ctx['post']
		self._errorDict = {}
		self._resultDict = {}
		self._isFormOK = None
		self._wf = WorkFlowBusiness(self._ctx)
		self._viewNameTarget = ''
	
	def buildJSONResult(self, resultDict):
		"""Builds json result
		@param resultDict: dict : Dictionary with json data
		@return: result : HttpResponse"""
		#print 'Dumping...'
		sResult = json.dumps(resultDict)
		#print 'sResult : ', sResult
		result = HttpResponse(sResult)
		return result
	
	def _addError(self, idError, form, errorField):
		"""Add error
		@param idError: String : Id of error
		@param form: Form
		@param errorField: String : The field inside class form"""
		if not self._errorDict.has_key(idError):
			self._errorDict[idError] = {}
		self._errorDict[idError] = form.fields[errorField].initial
	
	def _putParams(self, **args):
		"""Put parameters into workflow or navigation system.
		@param args: Arguments to insert into persistence"""
		if self._ctx[Ctx.IS_FLOW]:
			self._wf.putParams(**args)
		else:
			dd = json.loads(self._ctx[Ctx.FORM].base_fields['entryFields'].initial)
			for name in args:
				dd[name] = args[name]
			self._ctx[Ctx.FORM].base_fields['entryFields'].initial = json.dumps(dd)
	
	def _setTargetView(self, viewName):
		"""Set the target view for navigation."""
		self._viewNameTarget = viewName
	
	def _getTargetView(self):
		"""Get target view."""
		return self._viewNameTarget
	
	def _getParams(self, *nameList):
		"""Get parameter for list given, either from workflow dictionary or parameter dictionary in view.
		@param nameList: List of parameters to fetch"""
		valueDict = {}
		if self._ctx[Ctx.IS_FLOW]:
			print 'flow!!!!'
			for name in nameList:
				#value = self._wf.getParam(name)
				value = self._wf.getParamFromCtx(name)
				valueDict[name] = value
		else:
			print 'navigation!!!'
			dd = json.loads(self._ctx[Ctx.FORM].base_fields['entryFields'].initial)
			for name in nameList:
				if dd.has_key(name):
					valueDict[name] = dd[name]
		return valueDict
		
	
	def getErrorResultDict(self, errorDict, pageError=False):
		"""Get sorted error list to show in pop-up window
		@return: self._resultDict : ResultDict"""
		#dict = self._errorDict
		keyList = errorDict.keys()
		keyList.sort()
		myList = []
		for key in keyList:
			message = errorDict[key]
			index = key.find('id_')
			if pageError == False:
				if index == -1:
					myList.append(('id_' + key, message, False))
				else:
					myList.append((key, message, False))
			else:
				if index == -1:
					myList.append(('id_' + key, message, True))
				else:
					myList.append((key, message, True))
		self._resultDict = getResultERROR(myList)
		return self._resultDict

	def _doValidations(self, validationDict):
		"""Do all validations defined in validation dictionary"""
		bFormOK = self._ctx[Ctx.FORM].is_valid()
		if bFormOK:
			keys = self.validationDict.keys()
			for key in keys:
				oVal = eval(key)(self._ctx)
				for sFunc in self.validationDict[key]:
					oVal.eval(sFunc)()
				self._doErrors(oVal.getErrors())
		"""if self.isBusinessOK() and bFormOK:
			result = f(*argsTuple, **argsDict)
			# check errors
			return wrapped_f
		else:
			# Errors
			result = self._buildJSONResult(self._getErrorResultDict())
			return result"""
	
	def getForm(self):
		"""Get form"""
		#print 'form: ', self._ctx[Ctx.FORM]
		return self._ctx[Ctx.FORM]
	
	def setForm(self, form):
		"""Sets the form"""
		self._ctx[Ctx.FORM] = form
	
	def getPostDict(self):
		"""Get post dictionary. This will hold data even if form is not validated. If not validated cleaned_value will have no values"""
		return self._postDict
	
	def isBusinessOK(self):
		"""Checks that no errors have been generated in the validation methods
		@return: isOK : boolean"""
		if len(self._errorDict.keys()) == 0:
			self._isBusinessOK = True
		return self._isBusinessOK
	
	def _isFormValid(self):
		"""Is form valid?"""
		if self._isFormOK == None:
			self._isFormOK = self._ctx[Ctx.FORM].is_valid()
		return self._isFormOK

	def _isFormBsOK(self):
		"""Is form valid and business validations passed?"""
		bDo = False
		if len(self._errorDict.keys()) == 0:
			self._isBusinessOK = True
		if self._isFormOK == True and self._isBusinessOK == True:
			bDo = True
		return bDo
		
	def _f(self):
		"""Returns form from context"""
		return self._ctx[Ctx.FORM]
	
	def addError(self, field):
		"""Add error
		@param idError: String : Id of error
		@param form: Form
		@param errorField: String : The field inside class form"""
		form = self.getForm()
		#print 'form: ', form
		msgDict = _jsf.decodeArray(form.fields['errorMessages'].initial)
		idError = 'id_' + field
		if not self._errorDict.has_key(idError):
			self._errorDict[idError] = {}
		self._errorDict[idError] = msgDict['ERR_' + field]
		print '_errorDict : ', self._errorDict
	def getErrors(self):
		"""Get error dict
		@return: errorDict : Dictionary"""
		return self._errorDict	
	def getPost(self):
		"""Get post dictionary"""
		return self._ctx[Ctx.POST]
	
	def validateExists(self, dbDataList):
		"""Validates that db data provided exists. Error is shown in case does not exist.
		Db data contains data instance, query arguments in a dictionary
		and errorName for error message display at the front
		@param dbDataList: [dbObj, queryArgs, errorName]"""
		print 'validateExists...'
		print 'dbDataList : ', dbDataList
		for dbData in dbDataList:
			dbObj, qArgs, errName = dbData
			exists = dbObj.check(**qArgs)
			print 'validate Data: ', qArgs, exists, errName
			if not exists:
				self.addError(field=errName)
	
	def validateNotExists(self, dbDataList):
		"""Validates that db data provided does not exist. Error is shown in case exists.
		Db data contains data instance, query arguments in a dictionary
		and errorName for error message display at the front
		@param dbDataList: [dbObj, queryArgs, errorName]"""
		print 'validateNotExists...'
		print 'dbDataList : ', dbDataList
		for dbData in dbDataList:
			dbObj, qArgs, errName = dbData
			exists = dbObj.check(**qArgs)
			print 'exists : ', exists
			if exists:
				self.addError(field=errName)
		
	def validateContext(self, ctxDataList):
		"""Validates context variable. [[name, value, errName],...]"""
		for ctxData in ctxDataList:
			name, value, errName = ctxData
			if self._ctx[name] != value:
				self.addError(errName)
		
	def authenticateUser(self, **dd):
		"""Authenticates user and password
		dd: {'userName': $userName, 'password': $password, 'errorName': $errorName}"""
		qArgs = {'username': dd['userName'], 'password': dd['password']}
		user = authenticate(**qArgs)
		if user:
			pass
		else:
			self.addError(dd['errorName'])
		return user
	
	def isValid(self):
		"""Checks if no errors have been written to error container.
		If not, raises XpMsgException """
		self._errorDict = self.getErrors()
		print 'errorDict : ', self._errorDict
		if not self.isBusinessOK():
			# Here throw the BusinessException
			raise XpMsgException(None, _('Error in validating business layer'))
	def setOkMsg(self, idOK):
		"""Sets the ok message id"""
		msgDict = _jsf.decodeArray(self._f.fields['okMessages'].initial)
		self._f.fields['msg_ok'].initial = msgDict[idOK]

class WorkFlowBusiness (object):	
	_ctx = {}
	__wfData = {}
	
	def __init__(self, ctx):
		self._ctx = ctx
		self._dbWFData = WorkflowDataDAO(ctx, relatedDepth=2)
		self._dbWorkflow = WorkflowDAO(ctx, relatedDepth=2)
		self._dbWFView = WorkflowViewDAO(ctx, relatedDepth=2)
		self._dbWFParams = WFParamValueDAO(ctx, relatedDepth=2)
		self._dbView = ViewDAO(ctx)
		self._dbParam = ParamDAO(ctx)
		self._dbWFViewParam = WFViewEntryParamDAO(ctx, relatedDepth=2)
		self.__wfData = getBlankWfData({})
	
	def resolveFlowDataForUser(self, user, session, flowCode):
		"""Resolves flow for user and session key.
		@param user: User
		@param session: Session object
		@param flowCode: Flow code
		@return: resolvedFlow : Resolved flow for flow code , login user or session"""
		resolvedFlow = None
		sessionObj = Session.objects.get(session_key=session.session_key)
		if user.is_authenticated():
			flows = self._dbWFData.search(flow__code=flowCode, user=user)
			if len(flows) > 0:
				resolvedFlow = flows[0]
		else:
			flows = self._dbWFData.search(flow__code=flowCode, session=sessionObj)
			if len(flows) > 0:
				resolvedFlow = flows[0]
		if resolvedFlow == None:
			raise XpMsgException(None, _('Error in resolving workflow for user'))
		return resolvedFlow

	def resolveView(self, session, user, appCode, flowCode, viewNameSource, actionName):
		"""Search destiny views with origin viewSource and operation actionName
		@param viewNameSource: Origin view
		@param actionName: Action name
		@return: List of views"""
		viewTarget = ''
		flowViews = self._dbWFView.search(flow__application__code=appCode, flow__code=flowCode,
					viewSource__name=viewNameSource, action__name=actionName).order_by('order')
		params = self._dbWFParams.search(flowView__in=flowViews)
		paramFlowDict = {}
		for param in params:
			if not paramFlowDict.has_key(param.flowView.flow.code):
				paramFlowDict[param.flowView.flow.code] = []
			paramFlowDict[param.flowView.flow.code].append(param)
		wfDict = self.getFlowDataDict(session, user, flowCode)
		print 'wfDict: ', wfDict
		if len(flowViews) == 1:
			viewTarget = flowViews[0].viewTarget
		else:
			for flowCode in paramFlowDict:
				params = paramFlowDict[flowCode]
				check = True
				numberEval = 0
				for param in params:
					if wfDict['data'].has_key(param.name):
						if param.operator == Choices.OP_EQ:
							check = wfDict['data'][param.name] == param.value
						elif param.operator == Choices.OP_LT:
							check = wfDict['data'][param.name] < param.value
						elif param.operator == Choices.OP_GT:
							check = wfDict['data'][param.name] > param.value
						elif param.operator == Choices.OP_NE:
							check = wfDict['data'][param.name] != param.value
						if check == True:
							numberEval += 1
				if check == True and numberEval > 0:					
					viewTarget = flowViews.filter(flowView__code=flowCode).viewTarget
					break
		return viewTarget
		
	def putParams(self, **argsDict):
		"""Put list of workflow parameters in context
		@param flowCode: Flow code
		@param argsDict: Argument dictionary"""
		flowCode = self._ctx[Ctx.FLOW_CODE]
		flow = self._dbWorkflow.get(code=flowCode)
		if not self.__wfData:
			self.__wfData = getBlankWfData({})
		nameList = argsDict.keys()
		params = self._dbParam.search(name__in=nameList)
		if len(params) != 0:
			for name in argsDict:
				checkType = True
				paramFilter = params.filter(name=name)
				if not paramFilter:
					raise XpMsgException(None, _('Parameter "') + str(name) + _('" has not been registered'))
				paramDbType = paramFilter[0].paramType
				paramType = type(argsDict[name])
				if paramDbType == Choices.BASIC_TYPE_BOOL:
					checkType = paramType == types.BooleanType
				elif paramDbType == Choices.BASIC_TYPE_DATE:
					checkType = paramType is datetime.date
				elif paramDbType == Choices.BASIC_TYPE_FLOAT:
					checkType = paramType == types.FloatType
				elif paramDbType == Choices.BASIC_TYPE_INT:
					checkType = paramType == types.IntType
				elif paramDbType == Choices.BASIC_TYPE_LONG:
					checkType = paramType == types.LongType
				elif paramDbType == Choices.BASIC_TYPE_STR:
					checkType = paramType == types.StringType
				elif paramDbType == Choices.BASIC_TYPE_TIME:
					checkType = paramType is datetime.time
				if checkType == True:
					self.__wfData['data'][name] = argsDict[name]
				else:
					raise XpMsgException(None, _('Error in parameter type. "') + str(paramDbType) + _('" was expected and "') + str(paramType) + _('" was provided for parameter "') + str(name) + '"')
		else:
			raise XpMsgException(None, _('Parameters "') + ''.join(nameList) + _('" have not been registered'))
	
	def save(self, session, user, flowCode):
		"""Saves the workflow into database for user
		@param user: User
		@param flowCode: Flow code"""
		print '__wfData: ', self.__wfData
		if user.is_authenticated():
			flows = self._dbWFData.search(user=user, flow__code=flowCode)
			flow = flows[0]
			if flows > 0:
				flowData = _jsf.decode64dict(flow.data)
				for name in self.__wfData['data']:
					flowData['data'][name] = self.__wfData['data'][name]
		else:
			sessionObj = Session.objects.get(session_key=session.session_key)
			flows = self._dbWFData.search(session=sessionObj, flow__code=flowCode)
			flow = flows[0]
			if flows > 0:
				flowData = _jsf.decode64dict(flow.data)
				for name in self.__wfData['data']:
					flowData['data'][name] = self.__wfData['data'][name]
			else:
				raise XpMsgException(None, _('Flow data not found'))
		#if self.__wfData['viewName'] != '':
		flowData['viewName'] = self.__wfData['viewName']
		view = self._dbView.get(name=self.__wfData['viewName'])
		flow.view = view
		print 'save :: flowData: ', flowData
		flow.data = _jsf.encode64Dict(flowData)
		flow.save()
		return flow
	
	def resetFlow(self, session, user, flowCode, viewName):
		"""Reset flow. It deletes all workflow variables and view name
		@param user: User
		@param flowCode: Flow code"""
		try:
			flowData = self.resolveFlowDataForUser(user, session, flowCode)
			print 'resetFlow :: flowData: ', flowData
			self.__wfData = getBlankWfData({})
			self.__wfData['viewName'] = viewName
			print '__wfData: ', self.__wfData
			# Update flow data
			view = self._dbView.get(name=viewName)
			flowData.data = _jsf.encode64Dict(self.__wfData)
			flowData.view = view
			flowData.save()
		except XpMsgException:
			# Create flow data
			print 'create flow...', str(session), str(user)
			self.__wfData = getBlankWfData({})
			self.__wfData['viewName'] = viewName
			print '__wfData: ', self.__wfData
			view = self._dbView.get(name=viewName)
			workflow = self._dbWorkflow.get(code=flowCode)
			sessionObj = Session.objects.get(session_key=session.session_key)
			print 'session Model: ', Session.objects.get(session_key=session.session_key)
			if user.is_authenticated():
				self._dbWFData.create(session=sessionObj, user=user, flow=workflow, data = _jsf.encode64Dict(self.__wfData),
						view=view)
			else:
				self._dbWFData.create(session=sessionObj, flow=workflow, data = _jsf.encode64Dict(self.__wfData),
						view=view)

	def setViewName(self, viewName):
		"""Set view name in Workflow
		@param viewName: View name"""
		print 'setViewName :: ', self.__wfData
		self.__wfData['viewName'] = viewName
		print self.__wfData

	def getViewName(self):
		"""Get workflow view name.
		@return: viewName"""
		return self.__wfData['viewName']
	
	def getParam(self, name):
		"""Get workflow parameter from context
		@param name: Name
		@return: Param Value"""
		return self.__wfData['data'][name]
	
	def getParamFromCtx(self, name):
		"""Doc."""
		flowDataDict = self._ctx[Ctx.FLOW_DATA]
		return flowDataDict['data'][name]
	
	def buildFlowDataDict(self, flowData):
		"""Build the flow data dictionary having the flowData instance.
		@param flowData: Flow data
		@return: flowDataDict"""
		flowDataDict = _jsf.decode64dict(flowData.data)
		print 'build :: flowDataDict: ', flowDataDict
		return flowDataDict
	
	def getFlowDataDict(self, session, user, flowCode):
		"""Get flow data dictionary for user and flow code
		@param user: User
		@param flowCode: flowCode
		@return: flowData : Dictionary"""
		flowData = self.resolveFlowDataForUser(user, session, flowCode)
		flowDataDict = _jsf.decode64dict(flowData.data)
		print 'get :: flowDataDict: ', flowDataDict
		return flowDataDict
	
	def getFlowViewByAction(self, actionName):
		"""Get flow by action name. It queries the workflow data and returns flow associated with actionName
		@param actionName: Action name
		@return: flow: Workflow"""
		flowView = self._dbWFView.get(action__name=actionName)
		return flowView
	
	def getView(self, session, user, flowCode):
		"""Get view from flow
		@param user: User
		@param flowCode: Flow code
		@return: viewName"""
		flowDataDict = self.getFlowDataDict(session, user, flowCode)
		viewName = flowDataDict['viewName']
		return viewName
	
	def getViewParams(self, flowCode, viewName):
		"""Get view entry parameters for view and flow
		@param flowCode: Flow code
		@param viewName: View name
		@return: params : List of WFViewEntryParam"""
		params = self._dbWFViewParam.search(flowView__flow__code=flowCode, viewParam__view__name = viewName)
		print 'params: ', params
		paramDict = {}
		for param in params:
			paramDict[param.paramView.name] = param.paramView.value
		return paramDict

	def isLastView(self, viewNameSource, viewNameTarget, actionName):
		"""Checks if view is last in flow."""
		flowsView = self._dbWFView.search(viewSource__name=viewNameSource, action__name=actionName).order_by('-order')
		flowView = flowsView[0] if len(flowsView) != 0 else None
		isLastView = False
		if flowView != None and flowView.viewTarget.name == viewNameTarget:
			isLastView = True
		return isLastView
	
	def removeData(self, session, user, flowCode):
		"""Removes the workflow data for user or session."""
		flowData = self.resolveFlowDataForUser(user, session, flowCode)
		flowData.delete()
		

class EmailBusiness(object):
	#python -m smtpd -n -c DebuggingServer localhost:1025
	@staticmethod
	def send(xmlMessage, subsDict, recipientList):
		"""Send email
		@param keyName: keyName for datastore
		@subsDict : Dictionary with substitution values for template
		@param recipientList: List of emails to send message"""
		subject, message = ut_email.getMessage(xmlMessage)
		message = string.Template(message).substitute(**subsDict)
		send_mail(subject, message, settings.WEBMASTER_EMAIL, recipientList)


# ****************************************************
# **                DECORATORS                      **
# ****************************************************


class ShowSrvDecorator(object):
	"""Doc."""
	def __init__(self, *argsTuple, **argsDict):
		"""Doc."""
		self._form = argsTuple[0]
	def __call__(self, f):
		"""Doc."""
		def wrapped_f(*argsTuple, **argsDict):
			obj = argsTuple[0]
			obj._ctx[Ctx.FORM] = self._form()
			obj._f = self._form()
			try:
				f(*argsTuple, **argsDict)
				jsData = JsResultDict()
				obj._ctx[Ctx.FORM] = obj._f
				obj._ctx[Ctx.FORM].buildJsData(jsData)
				obj._ctx[Ctx.CTX] = json.dumps(jsData)
			except XpMsgException as e:
				if settings.DEBUG == True:
					print e
					print e.myException
					traceback.print_exc()
				errorDict = obj.getErrors()
				resultDict = obj.getErrorResultDict(errorDict, pageError=True)
				obj._ctx[Ctx.CTX] = json.dumps(resultDict)
			except Exception as e:
				raise
				if settings.DEBUG == True:
					print e
					traceback.print_exc()
				errorDict = {'': _('I cannot process your request due to an unexpected error. Sorry for the inconvenience, please retry later. Thanks')}
				resultDict = obj.getErrorResultDict(errorDict, pageError=True)
				obj._ctx[Ctx.CTX] = json.dumps(resultDict)
		return wrapped_f

class DoBusinessDecorator(object):
	"""Build response from jsData"""
	_pageError = False
	_form = None
	def __init__(self, *argsTuple, **argsDict):
		"""
		Options
		=======
		pageError: Show error detail as a list in a popup or show error in a message bar. pageError=True : Show error message bar
		form: Form class attached to the view
		"""
		if argsDict.has_key('pageError'):
			self._pageError = argsDict['pageError']
		else:
			self._pageError = False
		if argsDict.has_key('form'):
			self._form = argsDict['form']
	def __call__(self, f):
		def wrapped_f(*argsTuple, **argsDict):
			obj = argsTuple[0]
			#print 'DoBusinessDecorator :: data: ', argsTuple, argsDict
			try:
				#print 'DoBusinessDecorator :: ctx: ', obj._ctx.keys() 
				obj._ctx[Ctx.JS_DATA] = JsResultDict()
				if self._form != None:
					obj._ctx[Ctx.FORM] = self._form()
				f(*argsTuple, **argsDict)
				obj._ctx[Ctx.FORM].buildJsData(obj._ctx[Ctx.JS_DATA])
				#obj._ctx[Ctx.FORM].buildJsData(obj._ctx)
				result = obj.buildJSONResult(obj._ctx[Ctx.JS_DATA])
				#print obj._ctx[Ctx.JS_DATA]
				#print result
				return result
			except XpMsgException as e:
				errorDict = obj.getErrors()
				if settings.DEBUG == True:
					print errorDict
					print e
					print e.myException
					traceback.print_exc()
				if len(errorDict) != 0:
					result = obj.buildJSONResult(obj.getErrorResultDict(errorDict, pageError=self._pageError))
				else:
					raise
				return result
		return wrapped_f


class ValidateFormDecorator(object):
	"""Checks that form is valid, builds result, builds errors"""
	_form = None
	_pageError = False
	def __init__(self, *argsTuple, **argsDict):
		"""
		Options
		=======
		form: Form class
		"""
		# Sent by decorator
		self._form = argsTuple[0]
		"""if argsDict.has_key('pageError'):
			self._pageError = argsDict['pageError']
		else:
			self._pageError = False"""
	def __call__(self, f):
		"""Decorator call method"""
		def wrapped_f(*argsTuple, **argsDict):
			"""Doc."""
			#print 'ValidateFormDecorator :: ', argsTuple, argsDict
			obj = argsTuple[0]
			obj._ctx[Ctx.JS_DATA] = JsResultDict()
			obj._ctx[Ctx.FORM] = self._form(obj._ctx[Ctx.POST])
			bForm = obj._ctx[Ctx.FORM].is_valid()
			#obj._ctx[Ctx.FORM] = obj._f
			if bForm == True:
				result = f(*argsTuple, **argsDict)
				return result
				"""try:
					f(*argsTuple, **argsDict)
					obj._f.buildJsData(obj._ctx[Ctx.JS_DATA])
					result = obj.buildJSONResult(obj._ctx[Ctx.JS_DATA])
					#print result
					return result
				except XpMsgException as e:
					errorDict = obj.getErrors()
					if settings.DEBUG == True:
						print errorDict
						print e
						print e.myException
						traceback.print_exc()
					if len(errorDict) != 0:
						result = obj.buildJSONResult(obj.getErrorResultDict(errorDict, pageError=self._pageError))
					else:
						raise
					return result"""
				"""except Exception as e:
					if settings.DEBUG == True:
						print e
						traceback.print_exc()"""
			else:
				if settings.DEBUG == True:
					print 'Validation error!!!!!'
					#print obj._f
					print obj._ctx[Ctx.FORM].errors
					traceback.print_exc()
				errorDict = {'': 'Error validating your data. Check it out and send again'}
				result = obj.buildJSONResult(obj.getErrorResultDict(errorDict, pageError=True))
				return result
		return wrapped_f

class WFActionDecorator(object):
	_app = ''
	def __init__(self, *argsTuple, **argsDict):
		"""
		Options
		=======
		app: String : Application code
		"""
		# Sent by decorator
		if argsDict.has_key('app'):
			self._app = argsDict['app']
	def __call__(self, f):
		"""Decorator call method"""
		def wrapped_f(*argsTuple, **argsDict):
			obj = argsTuple[0]
			#print 'viewNameSource: ', obj._ctx[Ctx.VIEW_NAME_SOURCE]
			#print 'viewNameTarget: ', obj._ctx[Ctx.VIEW_NAME_TARGET]
			#print 'actionName: ', obj._ctx[Ctx.ACTION]
			#obj._wf = WorkFlowBusiness()
			actionName = obj._ctx[Ctx.ACTION]
			obj._ctx[Ctx.FLOW_CODE] = obj._wf.getFlowViewByAction(actionName).flow.code
			obj._ctx[Ctx.IS_FLOW] = True
			#print 'WFActionDecorator :: flowCode: ', obj._ctx[Ctx.FLOW_CODE]
			result = f(*argsTuple, **argsDict)
			# Resolve View
			#print 'session', 
			viewTarget = obj._wf.resolveView(obj._ctx[Ctx.SESSION], obj._ctx[Ctx.USER], 
						self._app, obj._ctx[Ctx.FLOW_CODE], obj._ctx[Ctx.VIEW_NAME_SOURCE], obj._ctx[Ctx.ACTION])
			viewName = viewTarget.name
			#print 'viewName: ', viewName
			# Insert view into workflow
			obj._wf.setViewName(viewName)
			viewAttrs = obj._wf.getViewParams(obj._ctx[Ctx.FLOW_CODE], viewName)
			#print 'viewAttrs: ', viewAttrs
			# Save workflow
			flowData = obj._wf.save(obj._ctx[Ctx.SESSION], obj._ctx[Ctx.USER], obj._ctx[Ctx.FLOW_CODE])
			# Set Flow data dictionary into context
			obj._ctx[Ctx.FLOW_DATA] = obj._wf.buildFlowDataDict(flowData)
			#print 'flowDataDict: ', obj._ctx[Ctx.FLOW_DATA]
			# Delete user flow ???
			if obj._wf.isLastView(obj._ctx[Ctx.VIEW_NAME_SOURCE], viewName, obj._ctx[Ctx.ACTION]):
				obj._wf.removeData(obj._ctx[Ctx.SESSION], obj._ctx[Ctx.USER], obj._ctx[Ctx.FLOW_CODE])
			# Show View
			impl = viewTarget.implementation
			implFields = impl.split('.')
			method = implFields[len(implFields)-1]
			classPath = ".".join(implFields[:-1])
			cls = getClass( classPath )
			objView = cls(obj._ctx)
			if (len(viewAttrs) == 0) :
				result = eval('objView.' + method)()
			else:
				result = eval('objView.' + method)(**viewAttrs)
			return result
		return wrapped_f

class WFViewStartDecorator(object):
	_flows = []
	def __init__(self, *argsTuple, **argsDict):
		# Sent by decorator
		self._flows = argsDict['flows']
	def __call__(self, f):
		"""Decorator call method"""
		def wrapped_f(*argsTuple, **argsDict):
			#print 'WFViewstartDecorator :: ', argsTuple, argsDict
			obj = argsTuple[0]
			#obj._wf = WorkFlowBusiness(obj._ctx)
			for flowCode in self._flows:
				obj._wf.resetFlow(obj._ctx[Ctx.SESSION], obj._ctx[Ctx.USER], flowCode, obj._ctx[Ctx.VIEW_NAME_SOURCE])
			result = f(*argsTuple, **argsDict)
			return result
		return wrapped_f

class NavActionDecorator(object):
	"""Navigation from a view to another view using actionName and action method."""
	_viewNameTarget = ''
	def __init__(self, *argsTuple, **argsDict):
		"""
		Options
		=======
		viewNameTarget: String : The view name end point of navigation
		"""
		# Sent by decorator
		if argsDict.has_key('viewNameTarget'):
			self._viewNameTarget = argsDict['viewNameTarget']
	def __call__(self, f):
		"""Decorator call method"""
		def wrapped_f(*argsTuple, **argsDict):
			obj = argsTuple[0]
			# Do action
			f(*argsTuple, **argsDict)
			# Get view
			dbView = ViewDAO(obj._ctx)
			if self._viewNameTarget == '':
				self._viewNameTarget = obj.getTargetView()
			viewTarget = dbView.get(name=self._viewNameTarget)
			# Show View
			impl = viewTarget.implementation
			implFields = impl.split('.')
			method = implFields[len(implFields)-1]
			classPath = ".".join(implFields[:-1])
			cls = getClass( classPath )
			objView = cls(obj._ctx)
			result = eval('objView.' + method)()
			return result
		return wrapped_f
