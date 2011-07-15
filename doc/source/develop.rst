================================================================
Development of Flatty
================================================================

Preparing packaging and distribution
------------------------------------

Test everything
+++++++++++++++
	
in the shell::
	
	cd doc
	make doctest
	
	cd src/flatty/tests
	python __init__.py
	
	
Change Version
++++++++++++++

Change the version in ``src/flatty/__init__.py``
Add changelog in ``CHANGELOG`` 
	
	
Commit and Tag
++++++++++++++
	
in the shell::
	
	cd doc
	make clean

	python setup.py clean
	
	git commit -a
	git tag -a vX.X.X
	git push --tags