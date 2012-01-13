"""
This module provides the base layer for all generic flattening schemas.
With this classes - if not yet exists as a flatty module - 
you can easily write a module to support flatty schemas with your favorite
marshaller/unmarshaller. As an example look at the other modules eg. flatty.couchdb 

=======
Classes
=======
"""
import inspect
import datetime
import types


class MetaBaseFlattyType(type):
	def __eq__(self, other):
		""" We need to overwrite this since the dynamically generated classes
		with ftype don't return equal when compared unlass compared only by names
		"""
		if hasattr(self, '__name__') and hasattr(other, '__name__') and \
			self.__name__ == other.__name__:
			return True
		else:
			return False
		
	def __instancecheck__(self, inst):
		""" We also need to overwrite this because of the failing comparrission
		due to dynamic class generation
		"""
		candidates = [type(inst), inst.__class__] 
		issubclasslist = []
		for c in candidates:
			issubclasslist.append(self.__subclasscheck__(c))
		return any(issubclasslist)
	
	def __subclasscheck__(cls, sub):
		"""Implement issubclass(sub, cls)."""
		candidates = cls.__dict__.get("__subclass__", []) or [cls]
		str_candidates = []
		for c in candidates:
			str_candidates.append(str(c))
		
		str_c = []
		for c in sub.mro():
			str_c.append(str(c))
		
		intersect = set(str_c).intersection( set(str_candidates) )
		if len(intersect) > 0: return True
		
		 

class BaseFlattyType(object):
	"""
	This class is the base Class for all special flatty schema types.
	These are :class:`TypedList` and :class:`TypedDict`
	"""
	ftype=None
	__metaclass__ = MetaBaseFlattyType
	
	
	
	@classmethod
	def set_type(cls, ftype):
		"""sets the type for the inherited flatty schema class
	
		Args:
			ftype: the type/class of the instance objects in the schema
			
		Returns:
			a class object with the class variable `ftype` set, used to 
			determine the instance type during unflattening"""
			
		# class must be generated dynamically otherwise ftype is set on
		# all classes which caused Bug #2
		new_cls = type(cls.__name__, cls.__bases__, dict(ftype=ftype, set_type=cls.set_type))
		return new_cls	

class TypedList(BaseFlattyType, list):
	"""
	This class is used for typed lists. During flattening and unflattening
	the types are checked and restored.
	
		>>> import flatty
		>>> 
		>>> 
		>>> class Bar(flatty.Schema):
		...	 a_num = int
		...	 a_str = str
		...	 a_thing = None  
		... 
		>>> class Foo(flatty.Schema):
		...	 my_typed_list = flatty.TypedList.set_type(Bar)
		>>> 
		>>> 
		>>> my_bar = Bar(a_num=42, a_str='hello world', a_thing='whatever type here')
		>>> foo = Foo(my_typed_list=[my_bar,])
		>>> 
		>>> flatted = foo.flatit()
		>>> print flatted
		{'my_typed_list': [{'a_num': 42, 'a_str': 'hello world', 'a_thing': 'whatever type here'}]}
		>>> 
		>>> restored_obj = Foo.unflatit(flatted)
		>>> 
		>>> isinstance(restored_obj, Foo)
		True
		>>> isinstance(restored_obj.my_typed_list[0], Bar)
		True
	"""
	pass
	
class TypedDict(BaseFlattyType, dict):
	"""
	This class is used for typed dict. During flattening and unflattening
	the types are checked and restored.
	
	
		>>> import flatty
		>>> 
		>>> 
		>>> class Bar(flatty.Schema):
		...	 a_num = int
		...	 a_str = str
		...	 a_thing = None  
		... 
		>>> class Foo(flatty.Schema):
		...	 my_typed_dict = flatty.TypedDict.set_type(Bar)
		>>> 
		>>> 
		>>> my_bar = Bar(a_num=42, a_str='hello world', a_thing='whatever type here')
		>>> foo = Foo(my_typed_dict={'my_key':my_bar})
		>>> 
		>>> flatted = foo.flatit()
		>>> print flatted
		{'my_typed_dict': {'my_key': {'a_num': 42, 'a_str': 'hello world', 'a_thing': 'whatever type here'}}}
		>>> 
		>>> restored_obj = Foo.unflatit(flatted)
		>>> 
		>>> isinstance(restored_obj, Foo)
		True
		>>> isinstance(restored_obj.my_typed_dict['my_key'], Bar)
		True
	"""
	pass

class Schema(object):
	"""
	This class builds the base class for all schema classes.
	All schema classes must inherit from this class
	
		>>> import flatty
		>>> 
		>>> class Bar(flatty.Schema):
		...	 a_num = int
		...	 a_str = str
		...	 a_thing = None  
	
	"""
	def __init__(self, **kwargs):
		#to comfortably set attributes via kwargs in the __init__
		for name, value in kwargs.items():
			if not hasattr(self, name):
				raise AttributeError('Attribute not exists')
			setattr(self, name, value)
	
	def flatit(self):
		"""one way to flatten the instance of this class
			
		Returns:
			a dict where the instance is flattened to primitive types"""
		return flatit(self)
	
	@classmethod
	def unflatit(cls, flat_dict):
		"""one way to unflatten and load the data back in the schema objects
			
		Returns:
			the object"""
		
		return unflatit(cls, flat_dict)		
			
def _check_type(val, type):
	if type == None or val == None or type == types.NoneType:
		return
	if inspect.isclass(type) == False:
		type = type.__class__
	if not isinstance(val, type): 
		raise TypeError(str(val.__class__) + " != " + str(type))

class Converter(object):
	"""
	Base class for all Converters. New converters of custom types can be build
	by inherit from this class and implement the following two methods
	
	"""
	@classmethod
	def check_type(cls, attr_type, attr_value):
		"""should be implemented to check if the attr_type from the schema
		matches the real type of attr_value 
	
		Args:
			attr_type: type from schema
			attr_value: value/obj with unknown type
			
		Returns:
			Nothing if type of attr_value is ok, otherwise should raise
			a TypeError Exception"""
		pass
	
	
	@classmethod
	def to_flat(cls, obj_type, obj):
		"""need to be implemented to convert a python object to a primitive 
	
		Args:
			obj: the src obj which needs to be converted here
			
		Returns:
			a converted primitive object"""
		raise NotImplementedError()
	
	@classmethod
	def to_obj(cls, val_type, val):
		"""need to be implemented to convert a primitive to a python object 
	
		Args:
			val: the flattened data which needs to be converted here
			
		Returns:
			a converted high level schema object"""
		raise NotImplementedError()
	
class DateConverter(Converter):
	"""
	Converter for datetime.date
	
	"""
	
	@classmethod
	def to_flat(cls, obj_type, obj):
		if obj == None:
			return None
		return obj.isoformat()
	@classmethod
	def to_obj(cls, val_type, val):
		if val == None:
			return None
		return datetime.datetime.strptime(str(val), "%Y-%m-%d").date()
			
class DateTimeConverter(Converter):
	"""
	Converter for datetime.datetime
	
	"""
	
	@classmethod
	def to_flat(cls, obj_type, obj):
		if obj == None:
			return None
		return obj.isoformat()
	@classmethod
	def to_obj(cls, val_type, val):
		if val == None:
			return None
		return datetime.datetime.strptime(str(val), "%Y-%m-%dT%H:%M:%S.%f")

class TimeConverter(Converter):
	"""
	Converter for datetime.time
	
	"""
	
	@classmethod
	def to_flat(cls, obj_type, obj):
		if obj == None:
			return None
		return obj.strftime("%H:%M:%S.%f")
	@classmethod
	def to_obj(cls, val_type, val):
		if val == None:
			return None
		return datetime.datetime.strptime(str(val), "%H:%M:%S.%f").time()
	
class SchemaConverter(Converter):
	"""
	Convert basic schema classes
	
	"""
	@classmethod
	def check_type(cls, attr_type, attr_value):
		if not issubclass(type(attr_value), attr_type):
			raise TypeError(repr(type(attr_value)) + '!=' + repr(attr_type))
	
	@classmethod
	def to_flat(cls, obj_type, obj):
		flat_dict = {}
		for attr_name in dir(obj_type):
			attr_value = getattr(obj, attr_name)
			attr_type = getattr(obj_type, attr_name)
			if not attr_name.startswith('__') and not inspect.ismethod(attr_value):
				
				#set None if types are still present in the object
				# and these are types and not objects
				if attr_value == attr_type and inspect.isclass(attr_value):
					attr_value = None
					
				#get the type of default instances in schema definitions
				if inspect.isclass(attr_type) == False:
					attr_type = type(attr_type)
					
				check_type(attr_type, attr_value)
				attr_value = flatit(attr_value, attr_type)
					
				flat_dict[attr_name] = attr_value		
		return flat_dict
	
	@classmethod
	def to_obj(cls, val_type, val):
		#instantiate new object
		cls_obj = val_type()
		#iterate all attributes
		for attr_name in dir(val_type):
			attr_value = getattr(val_type, attr_name)
			if not attr_name.startswith('__') and not inspect.ismethod(attr_value):
				#set attr the value of the flat_dict if exists
				flat_val = None
				if attr_name in val:
					flat_val = val[attr_name]
					#get the type of default instances in schema definitions
					if inspect.isclass(attr_value) == False:
						attr_value = type(attr_value)
					conv_attr_value = unflatit(attr_value, flat_val)
					check_type(attr_value, conv_attr_value)
				
					setattr(cls_obj, attr_name, conv_attr_value)
		return cls_obj

class TypedListConverter(Converter):
	"""
	Convert TypedList classes
	
	"""
	
	@classmethod
	def check_type(cls, attr_type, attr_value):
		if not(issubclass(type(attr_value), attr_type) \
			 or issubclass(type(attr_value), list) \
			 or type(attr_value) == types.NoneType):
			raise TypeError(repr(type(attr_value)) + '!=' + repr(attr_type))
	
	
	@classmethod
	def to_flat(cls, obj_type, obj):
		#TODO: CHECK TYPE but we might need also an additional val_type here as
		# method argument. Especially for the SchemaConverter because
		# there you need to check if the obj is a subclass of type defined in
		# the schema
		check_type(obj_type, obj)
		if obj == None:
			return None
		flat_list = []
		for item in obj:
			check_type(obj_type.ftype, item)
			flat_list.append(flatit(item))
		return flat_list
	
	@classmethod
	def to_obj(cls, val_type, val):
		obj = val_type()
		if val == None:
			return None
		
		for item in val:
			obj.append(unflatit(val_type.ftype, item))
		return obj
	
	
class TypedDictConverter(Converter):
	"""
	Convert TypedList classes
	
	"""
	@classmethod
	def check_type(cls, attr_type, attr_value):
		if not(issubclass(type(attr_value), attr_type) \
			 or issubclass(type(attr_value), dict) \
			 or type(attr_value) == types.NoneType):
			raise TypeError(repr(type(attr_value)) + '!=' + repr(attr_type))
	
	
	@classmethod
	def to_flat(cls, obj_type, obj):
		check_type(obj_type, obj)
		if obj == None:
			return None
		flat_dict = {}
		for k, v in obj.items():
			check_type(obj_type.ftype, v)
			flat_dict[k] = flatit(v)
		return flat_dict
	
	@classmethod
	def to_obj(cls, val_type, val):
		if val == None:
			return None
		obj = val_type()
		for k, v in val.items():
			obj[k] = unflatit(val_type.ftype, v)
		return obj
	

class ConvertManager(object):
	"""
	Class for managing the converters
	
	"""
	
	_convert_dict = {
					datetime.date:{'conv':DateConverter, 'exact':True},
					datetime.datetime:{'conv':DateTimeConverter, 'exact':True},
					datetime.time:{'conv':TimeConverter, 'exact':True},
					Schema:{'conv':SchemaConverter, 'exact':False},
					TypedDict:{'conv':TypedDictConverter, 'exact':True},
					TypedList:{'conv':TypedListConverter, 'exact':True},
					}
	
	@classmethod
	def to_flat(cls, val_type, obj):
		"""calls the right converter and converts to a flat type
	
		Args:
			val_type: the type of the object
			
			obj: the object which should be converted
			
		Returns:
			a converted primitive object"""
		for type in cls._convert_dict:
			#String comparisson is okay here since we compare schema against
			#object types which can differ in the ftype class variable therefore
			#string compare is correct and direct type compare fails
			if str(val_type) == str(type):
				return cls._convert_dict[type]['conv'].to_flat(val_type, obj)
		
		for type in cls._convert_dict:
			if cls._convert_dict[type]['exact'] == False and issubclass(val_type, type):
				return cls._convert_dict[type]['conv'].to_flat(val_type, obj)
			
		return obj
	
	@classmethod
	def to_obj(cls, val_type, val):
		"""calls the right converter and converts the flat val to a schema
		object
	
		Args:
			val_type: the type to which we want to convert
			
			val: the flattened data which needs to be converted here
			
		Returns:
			a converted high level schema object"""
		
		for type in cls._convert_dict:
			#String comparisson is okay here since we compare schema against
			#object types which can differ in the ftype class variable therefore
			#string compare is correct and direct type compare fails
			if str(val_type) == str(type):
				return cls._convert_dict[type]['conv'].to_obj(val_type, val)
		
		for type in cls._convert_dict:
			if cls._convert_dict[type]['exact'] == False and issubclass(val_type, type):
				return cls._convert_dict[type]['conv'].to_obj(val_type, val)
			
		return val
	
	@classmethod
	def check_type(cls, attr_type, attr_value):
		"""checks the type of value and type
	
		Args:
			attr_type: the type which the attr_value should have
			
			attr_value: obj which we check against attr_type
			
		Returns:
			None if everything is ok, otherwise raise TypeError"""
		for type in cls._convert_dict:
			#String comparisson is okay here since we compare schema against
			#object types which can differ in the ftype class variable therefore
			#string compare is correct and direct type compare fails
			if str(attr_type) == str(type):
				cls._convert_dict[type]['conv'].check_type(attr_type, attr_value)
				return
			
		for type in cls._convert_dict:
			if cls._convert_dict[type]['exact'] == False and issubclass(attr_type, type):
				cls._convert_dict[type]['conv'].check_type(attr_type, attr_value)
				return
			
		_check_type(attr_value, attr_type)
	
	@classmethod
	def set_converter(cls, conv_type, converter, exact=True):
		"""sets a converter object for a given `conv_type`
	
		Args:
			conv_type: the type for which the converter is responsible
				
			converter: a subclass of the :class:`Converter` class
			
			exact: When True only matches converter if type of obj is
				the type of the converter. If exact=False then converter
				matches also if obj is just a subclass of the converter type.
				E.g the Schema Class is added to the converter with exact=False
				because Schema Classes are always inherited at least once.
				(default=True) 
		"""
		if inspect.isclass(converter) and \
			issubclass(converter, Converter):
			cls._convert_dict[conv_type] = {}
			cls._convert_dict[conv_type]['conv'] = converter
			cls._convert_dict[conv_type]['exact'] = exact
		else:
			raise TypeError('Subclass of Converter expected')
	@classmethod
	
	def del_converter(cls, conv_type):
		"""deletes the converter object for a given `conv_type`"""
		if conv_type in cls._convert_dict:
			del cls._convert_dict[conv_type]
	
def check_type(attr_type, attr_value):
	"""check the type of attr_value against attr_type
	
		Args:
			attr_type: a type
			attr_value: an object
	
		Returns:
			None in normal cases, if attr_type doesn't match type of
			attr_value, raise TypeError"""
	ConvertManager.check_type(attr_type, attr_value)
	
def flatit(obj, obj_type=None):
	"""one way to flatten the `obj`
	
		Args:
			obj: a :class:`Schema` instance which will be flatted
	
		Returns:
			a dict where the obj is flattened to primitive types"""
	if obj_type == None:
		obj_type = type(obj)
	return ConvertManager.to_flat(obj_type, obj)
	
def unflatit(cls, flat_dict):
	"""one way to unflatten and load the data back in the `cls`
	
		Args:
			flat_dict: a flat dict which will be loaded into an instance of
				the `cls`
			cls: the class from which the instance is builded where the 
				data is merged
			
		Returns:
			an instance of type `cls`"""
	return ConvertManager.to_obj(cls, flat_dict)
	
