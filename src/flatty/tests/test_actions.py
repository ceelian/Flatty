#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import flatty
import sys
import copy

from test_utils import is_plain_dict


class ActionsTestCase(unittest.TestCase):
	
	def setUp(self):
		pass
	def tearDown(self):
		pass
	
	def test_is_plain_dict(self):
		
		class Foo(object):
			pass
		
		plain_dict = {'a':1, 'b': [1,3.023,u'utf','hallo'], 'c':{'aa':None,'bb':True}}
		self.assertTrue(is_plain_dict(plain_dict))
		
		cls_dict = copy.deepcopy(plain_dict)
		cls_dict['cls'] = Foo
		self.assertFalse(is_plain_dict(cls_dict))
		
		obj_dict = copy.deepcopy(plain_dict)
		obj_dict['obj'] = Foo()
		self.assertFalse(is_plain_dict(obj_dict))
		
	def test_typed_list(self):
		class Name(flatty.Schema):
			first_name = None
			last_name = None
					
		class Foo(flatty.Schema):
			a = None
			b = flatty.TypedList.set_type(Name)
			
		t1 = Foo()
		t1.a ="hallo"
		
		l1 = Name()
		l1.first_name = "hans"
		l1.last_name = "conrad"
		
		l2 = Name()
		l2.first_name = "karl"
		l2.last_name = "hirsch"
		
		t1.b = []
		t1.b.append(l1)
		t1.b.append(l2)
		  
		marsh = flatty.flatit(t1)
		n1 = flatty.unflatit(Foo, marsh)
		self.assertTrue(is_plain_dict(marsh))
		self.assertEqual(t1.a, n1.a)
		self.assertEqual(len(t1.b), len(n1.b))
		self.assertTrue(isinstance(n1.b, list))
		self.assertTrue(isinstance(n1.b,flatty.TypedList))
		
		for i in range(len(t1.b)):
			self.assertTrue(isinstance(n1.b[i], Name))
			self.assertEqual(t1.b[i].first_name, n1.b[i].first_name)
			self.assertEqual(t1.b[i].last_name, n1.b[i].last_name)
			
		#reflattening and compare if results doesn't change
		marsh2 = flatty.flatit(n1)
		self.assertEqual(marsh, marsh2)
	
	def test_typed_list_constructor(self):
		""" Test for Bug #2
		"""

		class X(flatty.Schema):
			x = int
		
		class Y(flatty.Schema):
			y = int
		
		class Top(flatty.Schema):
			t1 = flatty.TypedList.set_type(X)
			t2 = flatty.TypedList.set_type(Y)
		
		a = X(x=1)
		b = Y(y=2)
		t = Top(t1=[a], t2=[b])
		
		t.flatit()
		
	def test_types_in_typed_list(self):
		class Name(flatty.Schema):
			first_name = None
			last_name = None
					
		class Foo(flatty.Schema):
			a = None
			b = flatty.TypedList.set_type(Name)
			
		t1 = Foo()
		t1.a ="hallo"
		
		l1 = Name()
		l1.first_name = "hans"
		l1.last_name = "conrad"
		
		t1.b = [] #Foo.b()
		t1.b.append(l1)
		t1.b.append('foobar')
		  
		self.assertRaises(TypeError, flatty.flatit, t1)
		
	def test_cascading(self):
		class Bar(flatty.Schema):
			first_name = None
			last_name = None
					
		class Foo(flatty.Schema):
			a = None
			b = Bar
			
		foo1 = Foo(a = 5, b = Bar(
								first_name="Chris",
								last_name="Young"
								)
				)
		
		flatted = flatty.flatit(foo1)
		obj1 = flatty.unflatit(Foo, flatted)
		
		self.assertTrue(is_plain_dict(flatted))
		self.assertTrue(isinstance(obj1, Foo))
		self.assertTrue(isinstance(obj1.a, int))
		self.assertTrue(isinstance(obj1.b, Bar))
		self.assertEqual(obj1.a, 5)
		self.assertEqual(foo1.a, obj1.a)
		self.assertEqual(foo1.b.first_name, obj1.b.first_name)
		self.assertEqual(foo1.b.last_name, obj1.b.last_name)
		self.assertEqual(foo1.b.first_name, "Chris")
		self.assertEqual(foo1.b.last_name, "Young")
		
		#Testing for sideeffects when doing a second instance
		foo2 = Foo(a = 3, b = Bar(
								first_name="Karin",
								last_name="Mayer"
								)
				)
		flatted = flatty.flatit(foo2)
		obj2 = flatty.unflatit(Foo, flatted)
		
		self.assertTrue(is_plain_dict(flatted))
		self.assertTrue(isinstance(obj2, Foo))
		self.assertTrue(isinstance(obj2.a, int))
		self.assertTrue(isinstance(obj2.b, Bar))
		self.assertEqual(obj2.a, 3)
		self.assertEqual(foo2.a, obj2.a)
		self.assertEqual(foo2.b.first_name, obj2.b.first_name)
		self.assertEqual(foo2.b.last_name, obj2.b.last_name)
		self.assertEqual(foo2.b.first_name, "Karin")
		self.assertEqual(foo2.b.last_name, "Mayer")
		
	def test_typed_dict(self):
		class Name(flatty.Schema):
			first_name = None
			last_name = None
					
		class Foo(flatty.Schema):
			a = None
			b = flatty.TypedDict.set_type(Name)
		
		t1 = Foo()
		t1.a ="hallo"
		
		l1 = Name()
		l1.first_name = "hans"
		l1.last_name = "conrad"
		
		l2 = Name()
		l2.first_name = "karl"
		l2.last_name = "hirsch"
		
		t1.b = {}
		t1.b['first'] =l1
		t1.b['second'] =l2
		  
		flat_dict = flatty.flatit(t1)
		n1 = flatty.unflatit(Foo, flat_dict)
		
		self.assertTrue(is_plain_dict(flat_dict))
		self.assertEqual(t1.a, n1.a)
		self.assertEqual(len(t1.b), len(n1.b))
		self.assertTrue(isinstance(n1.b, dict))
		self.assertTrue(str(type(n1.b)) == str(flatty.TypedDict))
		self.assertTrue(isinstance(n1.b, flatty.TypedDict))
		
		for k,v in t1.b.items():
			self.assertTrue(isinstance(n1.b[k], Name))
			self.assertEqual(t1.b[k].first_name, n1.b[k].first_name)
			self.assertEqual(t1.b[k].last_name, n1.b[k].last_name)
			
		#reflattening and compare if results doesn't change
		flat_dict2 = flatty.flatit(n1)
		self.assertEqual(flat_dict, flat_dict2)
		
	def test_types_in_typed_dict(self):
		class Name(flatty.Schema):
			first_name = None
			last_name = None
					
		class Foo(flatty.Schema):
			a = None
			b = flatty.TypedDict.set_type(Name)
		
		t1 = Foo()
		t1.a ="hallo"
		
		l1 = Name()
		l1.first_name = "hans"
		l1.last_name = "conrad"
		
		t1.b = {}
		t1.b['first'] =l1
		t1.b['second'] ="foobar"
		  
		self.assertRaises(TypeError,flatty.flatit,t1)
		
		
	def test_deep_nested_classes(self):
		class Region(flatty.Schema):
			name = str
		
		class Country(flatty.Schema):
			size = int
			regions = flatty.TypedList.set_type(Region)
		
		class World(flatty.Schema):
			countries = flatty.TypedDict.set_type(Country)
		
		regions = [Region(name='styria'),Region(name='carinthia')]
		countries = {'austria':Country(size=7,regions=regions)}
		world = World(countries = countries)
		
		flat_dict = flatty.flatit(world)
		self.assertTrue(is_plain_dict(flat_dict))
		world2 = flatty.unflatit(World, flat_dict)
		flat_dict2 = flatty.flatit(world2)
		self.assertEqual(flat_dict, flat_dict2)

	def test_default_values(self):
		class Country(flatty.Schema):
			desc = str
			pop = int(7)
			num_rivers = 231
		
		class World(flatty.Schema):
			countries = flatty.TypedDict.set_type(Country)
			
		world = World(countries={'austria':Country()})
		self.assertEqual(world.countries['austria'].pop, 7)
		self.assertEqual(world.countries['austria'].num_rivers, 231)
		
		world2 = World(countries={'hungary':Country(pop=20, num_rivers =10)})
		self.assertEqual(world.countries['austria'].pop, 7)
		self.assertEqual(world.countries['austria'].num_rivers, 231)
		self.assertEqual(world2.countries['hungary'].pop, 20)
		self.assertEqual(world2.countries['hungary'].num_rivers, 10)
		
		flat_dict = flatty.flatit(world)
		self.assertTrue(is_plain_dict(flat_dict))
		restored_world = flatty.unflatit(World, flat_dict)
		self.assertEqual(restored_world.countries['austria'].pop, 7)
		self.assertEqual(restored_world.countries['austria'].num_rivers, 231)
		flat_dict2 = flatty.flatit(restored_world)
		self.assertEqual(flat_dict, flat_dict2)
		self.assertTrue(is_plain_dict(flat_dict2))
		
		
		flat_dict = flatty.flatit(world2)
		self.assertTrue(is_plain_dict(flat_dict))
		restored_world = flatty.unflatit(World, flat_dict)
		self.assertEqual(restored_world.countries['hungary'].pop, 20)
		self.assertEqual(restored_world.countries['hungary'].num_rivers, 10)
		flat_dict2 = flatty.flatit(restored_world)
		self.assertTrue(is_plain_dict(flat_dict2))
		self.assertEqual(flat_dict, flat_dict2)
		
	def test_type_safe_flatit(self):
		
		class Country(flatty.Schema):
			desc = str
			pop = int(7)
			num_rivers = 231
		
		country = Country(desc=42)
		self.assertRaises(TypeError, flatty.flatit, country)
		
	def test_type_safe_unflatit(self):
		
		class Country(flatty.Schema):
			desc = str
			pop = int(7)
			num_rivers = 231
		
		flat_dict={'desc':42}
		self.assertRaises(TypeError, flatty.unflatit, Country, flat_dict)
		
	def test_conversion_manager(self):
		import datetime
		
		class Rgb(object):
			def __init__(self, r,g,b):
				self.r = r
				self.g = g
				self.b = b
			
		class RgbConverter(flatty.Converter):
			import datetime
			@classmethod
			def to_flat(cls, obj_type, obj):
				return str("%d,%d,%d"%(obj.r,obj.g, obj.b))
			@classmethod
			def to_obj(cls, val_type, val):
				rgb_arr = str(val).split(',')
				obj = Rgb(int(rgb_arr[0]),int(rgb_arr[1]),int(rgb_arr[2]))
				return obj
		
		flatty.ConvertManager.set_converter(Rgb, RgbConverter)
		
		class Foo(flatty.Schema):
			color = Rgb
			
		my_color = Rgb(255,124,45)
		foo = Foo(color=my_color)
		flat_dict = foo.flatit()
		self.assertTrue(is_plain_dict(flat_dict))
		restored_foo = Foo.unflatit(flat_dict)
		restored_color = restored_foo.color
		self.assertEqual(restored_color.r, my_color.r)
		self.assertEqual(restored_color.g, my_color.g)
		self.assertEqual(restored_color.b, my_color.b)
		
	def test_datetime_conversion(self):
		import datetime
		now = datetime.datetime.now()
		now_flat = flatty.DateTimeConverter.to_flat(datetime.datetime, now)
		restored_now = flatty.DateTimeConverter.to_obj(datetime.datetime, now_flat)
		self.assertEqual(now, restored_now)
		
	
	def test_date_conversion(self):
		import datetime
		now = datetime.datetime.now().date()
		now_flat = flatty.DateConverter.to_flat(datetime.datetime.date, now)
		restored_now = flatty.DateConverter.to_obj(datetime.datetime.date, now_flat)
		self.assertEqual(now, restored_now)
		
	def test_time_conversion(self):
		import datetime
		now = datetime.datetime.now().time()
		now_flat = flatty.TimeConverter.to_flat(datetime.datetime.time, now)
		restored_now = flatty.TimeConverter.to_obj(datetime.datetime.time, now_flat)
		self.assertEqual(now, restored_now)
		
	def test_flatit_primitve(self):
		s = 'Hello World'
		s_flat = flatty.flatit(s)
		self.assertEqual(s, s_flat)
	
			
			
def suite():
	suite = unittest.TestSuite()
	if len(sys.argv) > 1 and sys.argv[1][:2] == 't:':
		suite.addTest(ActionsTestCase(sys.argv[1][2:]))
	else:
		suite.addTest(unittest.makeSuite(ActionsTestCase, 'test'))
	return suite


if __name__ == '__main__':
	#call it with 
	#t:<my_testcase>
	#to launch only <my_testcase> test 
	unittest.TextTestRunner(verbosity=1).run(suite())