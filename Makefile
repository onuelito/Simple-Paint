SOURCE=src
TREEDIR=$(SOURCE)/treeglet
COREDIR=$(SOURCE)/core
LIB_DIR=$(SOURCE)/cfuncs
CACHE=__pycache__



compile:
	python -m pip install pyglet==1.5.27 setuptools cython numpy
	python setup.py build_ext -i

clean:
	rm -rf $(TREEDIR)/$(CACHE)
	rm -rf $(SOURCE)/$(CACHE)
	rm -rf $(COREDIR)/$(CACHE)
	rm -rf $(LIB_DIR)/$(CACHE)
	rm -f $(LIB_DIR)/*.so $(LIB_DIR)/*.c
	rm -f -r build

