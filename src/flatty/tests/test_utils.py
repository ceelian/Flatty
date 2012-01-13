
import types
allowed_types = (types.NoneType,
 types.BooleanType, 
 types.IntType,
 types.LongType,
 types.FloatType,
 types.StringType,
 types.UnicodeType,
 types.ListType,
 types.DictType,
 types.NoneType)

def is_plain_dict(obj):
	if isinstance(obj, allowed_types):
		if isinstance(obj, types.DictType):
			for v in obj.values():
				if not is_plain_dict(v):
					return False
				
		if isinstance(obj, types.ListType):
			for v in obj:
				if not is_plain_dict(v):
					return False
		return True
	else:
		return False