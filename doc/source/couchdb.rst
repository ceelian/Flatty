**********************************
flatty.couch - the couchdb adapter
**********************************

This module helps you to build schemas for couchdb (it uses the couchdb-python
module for storing the flattened dicts as couchdb documents)

This module has less than 20 lines of python code. If you want to support another
marshaller, look at this modules source code, this should give you a good start.


==============
Simple Example
==============

	
	>>> import flatty
	>>> import couchdb
	>>> from datetime import datetime
	
	We use the db 'flatty_couchdb_test' and create it if it doesn't exist
	
	>>> dbname = 'flatty_couchdb_test'
	>>> server = couchdb.Server('http://localhost:5984/')
	>>> 
	>>> if dbname not in server:
	...     db = server.create(dbname)
	... else:
	...     db = server[dbname]
	>>> 
	
	Here comes the actual flatty code. This example is intentionally similar to
	the example for the couchdb-python mapper (http://packages.python.org/CouchDB/mapping.html)
	because we want to show the differences.
	
	To define a flatable class in a couchdb you must inherit from the 
	:class:`flatty.couch.Document`. You can simply add fields and define their
	types.
	
	>>> class Person(flatty.couch.Document):
	...     name = str
	...     age = int
	...     added = datetime
	...     
	...     def __init__(self, **kwargs):
	...             super(Person,self).__init__(**kwargs)
	...             self.added = datetime.now()
	... 
	>>> 
	>>> person = Person(name='John Doe', age=42)
	>>> person.store(db)   #doctest: +ELLIPSIS
	('...', '...')  
	>>> old_rev = person._rev
	>>> person = Person.load(db, person._id)
	>>> person.name
	'John Doe'
	>>> person.added #doctest: +ELLIPSIS
	datetime.datetime(...)
	
	To update the document call the ``store`` method.
	
	>>> person.name = 'John R. Doe'
	>>> person.store(db) #doctest: +ELLIPSIS
	('...', '...')
	
	After retrieving the document from the db once again we will also get the
	updated values.
	
	>>> person = Person.load(db, person._id)
	>>> person.name
	'John R. Doe'
	>>> person._rev != old_rev
	True
	>>> 


======================
A more complex example
======================

	>>> from datetime import date
	>>> import flatty
	>>> import couchdb
	
	We use the db 'flatty_couchdb_test' and create it if it doesn't exist
	
	>>> dbname = 'flatty_couchdb_test'
	>>> server = couchdb.Server('http://localhost:5984/')
	>>>  
	... if dbname not in server:
	...     db = server.create(dbname)
	... else:
	...     db = server[dbname]
	
	We define the schema
	
	>>> class Comment(flatty.Schema):
	...     user = str
	...     txt = str
	...     
	>>> class Book(flatty.Schema):
	...     name = str
	...     year = date
	...     comments = flatty.TypedList.set_type(Comment)
	...     
	>>> class Address(flatty.Schema):
	...     street = str
	...     city = str
	... 
	>>> class Library(flatty.couch.Document):
	...     name = str
	...     address = Address 
	...     books = flatty.TypedDict.set_type(Book)
	
	The **important things** we want to show in this schema definition are:
	
		- only the class wich acts as couchdb document need to be subclassed
			from `flatty.couch.Document all others are subclassed from `flatty.Schema`
		
		- Schema classes can be cascaded easily either direct (like Address) or
			with `flatty.TypedDict` and `flatty.TypedList`. 
	
	Now we can create objects and store it to the db
	
	>>> library = Library(name='IT Library')
	>>> library.address = Address(street='Baker Street 221b', city='London')
	>>> book1 = Book(name='Dive Into Python',
	...              year = date(2008,10,10))
	>>> book2 = Book(name='Programming Python',
	...              year = date(2011,1,31))
	>>> book2.comments = []
	>>> book2.comments.append(Comment(user='Alex', txt='good Book'))
	>>> library.books={}
	>>> library.books['978-1590593561'] = book1
	>>> library.books['978-0596158101'] = book2
	>>> id, rev = library.store(db)
	
	When we load the the library object from the db again, the whole class 
	structure is restored.
	
	>>> library = Library.load(db, library._id)
	>>> isinstance(library.address, Address)
	True
	>>> isinstance(library.books['978-0596158101'].comments[0], Comment)
	True
	



.. currentmodule:: flatty.couch

.. automodule:: flatty.couch
    :members:


