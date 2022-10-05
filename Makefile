all:
	cd c_utils && $(MAKE) && cd ..

clean:
	cd c_utils && $(MAKE) clean
