**********************************
flatty.mongo - the mongodb adapter
**********************************

This module helps you to build schemas for mongodb (it uses the pymongo
module for storing the flattened dicts as mongodb documents)

This module has less than 20 lines of python code. If you want to support another
marshaller, look at this modules source code, this should give you a good start.


==============
Simple Example
==============

	
	>>> import flatty
	>>> import pymongo
	>>> from datetime import datetime
	
	We use the db 'flatty_mongodb_test' and create it if it doesn't exist
	
	>>> dbname = 'flatty_mongodb_test'
	>>> client = pymongo.MongoClient('localhost', 27017)
	>>> 
	>>> db = client[dbname]
	>>> 
	
	Here comes the actual flatty code.
	
	To define a flatable class in a mongodb you must inherit from the 
	:class:`flatty.mongo.Document`. You can simply add fields and define their
	types.
	
	>>> class Person(flatty.mongo.Document):
	...     name = basestring
	...     age = int
	...     added = datetime
	...     
	...     def __init__(self, **kwargs):
	...             super(Person,self).__init__(**kwargs)
	...             self.added = datetime.now()
	... 
	>>> 
	>>> person = Person(name='John Doe', age=42)
	>>> person.store(db) # doctest: +ELLIPSIS
	ObjectId('...')
	>>> person2 = Person.load(db, person._id)
	>>> person2.name
	u'John Doe'
	>>> person2.name == person.name
	True
	>>> person.added # doctest: +ELLIPSIS
	datetime.datetime(...)
	
	To update the document call the ``store`` method.
	
	>>> person.name = 'John R. Doe'
	>>> person.store(db) # doctest: +ELLIPSIS
	ObjectId('...')
	
	After retrieving the document from the db once again we will also get the
	updated values.
	
	>>> person = Person.load(db, person._id)
	>>> person.name
	u'John R. Doe'
	 


======================
A more complex example
======================

	>>> from datetime import date
	>>> import flatty
	>>> import pymongo
	
	We use the db 'flatty_mongodb_test' and create it if it doesn't exist
	
	>>> dbname = 'flatty_mongodb_test'
	>>> client = pymongo.MongoClient('localhost', 27017)
	>>> 
	>>> db = client[dbname]
	>>> 
	
	We define the schema
	
	>>> class Comment(flatty.Schema):
	...     user = basestring
	...     txt = basestring
	...     
	>>> class Book(flatty.Schema):
	...     name = basestring
	...     year = date
	...     comments = flatty.TypedList.set_type(Comment)
	...     
	>>> class Address(flatty.Schema):
	...     street = basestring
	...     city = basestring
	... 
	>>> class Library(flatty.mongo.Document):
	...     name = basestring
	...     address = Address 
	...     books = flatty.TypedDict.set_type(Book)
	
	The **important things** we want to show in this schema definition are:
	
		- only the class wich acts as mongodb document need to be subclassed
			from `flatty.mongo.Document all others are subclassed from `flatty.Schema`
		
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
	>>> id = library.store(db)
	
	When we load the the library object from the db again, the whole class 
	structure is restored.
	
	>>> library = Library.load(db, library._id)
	>>> isinstance(library.address, Address)
	True
	>>> isinstance(library.books['978-0596158101'].comments[0], Comment)
	True
	



.. currentmodule:: flatty.mongo

.. automodule:: flatty.mongo
    :members:


