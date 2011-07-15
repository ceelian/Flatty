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


class BaseFlattyType(object):
	"""
	This class is the base Class for all special flatty schema types.
	These are :class:`TypedList` and :class:`TypedDict`
	"""

	
	@classmethod
	def set_type(cls, ftype):
		"""sets the type for the inherited flatty schema class
	
		Args:
			ftype: the type/class of the instance objects in the schema
			
		Returns:
			a class object with the class variable `ftype` set, used to 
			determine the instance type during unflattening"""
		cls.ftype = ftype
		return cls	

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
	
	def _to_flat(self):
		flat_list = []
		for item in self:
			flat_list.append(flatit(item))
		return flat_list
	
	@classmethod
	def _to_obj(cls, flat_dict):
		obj = cls()
		for item in flat_dict:
			obj.append(unflatit(cls.ftype, item))
		return obj
	
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
	
	def _to_flat(self):
		flat_dict = {}
		for k,v in self.items():
			flat_dict[k] = flatit(v)
		return flat_dict
	
	@classmethod
	def _to_obj(cls, flat_dict):
		obj = cls()
		for k,v in flat_dict.items():
			obj[k] = unflatit(cls.ftype, v)
		return obj
	
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
	def to_flat(self, obj):
		"""need to be implemented to convert a python object to a primitive 
	
		Args:
			obj: the src obj which needs to be converted here
			
		Returns:
			a converted primitive object"""
		raise NotImplementedError()
	
	def to_obj(self, val):
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
	def to_flat(cls, obj):
		if obj == None:
			return None
		return obj.isoformat()
	@classmethod
	def to_obj(cls, val):
		if val == None:
			return None
		return datetime.datetime.strptime(str(val), "%Y-%m-%d").date()
			
class DateTimeConverter(Converter):
	"""
	Converter for datetime.datetime
	
	"""
	
	@classmethod
	def to_flat(cls, obj):
		if obj == None:
			return None
		return obj.isoformat()
	@classmethod
	def to_obj(cls, val):
		if val == None:
			return None
		return datetime.datetime.strptime(str(val), "%Y-%m-%dT%H:%M:%S.%f")

class TimeConverter(Converter):
	"""
	Converter for datetime.time
	
	"""
	
	@classmethod
	def to_flat(cls, obj):
		if obj == None:
			return None
		return obj.strftime("%H:%M:%S.%f")
	@classmethod
	def to_obj(cls, val):
		if val == None:
			return None
		return datetime.datetime.strptime(str(val), "%H:%M:%S.%f").time()

class ConvertManager(object):
	"""
	Class for managing the converters
	
	"""
	
	_convert_dict = {
					datetime.date:DateConverter,
					datetime.datetime:DateTimeConverter,
					datetime.time:TimeConverter,
					}
	
	@classmethod
	def to_flat(cls, val_type, obj):
		"""calls the right converter and converts to a flat type
	
		Args:
			val_type: the type of the object
			
			obj: the object which should be converted
			
		Returns:
			a converted primitive object"""
		if val_type not in cls._convert_dict:
			return obj
		else:
			return cls._convert_dict[val_type].to_flat(obj)
	
	@classmethod
	def to_obj(cls, val_type, val):
		"""calls the right converter and converts the flat val to a schema
		object
	
		Args:
			val_type: the type to which we want to convert
			
			val: the flattened data which needs to be converted here
			
		Returns:
			a converted high level schema object"""
		if val_type not in cls._convert_dict:
			return val
		else:
			return cls._convert_dict[val_type].to_obj(val)
	
	@classmethod
	def set_converter(cls, conv_type, converter):
		"""sets a converter object for a given `conv_type`
	
		Args:
			conv_type: the type for which the converter is responsible
				
			converter: a subclass of the :class:`Converter` class
		"""
		if inspect.isclass(converter) and \
			issubclass(converter, Converter):
			cls._convert_dict[conv_type] = converter
		else:
			raise TypeError('Subclass of Converter expected')
	@classmethod
	
	def del_converter(cls, conv_type):
		"""deletes the converter object for a given `conv_type`"""
		if conv_type in cls._convert_dict:
			del cls._convert_dict[conv_type]
	
def flatit(obj):
	"""one way to flatten the `obj`
	
		Args:
			obj: a :class:`Schema` instance which will be flatted
	
		Returns:
			a dict where the obj is flattened to primitive types"""
			
	flat_dict = {}
	for attr_name in dir(obj.__class__):
		attr_value = getattr(obj, attr_name)
		attr_type = getattr(obj.__class__, attr_name)
		if not attr_name.startswith('__') and not inspect.ismethod(attr_value):
			
			#if attr is of type TypedList or TypedDict
			if isinstance(attr_value, BaseFlattyType): 
				_check_type(attr_value, attr_type)
				flat_dict[attr_name] = attr_value._to_flat()
			
			#if plain dict or lists were used during construction then decorate
			# with the TypedDict/TypedList Classes
			elif inspect.isclass(getattr(obj.__class__, attr_name)) and \
				issubclass(getattr(obj.__class__, attr_name), BaseFlattyType):
				cls_attr_val = getattr(obj.__class__,attr_name)
				#if we don't have a instance yet set it None 
				if cls_attr_val == attr_value:
					flat_dict[attr_name] = None
				else:
					deco_attr_val = cls_attr_val(attr_value)
					_check_type(deco_attr_val, attr_type)
					flat_dict[attr_name] = deco_attr_val._to_flat()	
			
			# if it is a schema
			elif isinstance(attr_value, Schema):
				_check_type(attr_value, attr_type)
				flat_dict[attr_name] = flatit(attr_value)
			
			elif inspect.isclass(attr_value):
				flat_dict[attr_name] = None
			
			#if it is a primitive attribute
			else:
				_check_type(attr_value, attr_type)
				#get the type of default instances in schema definitions
				if inspect.isclass(attr_type) == False:
					attr_type = type(attr_type)
				attr_value = ConvertManager.to_flat(attr_type, attr_value)
				flat_dict[attr_name] = attr_value
			
	return flat_dict
	
def unflatit(cls, flat_dict):
	"""one way to unflatten and load the data back in the `cls`
	
		Args:
			flat_dict: a flat dict which will be loaded into an instance of
				the `cls`
			cls: the class from which the instance is builded where the 
				data is merged
			
		Returns:
			an instance of type `cls`"""
	#instantiate new object
	cls_obj = cls()
	#iterate all attributes
	for attr_name in dir(cls):
		attr_value = getattr(cls, attr_name)
		if not attr_name.startswith('__') and not inspect.ismethod(attr_value):
			if inspect.isclass(attr_value) and \
				issubclass(attr_value, BaseFlattyType):
				#convert flatty type to object
				if flat_dict[attr_name] == None:
					setattr(cls_obj,attr_name, None)
				else:
					deco_obj = attr_value._to_obj(flat_dict[attr_name])
					setattr(cls_obj,attr_name,deco_obj)
			elif inspect.isclass(attr_value) and issubclass(attr_value, Schema):
				#cascade unflatit when we get a schema attr
				setattr(cls_obj, attr_name, 
					unflatit(attr_value, flat_dict[attr_name]))
			else:
				#set attr the value of the flat_dict if exists
				flat_val = None
				if attr_name in flat_dict:
					flat_val = flat_dict[attr_name]
					#get the type of default instances in schema definitions
					if inspect.isclass(attr_value) == False:
						attr_value = type(attr_value)
					conv_attr_value = ConvertManager.to_obj(attr_value, flat_val)
					_check_type(conv_attr_value, attr_value)
				
				setattr(cls_obj,attr_name,conv_attr_value)
	return cls_obj