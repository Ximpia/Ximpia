from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group
from filebrowser.fields import FileBrowseField

from ximpia.core.models import BaseModel, MetaKey
import ximpia.core.constants as CoreK
from ximpia.core.choices import Choices as CoreChoices

import constants as K
from choices import Choices

class Param ( BaseModel ):
	
	"""
	
	Site Parameters
	
	**Attributes**
	
	* ``mode``:CharField(20) : Parameter mode. When parameters have same mode, table with key->value can be obtained.
	* ``name``:CharField(20) : Parameter name
	* ``value``:CharField(100) : Parameter value
	* ``paramType``:Charfield(10) : Parameter type: string, integer, date
	
	"""
	
	id = models.AutoField(primary_key=True, db_column='ID_SITE_PARAMETER')
	mode = models.CharField(max_length=20, db_column='MODE', null=True, blank=True, 
			verbose_name=_('Mode'), help_text=_('Parameter Mode'))
	name = models.CharField(max_length=20, db_column='NAME',
			verbose_name=_('Name'), help_text=_('Parameter Name'))
	value = models.CharField(max_length=100, null=True, blank=True, db_column='VALUE', 
			verbose_name=_('Value'), help_text=_('Parameter Value'))
	paramType = models.CharField(max_length=10, choices=CoreChoices.PARAM_TYPE, default=CoreChoices.PARAM_TYPE_STRING, 
			db_column='PARAM_TYPE',
			verbose_name=_('Parameter Type'), help_text=_('Type: either parameter or table'))
	def __unicode__(self):
		return str(self.mode) + ' - ' + str(self.name)
	class Meta:
		db_table = 'SITE_PARAMETER'
		verbose_name = "Parameter"
		verbose_name_plural = "Parameters"

class MetaKey( BaseModel ):
	"""
	
	Model to store the keys allowed for meta values. Used for META tables and settings tables.
	
	**Attributes**
	
	* ``name``:CharField(20) : Key META name
	
	**Relationships**
	
	* ``keyType`` : META Key type from SITE_PARAMETER table
	
	"""
	name = models.CharField(max_length=20,
	        verbose_name = _('Key Name'), help_text = _('Meta Key Name'), db_column='NAME')
	keyType = models.ForeignKey(Param, limit_choices_to={'mode': CoreK.PARAM_META_TYPE}, db_column='ID_SITE_PARAMETER',
			verbose_name=_('Key META Type'), help_text=_('Key META Type') )
	def __unicode__(self):
		return self.name
	class Meta:
		db_table = 'SITE_META_KEY'
		ordering = ['name']
		verbose_name = _('Meta Key')
		verbose_name_plural = _('Meta Keys')

class TagMode ( BaseModel ):
	"""
	
	Tag Mode Model. Tags can have types (modes) in order to provide tag types
	
	**Attributes**
	
	* ``mode``:CharField(30) : Tag mode (type)
	* ``isPublic``:BooleanField : is tag public or private?
	
	"""
	id = models.AutoField(primary_key=True, db_column='ID_SITE_TAG_MODE')
	mode = models.CharField(max_length=30, db_column='MODE',
			verbose_name = _('Mode'), help_text = _('Tag mode'))
	isPublic = models.BooleanField(default=True, db_column='IS_PUBLIC',
			verbose_name = _('Public'), help_text = _('Is tag mode public?'))
	def __unicode__(self):
		return self.mode
	class Meta:
		db_table = 'SITE_TAG_MODE'
		verbose_name = _('Tag Mode')
		verbose_name_plural = _("Tag Modes")

class Tag ( BaseModel ):
	"""
	
	Tag Model. Tags have name, tag type (mode), popularity and weather or not they are public. Popularity is integer. Can
	be rating stars type of popularity, ranking alorithms, etc...
	
	**Attributes**
	
	* ``name``:CharField(30) : Tag name
	* ``popularity``IntegerField : Tag popularity
	* ``isPublic``:BooleanField : is tag public or private?
	* ``url`` : Built by services / business to provide an url for tags. tag.url = myUrl
	
	"""

	id = models.AutoField(primary_key=True, db_column='ID_SITE_TAG')
	name = models.CharField(max_length=30, db_column='NAME',
			verbose_name = _('Name'), help_text = _('Tag name'))
	mode = models.ForeignKey(TagMode, related_name='Tag_Mode', db_column='ID_MODE',
			verbose_name = _('Mode'), help_text = _('Tag mode'))
	popularity = models.IntegerField(default=1, null=True, blank=True, db_column='POPULARITY',
			verbose_name = _('Popularity'), help_text = _('Popularity'))
	isPublic = models.BooleanField(default=True, db_column='IS_PUBLIC',
			verbose_name = _('Public'), help_text = _('Is tag public?'))
	url = ''
	def __unicode__(self):
		return self.name
	def getText(self):
		return self.name
	def related_label(self):
		return u"%s" % (self.name)
	def get_url(self):
		return self.__url
	def set_url(self, value):
		self.__url = value
	def del_url(self):
		del self.__url
	class Meta:
		db_table = 'SITE_TAG'
		verbose_name = _('Tag')
		verbose_name_plural = _("Tags")
		ordering = ['-popularity']
	url = property(get_url, set_url, del_url, "Url for tag")

class UserChannel ( BaseModel ):
	"""
	
	Every user can have one or more social channels. In case social channels are disabled, only one registry will
	exist for each user.
	
	User channels allow different social activities for users, for example data for private channel, friends channel,
	professional channel, company A channel, company B channel, etc...
	
	In case you need to provide your app model channel functionality, create a foreign key to UserChannel instead of
	django User model.
	
	**Attributes**
	
	* ``title``CharField(20) : Title for the user channel
	* ``name``:CharField(20) : Name. Default USER name. When creating users, USER channel is created. Later on, more channels can
	be added
	
	**Relationships**
	
	* ``user`` -> Foreign key to User
	* ``groups`` <-> Many to many relationship with GroupChannel
	* ``tag`` -> Foreign key relationship with Tag 
	
	"""
	
	id = models.AutoField(primary_key=True, db_column='ID_SITE_USER')
	user = models.ForeignKey(User, db_column='ID_USER',
				verbose_name = _('User'), help_text = _('User'))
	groups = models.ManyToManyField('site.GroupChannel', related_name='userchannel_groups', through='UserChannelGroups',  
				verbose_name = _('Groups'), help_text = _('Groups'))
	title = models.CharField(max_length=20, db_column='TITLE',
				verbose_name = _('Channel Title'), help_text=_('Title for the social channel'))
	name = models.CharField(max_length=20, default=K.USER, db_column='NAME',
				verbose_name = _('Social Channel Name'), help_text = _('Name for the social channel'))
	tag = models.ForeignKey(Tag, db_column='ID_TAG',
				verbose_name=_('Tag'), help_text=_('User channel tag'))
	def __unicode__(self):
		return str(self.user.username) + '-' + str(self.name)
	def getGroupById(self, groupId):
		"""Get group by id"""
		groups = self.groups.filter(pk=groupId)
		if len(groups) != 0:
			value = groups[0]
		else:
			value = None
		return value
	def getFullName(self):
		"""Get full name: firstName lastName"""
		name = self.user.get_full_name()
		return name
	class Meta:
		db_table = 'SITE_USER'
		verbose_name = 'User'
		verbose_name_plural = "Users"
		unique_together = ("user", "name")

class Category ( BaseModel ):
	
	"""
	
	Category model
	
	**Attributes**
	
	* ``name``:CharField(55) : Category name.
	* ``slug``:CharField(200) : Category slug to build urls.
	* ``description``:CharField(255) : Category description.
	* ``image``:FileBrowserField(200) : Image path with django-filebrowser. Native version. Additional versions can be created
	with filebrowser version creating features.
	* ``type``:CharField(20) : Category type.
	* ``isPublished``:BooleanField : Category has been published and no longer in draft mode.
	* ``isPublic``:BooleanField : Category is private or public.
	*  ``popularity``:IntegerField : Category popularity
	* ``menuOrder``:PositiveSmallIntegerField : Menu order. Used by menu systems to display categories in ordered lists.
	* ``url``:String : Url built from layers using slugs and parent slugs to provide hierarchable urls.
	* ``imgThumbnail``:String : Image version for showing in lists.
	* ``count``:int : Number of elements in category. Using aggregation features of django, this value is created by layers and shown
	in this model entity.
	
	**Relationships**
	
	* ``parent`` -> self : Foreign key to self for hierarchy
	
	"""

	id = models.AutoField(primary_key=True, db_column='ID_SITE_CATEGORY')
	user = models.ForeignKey(UserChannel, related_name='category_owner',  
		    verbose_name = _('User'), help_text = _('User'), db_column='ID_USER_CHANNEL')
	relationship = models.CharField(max_length=20, choices=Choices.ACCESS_RELATIONSHIP, default=Choices.ACCESS_RELATIONSHIP_USER, 
				db_column='RELATIONSHIP',
				verbose_name=_('Relationship'), help_text=_('Access relationship: User, Owner, Admin and Manager'))
	name = models.CharField(max_length=55,
		verbose_name = _('name'), help_text = _('Category name'), db_column='NAME')
	slug = models.SlugField(max_length=200,
		verbose_name = _('Slug'), help_text = _('Slug'), db_column='SLUG')
	description = models.CharField(max_length=255, null=True, blank=True,
		verbose_name = _('Description'), help_text = _('Description'), db_column='DESCRIPTION')
	parent = models.ForeignKey('self', null=True, blank=True, related_name='category_parent', 
		    verbose_name = _('Parent'), help_text = _('Parent'), db_column='ID_PARENT')
	image = FileBrowseField(max_length=200, format='image', null=True, blank=True, 
		    verbose_name = _('Image'), help_text = _('Category image. Will be shown in listing categories or links to category'), 
		    db_column='IMAGE')
	type = models.CharField(max_length=20, choices=Choices.CATEGORY_TYPE, default=Choices.CATEGORY_TYPE_DEFAULT,
		verbose_name = _('Type'), help_text = _('Category Type: Blog or site'), db_column='TYPE')
	isPublished = models.BooleanField(default=False,
		verbose_name = _('Is Published?'), help_text = _('Is Published?'), db_column='IS_PUBLISHED')
	isPublic = models.BooleanField(default=True, db_column='IS_PUBLIC',
			verbose_name = _('Public'), help_text = _('Is category public?'))
	popularity = models.IntegerField(default=1, null=True, blank=True, db_column='POPULARITY',
			verbose_name = _('Popularity'), help_text = _('Popularity'))
	menuOrder = models.PositiveSmallIntegerField(default=1,
		    verbose_name = _('Menu Order'), help_text = _('Menu Order'), db_column='MENU_ORDER')

	url = ''
	imgThumbnail = ''
	count = 0
	
	def __unicode__(self):
		return self.name
	def related_label(self):
		return u"%s" % (self.name)	
	def get_url(self):
		return self.__url
	def get_img_thumbnail(self):
		return self.__imgThumbnail
	def set_url(self, value):
		self.__url = value
	def set_img_thumbnail(self, value):
		self.__imgThumbnail = value
	def del_url(self):
		del self.__url
	def del_img_thumbnail(self):
		del self.__imgThumbnail
	def get_count(self):
		return self.__count
	def set_count(self, value):
		self.__count = value
	def del_count(self):
		del self.__count
	
	class Meta:
		db_table = 'SITE_CATEGORY'
		verbose_name = _('Category')
		verbose_name_plural = _('Categories')

	url = property(get_url, set_url, del_url, "url for category")
	imgThumbnail = property(get_img_thumbnail, set_img_thumbnail, del_img_thumbnail, "thumb image for category")
	count = property(get_count, set_count, del_count, "number of items in category")

class SocialNetworkUser ( BaseModel ):
	
	"""
	
	Social Networks for users
	
	**Attributes**
	
	* ``socialNetwork``:CharField(20) : Social network.
	* ``socialId``:IntegerField : Social user id for network.
	* ``token``:CharField(255) : Token for user in network.
	* ``tokenSecret``:CharField(255) : Token secret for user in network.
	
	**Relationships**
	
	* ``user`` -> User : Foreign key to User mode.
	
	"""
	
	id = models.AutoField(primary_key=True, db_column='ID_SITE_SOCIAL_USER')
	user = models.ForeignKey(User, db_column='ID_USER',
				verbose_name = _('User'), help_text = _('User'))
	socialNetwork = models.ForeignKey('core.CoreParam', limit_choices_to={'mode__lte': K}, db_column='ID_CORE_PARAMETER',
				verbose_name = _('Social Network'), help_text = _('Social network'))
	socialId = models.IntegerField(db_column='SOCIAL_ID', verbose_name = _('Social ID'), help_text = _('Social network user id'))
	token = models.CharField(max_length=255, db_column='TOKEN',
				verbose_name = _('Token'), help_text = _('Token'))
	tokenSecret = models.CharField(max_length=255, null=True, blank=True, db_column='TOKEN_SECRET',
				verbose_name = _('Token Secret'), help_text = _('Token secret'))
	def __unicode__(self):
		return str(self.getName()) + ' ' + str(self.user)
	def getName(self):
		return self.socialNetwork
	class Meta:
		db_table = 'SITE_SOCIAL_USER'
		unique_together = ("user", "socialNetwork")
		verbose_name = 'Social Networks for User'
		verbose_name_plural = "Social Networks for Users"

class Settings ( BaseModel ):
	"""
	Settings model
	
	**Attributes**
	
	* ``value``:TextField : Settings value.
	* ``description``:CharField(255) : Setting description.
	* ``mustAutoload``:BooleanField : Has to load settings on cache?
	
	**Relationships**
	
	* ``name`` -> MetaKey : Foreign key to MetaKey model.
	
	"""
	
	name = models.ForeignKey(MetaKey, db_column='ID_META',
				verbose_name=_('Name'), help_text=_('Settings name'))
	value = models.TextField(verbose_name = _('Value'), help_text = _('Settings value'), db_column='VALUE')
	description = models.CharField(max_length=255,
	        verbose_name = _('Description'), help_text = _('Description'), db_column='DESCRIPTION')
	mustAutoload = models.BooleanField(default=False,
	        verbose_name = _('Must Autoload?'), help_text = _('Must Autoload?'), db_column='MUST_AUTOLOAD')
	def __unicode__(self):
		return str(self.name)
	class Meta:
		db_table = 'SITE_SETTINGS'
		verbose_name = _('Settings')
		verbose_name_plural = _('Settings')

class UserMeta ( BaseModel ):
	"""
	
	User meta values for user in site. This has meta keys for ximpia site. You can add your user meta keys here for any values you need
	for your users like file quotas, session generated data you need to save into database, etc...
	
	**Attributes**
	
	* ``value``:TextField : User meta value.
	
	**Relationships**
	
	* ``user`` -> User . Foreign key relationship with User model.
	* ``meta`` -> MetaKey . Foreign key relationship with MetaKey.
	
	"""
	
	id = models.AutoField(primary_key=True, db_column='ID_SITE_USER_PROFILE')
	user = models.ForeignKey(User, db_column='ID_USER',
				verbose_name = _('User'), help_text = _('User'))
	meta = models.ForeignKey(MetaKey, db_column='ID_META',
				verbose_name=_('Meta Key'), help_text=_('Meta Key'))
	value = models.TextField(db_column='VALUE', verbose_name = _('Value'), help_text = _('Value'))
	
	class Meta:
		db_table = 'SITE_USER_META'
		verbose_name = 'User Meta Keys'
		verbose_name_plural = "Users Meta Keys"

class UserProfile ( BaseModel ):
	"""
	
	Basic user profile for site users
	
	**Attributes**
	
	* ``image``:FileBrowserField(200) : User image profile.
	
	**Relationships**
	
	* ``user`` -> User. Foreign key with User model.
	* ``status`` -> Param . Foreign key with SITE_PARAMETER for valud user statuses: mode='USER_STATUS'.
	
	"""
	
	id = models.AutoField(primary_key=True, db_column='ID_SITE_USER_PROFILE')
	user = models.ForeignKey(User, db_column='ID_USER',
				verbose_name = _('User'), help_text = _('User'))
	image = FileBrowseField(max_length=200, format='image', null=True, blank=True, 
		    verbose_name = _('Image'), help_text = _('User profile image'), 
		    db_column='IMAGE')
	status = models.ForeignKey(Param, limit_choices_to={'mode': K.PARAM_USER_STATUS}, db_column='ID_SITE_PARAMETER',
			verbose_name=_('Status'), help_text=_('User Status') )
	
	class Meta:
		db_table = 'SITE_USER_META'
		verbose_name = 'User Meta Keys'
		verbose_name_plural = "Users Meta Keys"

class GroupChannel ( BaseModel ):
	"""
	
	Group channels. This model has been designed to allow discussion groups, definition of departments inside organizations,
	work groups inside departments, user profiles, etc... It is a pretty flexible design to accomodate your needs. Groups can
	be tagged and categorized to provide group types: profiles, departments, work groups...
	
	**Attributes**
	
	* ``groupNameId``:CharField(20)
	* ``isPublic``:BooleanField
	
	**Relationships**
	
	* ``group`` -> Group
	* ``parent`` -> GroupChannel
	* ``accessGroups`` <-> GroupChannelAccess
	* ``tags`` <-> GroupChannelTags
	* ``category`` -> Category	
	
	"""
	
	id = models.AutoField(primary_key=True, db_column='ID_SITE_GROUP')
	group = models.ForeignKey(Group, unique=True, db_column='ID_GROUP',
				verbose_name = _('Group'), help_text = _('Group'))
	parent = models.ForeignKey('self', null=True, blank=True, related_name='groupchannel_parent', 
		    verbose_name = _('Parent'), help_text = _('Parent'), db_column='ID_PARENT')
	groupNameId = models.CharField(max_length=20, null=True, blank=True, db_column='GROUP_NAME_ID',
				verbose_name = _('Group Name Id'), help_text = _('Identification for group'))
	isPublic = models.BooleanField(default=True, db_column='IS_PUBLIC',
				verbose_name = _('Public'), help_text = _('Group is public'))
	accessGroups = models.ManyToManyField('self', through='site.GroupChannelAccess', related_name='groupchannel_access', 
				verbose_name = _('Access Groups'), help_text = _('Profiles that have access to this group'))
	tags = models.ManyToManyField(Tag, through='site.GroupChannelTags', null=True, blank=True, related_name='groupchannel_tags',
				verbose_name = _('Tags'), help_text = _('Tags'))
	category = models.ForeignKey(Category, null=True, blank=True, db_column='ID_CATEGORY',
				verbose_name=_('Category'), help_text=_('Category for group'))
	
	def __unicode__(self):
		if self.account != None:
			return '%s %s' % (self.account, self.group)
		else:
			return self.group
	class Meta:
		db_table = 'SITE_GROUP'
		verbose_name = 'Group Channel'
		verbose_name_plural = "Group Channels"

class GroupChannelAccess ( BaseModel ):
	"""
	
	Access to group channels : User profiles.
	
	**Relationships**
	
	* ``groupChannel`` -> GroupChannel
	
	"""
	
	id = models.AutoField(primary_key=True, db_column='ID_SITE_GROUP_CHANNEL_ACCESS')
	groupChannel = models.ForeignKey(GroupChannel, db_column='ID_GROUP_CHANNEL',
					verbose_name=_('Group'), help_text=_('Group Channel'))
	
	def __unicode__(self):
		return '%s %s' % (self.groupChannel, self.userChannel)
	
	class Meta:
		db_table = 'SITE_GROUP_CHANNEL_ACCESS'
		verbose_name = 'Group Channel Profiles'
		verbose_name_plural = "Group Channel Profiles"

class UserChannelGroups ( BaseModel ):
	"""
	
	User related to channel and their role (relationship). Relationships can be user, owner, admin and manager.
	
	**Attributes**
	
	* ``relationship``:CharField(20) : Choices.ACCESS_RELATIONSHIP : user, admin, manager, owner
	
	**Relationships**
	
	* ``groupChannel`` -> GroupChannel
	* ``userChannel`` -> UserChannel
	
	"""
	
	id = models.AutoField(primary_key=True, db_column='ID_SITE_GROUP_CHANNEL_USERS')
	groupChannel = models.ForeignKey(GroupChannel, db_column='ID_GROUP_CHANNEL',
					verbose_name=_('Group'), help_text=_('Group Channel'))
	userChannel = models.ForeignKey(UserChannel, db_column='ID_USER_CHANNEL',
					verbose_name=_('User'), help_text=_('User channel'))
	relationship = models.CharField(max_length=20, choices=Choices.ACCESS_RELATIONSHIP, default=Choices.ACCESS_RELATIONSHIP_USER, 
				db_column='RELATIONSHIP',
				verbose_name=_('Relationship'), help_text=_('Access relationship: User, Owner, Admin and Manager'))
	
	def __unicode__(self):
		return '%s %s' % (self.groupChannel, self.userChannel)
	
	class Meta:
		db_table = 'SITE_GROUP_CHANNEL_USERS'
		verbose_name = 'Group Channel Users'
		verbose_name_plural = "Group Channel Users"

class GroupChannelTags ( BaseModel ):
	"""
	
	Tags for group channels
	
	**Relationships**
	
	* ``groupChannel`` -> GroupChannel
	* ``tag`` -> Tag
	
	"""
	
	id = models.AutoField(primary_key=True, db_column='ID_SITE_GROUP_CHANNEL_TAGS')
	groupChannel = models.ForeignKey(GroupChannel, db_column='ID_GROUP_CHANNEL',
					verbose_name=_('Group'), help_text=_('Group Channel'))
	tag = models.ForeignKey(Tag, db_column='ID_TAG',
					verbose_name=_('Tag'), help_text=_('Tag'))
	
	def __unicode__(self):
		return '%s - %s' % (self.groupChannel, self.tag)
	
	class Meta:
		db_table = 'SITE_GROUP_CHANNEL_TAGS'
		verbose_name = 'Group Channel Tags'
		verbose_name_plural = "Group Channel Tags"

class XmlMessage ( BaseModel ):
	
	"""
	
	XML Messages
	
	"""
	
	# TODO: This table will go to settings, having name as name
	# @deprecated: Move table data to SITE_SETTINGS
	id = models.AutoField(primary_key=True, db_column='ID_SITE_XML_MESSAGE')
	name = models.CharField(max_length=255, db_column='NAME',
			verbose_name = _('Name'), help_text = _('Code name of XML'))
	lang = models.CharField(max_length=2, choices=Choices.LANG, default=Choices.LANG_ENGLISH, db_column='LANG',
			verbose_name = _('Language'), help_text = _('Language for xml'))
	body = models.TextField(db_column='BODY', verbose_name = _('Xml Content'), help_text = _('Xml content'))
	def __unicode__(self):
		return str(self.name)
	class Meta:
		db_table = 'SITE_XML_MESSAGE'
		verbose_name = _('Xml Message')
		verbose_name_plural = _('Xml Messages')

class SignupData ( BaseModel ):
	
	"""	
	SignUp Data. When users signup and further validation is required, signup data is recorded into this table. When they are validated 
	(email, etc...) an user and userchannel is created.
	
	**Attributes**
	
	* ``user``:CharField(30) : User id.
	* ``activationCode``:POsitiveSmallIntegerField : Activation code used in validation message (email).
	* ``data``:TextField : User data.
	
	"""
	
	id = models.AutoField(primary_key=True, db_column='ID_SITE_SIGNUP_DATA')
	user = models.CharField(max_length=30, unique=True, db_column='USER',
			verbose_name = _('User'), help_text = _('User'))
	activationCode = models.PositiveSmallIntegerField(db_column='ACTIVATION_CODE', 
			verbose_name = _('Activation Code'), help_text = _('Activation code'))
	data = models.TextField(db_column='DATA', verbose_name = _('Data'), help_text = _('Data'))
	def __unicode__(self):
		return str(self.user)
	class Meta:
		db_table = 'SITE_SIGNUP_DATA'
		verbose_name = _('Signup Data')
		verbose_name_plural = _('Signup Data')

class Address ( BaseModel ):
	"""
	
	Address model. It can store only cities and countries or sholw addresses with geo spatial information.
	
	**Attributes**
	
	* ``street`` :CharField(50) : Street address.
	* ``city``:CharField(20) : City.
	* ``region``:CharField(20) : Region.
	* ``zipCode``:CharField(20) : Zip code.
	* ``country``:CharField(2) : Country from Choices.COUNTRY
	* ``long``:DecimalField(18,12) : Longitude for address (Geo Data)
	* ``lat``:DecimalField(18,12) : Latitude for address (Geo Data)
	
	"""
	id = models.AutoField(primary_key=True, db_column='ID_SITE_ADDRESS')
	street = models.CharField(max_length=50, null=True, blank=True, db_column='STREET',
			verbose_name = _('Street'), help_text = _('Street'))
	city = models.CharField(max_length=20, db_column='CITY',
			verbose_name = _('City'), help_text = _('City'))
	region = models.CharField(max_length=20, null=True, blank=True, db_column='REGION',
			verbose_name = _('Region'), help_text = _('Region'))
	zipCode = models.CharField(max_length=20, null=True, blank=True, db_column='ZIP_CODE',
			verbose_name = _('Zip Code'), help_text = _('Zip Code'))
	country = models.CharField(max_length=2, choices=Choices.COUNTRY, db_column='COUNTRY',
			verbose_name = _('Country'), help_text = _('Country'))
	long = models.DecimalField(max_digits=18, decimal_places=12, null=True, blank=True,
			verbose_name=_('Geo Longitude'), help_text=_('Geo longitude'))
	lat = models.DecimalField(max_digits=18, decimal_places=12, null=True, blank=True,
			verbose_name=_('Geo Latitude'), help_text=_('Geo latitude'))
	def __unicode__(self):
		return '%s %s' % (self.street, self.city)
	class Meta:
		db_table = 'SITE_ADDRESS'
		verbose_name = _('Address')
		verbose_name_plural = _('Addresses')

class Invitation ( BaseModel ):
	"""
	
	Invitation Model
	
	**Attributes**
	
	* ``invitationCode``:CharField(10) : Invitation code.
	* ``email``:EmailField : Invitation sent to this email address.
	* ``status``:CharField(10) : Invitation status from Choices.INVITATION_STATUS.
	* ``number``:PositiveSmallIntegerField : Number of invitations (either sent or used, depending on logic)
	* ``message``:TextField : Invitation message.
	
	**Relationships**
	
	* ``fromUser`` -> User : Foreign key for origin user which send invitation. 
	
	"""
	id = models.AutoField(primary_key=True, db_column='ID_SITE_INVITATION')
	fromUser = models.ForeignKey(User, db_column='ID_USER',
				verbose_name = _('From User'), help_text = _('Invitation from user'))
	invitationCode = models.CharField(max_length=10, unique=True, db_column='INVITATION_CODE',
				verbose_name = _('Inivitation Code'), help_text = _('Invitation Code'))
	email = models.EmailField(unique=True, db_column='EMAIL', verbose_name = _('Email'), help_text = _('Email attached to invitation'))
	status = models.CharField(max_length=10, choices=Choices.INVITATION_STATUS, default=K.PENDING, db_column='STATUS',
				verbose_name = _('Status'), help_text = _('Invitation status : pending, used.'))
	number = models.PositiveSmallIntegerField(default=1, db_column='NUMBER',
				verbose_name = _('Number'), help_text = _('Invitation Number'))
	message = models.TextField(null=True, blank=True, db_column='MESSAGE',
				verbose_name = _('Message'), help_text = _('Message'))
	def __unicode__(self):
		return '%s %s' % (self.fromUser, self.invitationCode)
	class Meta:
		db_table = 'SITE_INVITATION'
		verbose_name = _('Invitation')
		verbose_name_plural = _('Invitations')
