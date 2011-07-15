================================================================
Flatty - marshaller/unmarshaller for light-schema python objects
================================================================

Introduction
------------

``Flatty`` is a microframework for easily creating flexible python class schemas.
Normaly you will use flatty on top of marshallers which uses python dict as
input/output format. Think of couchdb, json, xml, yaml, etc. With flatty you can
easily store an object-oriented class schema in these systems by just storing 
the data (no meta-data is stored). 

**Key Features:**

	- easy to use
	- couchdb adapter to use flatty schemas with couchdb
	- only plain data is marshaled, no class meta-data
	- extensible, add custom converters for your own needs and types
	- can be easily extended to support unique features of a marshal framework 
	- light-weight (flatty has currently less than 200 lines of code)
	- OpenSource BSD-licensed
	

**Full documentation can be found on** `PyPi Flatty Documentation`_

.. _`PyPi Flatty Documentation`: http://packages.python.org/flatty/index.html


Idea behind Flatty
------------------

The goal of Flatty is to provide a class-to-dict marshaller which stays in the
background on top of other low-level marshallers. They might only support python 
dicts and some base types. 

With Flatty you can build a complete class schema and
marshall/unmarshall (flatten/unflatten) high-level class objects to the low-level 
marshaller which provides the persistence layer. 
A good example where Flatty already provides an 
adapter is couchdb. We tried to keep the schema definition as much as possible 
"standard python" and gather the needed information through inspection to keep 
things easy. 

Flatty reduces everything to a simple dict, without storing metainformation in 
the marshalled data. The marshalling process Flatty uses is simple:
It treats classes as dicts and their attributes as key-value pairs in the dict. 
Lists are stored as lists. That's it.
 

	
Getting started with Flatty
---------------------------

	Let's go:
	
	>>> import flatty

	This imports the flatty module. Now we can define a schema using python
	classes:
		
	>>> class Bar(flatty.Schema):
	...	 a_num = int
	...	 a_str = str
	...	 a_thing = None  
	
	The class `Bar`has 3 attributes. `a_num` is typed as int, `a_str` as string
	and `a_thing` can be of any type. Types are checked during flattening and
	unflattening and couse a `TypeError` Exception if type does not fit.
	
	>>> class Foo(flatty.Schema):
	...	 my_typed_list = flatty.TypedList.set_type(Bar)
	
	The class `Foo` defines just one attribute `my_typed_list`. As the name
	might already explain, the type of this attribute is a list. It acts like a
	normal python list (actually it is inherited from `list`) with one difference
	it only accepts items instances of type `Bar`.
	
	.. note::
	
		The benefit of this "strict" typing with `TypedList` is that `Flatty` 
		knows which types you expect and can create instances of class `Bar` during 
		unflattening. Because flatty doesn't marshal type information it needs
		this information during unmarshaling to restore the correct types 
	
	You can also use just a normal python list but when you unflat your data
	you will just get "classless" items instead of `Bar` instances.
	
	There is also a `TypedDict` to produce "strict" typed dicts
	 
	Next we create some instances. You see we can use named arguments in the
	constructor to fill the attributes.
	
	>>> my_bar = Bar(a_num=42, a_str='hello world', a_thing='whatever type here')
	>>> foo = Foo(my_typed_list=[my_bar,])
	
	No we have `my_bar`added to the list of `foo`. 
	
	.. note::
		
		Above you can see that we use a python list (not `TypedList`) 
		``my_typed_list=[my_bar,]``	to create the `foo` instance with the 
		`my_typed_list` attribute.
		
	Flatty, flat it!
	
	>>> flatted = foo.flatit()
	>>> print flatted
	{'my_typed_list': [{'a_num': 42, 'a_str': 'hello world', 'a_thing': 'whatever type here'}]}
	
	Voila, this is the flattened dictionary you get. 
	
	Per default just instances
	of type `Schema`, `datetime`, `date`, `time` will be flattened. But if  - 
	for example - your marshaller don't understand integers just strings
	you can easily add a `Converter` for type `int` (see reference).

	The `flatted` can now be stored using your favorite low-level marshaller
	(couchdb, json, yaml, xml, etc).
	
	Next we see how we can restore objects only using the flatted data and the
	schema.

	>>> restored_obj = Foo.unflatit(flatted)
	>>> isinstance(restored_obj, Foo)
	True
	>>> isinstance(restored_obj.my_typed_list[0], Bar)
	True
	>>> restored_obj.my_typed_list[0].a_num
	42
	
	The restored_obj is a new object filled with the data of flatted
	
	
Bug Tracker
-----------

If you find any issues please report them on https://github.com/ceelian/Flatty/issues


Getting Flatty
--------------

You can get the python package on the `Python Package Index`_

.. _`Python Package Index`: http://pypi.python.org/pypi/flatty

The git repository is available at `github.com Flatty`_

.. _`github.com Flatty`: https://github.com/ceelian/Flatty


Installation
------------


``Flatty`` can be installed via the Python Package Index of from source.

Using ``easy_install`` to install ``Flatty``::

	$ easy_install Flatty


If you have downloaded a source tarball you can install it
by doing the following::

    $ python setup.py build
    $ python setup.py install


Supported by
------------
Wingware - The Python IDE (http://wingware.com)

Contributing
------------

We are welcome everyone who wants to contribute to Flatty. 
Development of Flatty happens at  https://github.com/ceelian/Flatty

License
-------

Flatty is released under the BSD License. 
The full license text is in the root folder of the Flatty Package.


   