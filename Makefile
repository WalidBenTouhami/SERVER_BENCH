CC = gcc
CFLAGS = -Wall -Wextra -O2
DEBUGFLAGS = -fsanitize=address,undefined -g

SRC_DIR = src
TEST_DIR = tests

BIN_MONO = serveur_mono
BIN_MULTI = serveur_multi
BIN_TEST_QUEUE = test_queue

SRC_MONO = $(SRC_DIR)/serveur_mono.c $(SRC_DIR)/queue.c
SRC_MULTI = $(SRC_DIR)/serveur_multi.c $(SRC_DIR)/queue.c
SRC_TEST_QUEUE = $(TEST_DIR)/test_queue.c $(SRC_DIR)/queue.c

.PHONY: all clean debug test

all: $(BIN_MONO) $(BIN_MULTI)

$(BIN_MONO): $(SRC_MONO)
	$(CC) $(CFLAGS) -o $@ $^

$(BIN_MULTI): $(SRC_MULTI)
	$(CC) $(CFLAGS) -o $@ $^

$(BIN_TEST_QUEUE): $(SRC_TEST_QUEUE)
	$(CC) $(CFLAGS) -o $@ $^

debug: CFLAGS += $(DEBUGFLAGS)
debug: clean all $(BIN_TEST_QUEUE)

test: $(BIN_TEST_QUEUE)
	./$(BIN_TEST_QUEUE)

clean:
	rm -f $(BIN_MONO) $(BIN_MULTI) $(BIN_TEST_QUEUE) $(SRC_DIR)/*.o $(TEST_DIR)/*.o
