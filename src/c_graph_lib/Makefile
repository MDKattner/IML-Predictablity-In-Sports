CC = gcc
BINDIR = ./bin/
INCDIR = ./include/
STD = --std=c23 -xc
WARN = -Wall -Werror -Wpedantic
DBG = -g -fsanitize=address
PYFLAGS = $(shell python3-config --cflags --ldflags --embed)

.PHONY: all clean

all: tests

tests: ./test.c $(INCDIR)functions.c $(INCDIR)types.h
	$(CC) $(STD) $(WARN) $(DBG) ./test.c -o $(BINDIR)$@

tourny: ./python_bindings.c $(INCDIR)functions.c $(INCDIR)types.h
	$(CC) $(STD) $(WARN) -fPIC $(PYFLAGS) -shared ./python_bindings.c -o $(BINDIR)$@.so

clean:
	rm -f $(BINDIR)*
