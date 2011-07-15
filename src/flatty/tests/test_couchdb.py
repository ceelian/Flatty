
import flatty
import couchdb
import unittest
import sys

class CouchdbTestCase(unittest.TestCase):
	
	def setUp(self):
		dbname = 'flatty_couchdb_test'
		self.couch = couchdb.Server()
		if dbname in self.couch:
			del self.couch[dbname]
			self.couch.create(dbname)
		else:
			self.couch.create(dbname)
		
		self.db = self.couch[dbname]
	def tearDown(self):
		pass
	
	def test_create_document(self):
		from datetime import datetime
		db = self.db
		t_now = datetime.now()
		
		class Person(flatty.couch.Document):
			name = str
			age = int
			added = datetime
			
			def __init__(self, **kwargs):
				super(Person,self).__init__(**kwargs)
				self.added = t_now #datetime.now()
			
		person = Person(name='John Doe', age=42)
		self.assertEqual(person.name, 'John Doe')
		self.assertEqual(person.age, 42)
		self.assertEqual(person.added, t_now)
		
		person.store(db)
		old_rev = person._rev
		person2 = Person.load(db, person._id)
		self.assertEqual(person.name, person2.name)
		self.assertEqual(person.added, person2.added)
	
		person2.name = 'John R. Doe'
		person2.store(db)
		person3 = Person.load(db, person._id)
		self.assertTrue(person.name != person3.name)
		self.assertEqual(person.added, person3.added)
		self.assertTrue(person3._rev != old_rev)
		self.assertEqual(person._id, person3._id)
		
	def test_complex_document(self):
		from datetime import date
		db = self.db
		
		class Comment(flatty.Schema):
			user = str
			txt = str
		
		class Book(flatty.Schema):
			name = str
			year = date
			comments = flatty.TypedList.set_type(Comment)
		
		class Address(flatty.Schema):
			street = str
			city = str
			
		class Library(flatty.couch.Document):
			name = str
			address = Address 
			books = flatty.TypedDict.set_type(Book)
		
		
		library = Library(name='IT Library')
		library.address = Address(street='Baker Street 221b', city='London')
		book1 = Book(name='Dive Into Python',
						year = date(2008,10,10))
		book2 = Book(name='Programming Python',
						year = date(2011,1,31))
		book2.comments = []
		book2.comments.append(Comment(user='Alex', txt='good Book'))
		
		library.books={}
		library.books['978-1590593561'] = book1
		library.books['978-0596158101'] = book2
		
		id, rev = library.store(db)
		library2 =  Library.load(db, id)
		
		self.assertEqual(library2.books['978-1590593561'].comments, None)
		self.assertEqual(len(library2.books['978-0596158101'].comments), 1)
		self.assertTrue(isinstance(library2.address, Address))
		
		
def suite():
	suite = unittest.TestSuite()
	if len(sys.argv) > 1 and sys.argv[1][:2] == 't:':
		suite.addTest(CouchdbTestCase(sys.argv[1][2:]))
	else:
		suite.addTest(unittest.makeSuite(CouchdbTestCase, 'test'))
	return suite


if __name__ == '__main__':
	#call it with 
	#t:<my_testcase>
	#to launch only <my_testcase> test 
	unittest.TextTestRunner(verbosity=1).run(suite())