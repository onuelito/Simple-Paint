
compile: libpaint.o
	#gcc -shared -o floodfill.so floodfill.o
	gcc -shared -o libpaint.so libpaint.o
	#rm *.o
	
libpaint.o: libpaint.c
	gcc -c -Wall -Werror -fpic libpaint.c

clean:
	rm *.o *so
