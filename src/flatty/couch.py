"""

=======
Classes
=======
"""
import flatty

class Document(flatty.Schema):
	"""
	This class is the base Class for alls couchdb documents
	"""
	
	_id = str
	_rev = str
	
	def store(self, db):
		"""stores the document in the couchdb 
	
		Args:
			db: should must be a couchdb-python ''Database'' object
			
		Returns:
			returns a tuple `id, rev`. `id`  is the document id which stays the
			same over time. `rev` changes on every store.
		"""
		flattened =  self.flatit()
		if self._id == str:
			del flattened['_id']
		if self._rev == str:
			del flattened['_rev']
		self._id, self._rev = db.save(flattened)
		return self._id, self._rev
	
	@classmethod
	def load(cls, db, id):
		"""loads the document from couchdb 
	
		Args:
			db: should must be a couchdb-python ''Database'' object
			
			id: the document id of the couchdb document
			
		Returns:
			returns the object
		"""
		return cls.unflatit(db[id])
		
	