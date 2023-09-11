gcc -ggdb `pkg-config --cflags opencv` tanuki.c -o tanuki `pkg-config --libs opencv`;
