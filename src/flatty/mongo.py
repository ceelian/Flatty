"""

=======
Classes
=======
"""
import flatty
from pymongo.objectid import ObjectId

class Document(flatty.Schema):
	"""
	This class is the base Class for all mongodb documents
	
	**IMPORTANT**:
		Due to the fact that mongodb always return strings as unicode we need
		to define string attributes of type basestring (which is the parent 
		class of str and unicode class). Otherwise flatty will
		raise a TypeError (<type 'str'> != <type 'unicode'>) 
	"""
	__collection__ = None
	__old_doc__ = None
	_id = ObjectId
	
	def store(self, db):
		"""stores the document in the mongodb.
		Only saves the document if it wasn't changed in the meantime otherwise
		*UpdateFailedError* Exception is raised
	
		Args:
			db: should must be a pymongo ''Database'' object
			
		Returns:
			returns *id*.  *id*  is the document id which stays the
			same over time.
		"""
		error = None
		
		flattened =  self.flatit()
		if self._id == ObjectId:
			del flattened['_id']
		
		if self.__collection__ == None:
			self.__collection__ = self.__class__.__name__.lower()
			
		if self.__old_doc__ == None:
			id = db[self.__collection__].save(flattened, safe=True, manipulate=True)
			self._id = id
		else: 
			error = db[self.__collection__].update(self.__old_doc__, flattened, safe=True)
			
		if error != None and 'updatedExisting' in error \
			and error['updatedExisting'] == False:
			raise UpdateFailedError('Document in db is newer than the document for storing')
		return self._id

	
	@classmethod
	def load(cls, db, id):
		"""loads the document from mongodb 
	
		Args:
			db: should must be a pymongo ''Database'' object
			
			id: the document id of the mongodb document
			
		Returns:
			returns the object
		"""
		if cls.__collection__ == None:
			cls.__collection__ = cls.__name__.lower()
		doc = db[cls.__collection__].find_one({'_id':id})
		
		obj = cls.unflatit(doc)
		obj.__old_doc__ =  doc
		
		
		return obj
		
class UpdateFailedError(Exception):
	pass
	