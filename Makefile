
CC=gcc
OBJ_DIR=c_utils
TARGET = $(OBJ_DIR)/libpaint
CFLAGS = -Wall -Werror -fpic

compile: $(TARGET).o
	$(CC) -shared -o $(TARGET).so $(TARGET).o
	cd $(OBJ_DIR) && rm *.o
	
$(TARGET).o: $(TARGET).c
	$(CC) $(CFLAGS) -c $(TARGET).c && mv libpaint.o $(OBJ_DIR)
	
clean:
	cd $(OBJ_DIR) && rm *.o *.so
