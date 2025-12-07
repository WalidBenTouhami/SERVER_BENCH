###############################################################################
#   MAKEFILE PRO – Serveurs TCP/HTTP (C/POSIX) + Queue FIFO
#   Auteur : Walid Ben Touhami
###############################################################################

SRC_DIR   := src
TEST_DIR  := tests
BUILD_DIR := build
BIN_DIR   := bin

CC       := gcc
CFLAGS   := -Wall -Wextra -O2 -pthread -I$(SRC_DIR)
DBGFLAGS := -g -fsanitize=address,undefined -DDEBUG -I$(SRC_DIR)
LDFLAGS  := -lm -pthread

SRC_FILES := $(wildcard $(SRC_DIR)/*.c)
OBJ       := $(SRC_FILES:$(SRC_DIR)/%.c=$(BUILD_DIR)/%.o)

TARGETS := \
    $(BIN_DIR)/serveur_mono \
    $(BIN_DIR)/serveur_multi \
    $(BIN_DIR)/serveur_mono_http \
    $(BIN_DIR)/serveur_multi_http \
    $(BIN_DIR)/test_queue

TEST_OBJ := $(TEST_DIR)/test_queue.o $(BUILD_DIR)/queue.o

GREEN  := \033[1;32m
BLUE   := \033[1;34m
YELLOW := \033[1;33m
RED    := \033[1;31m
RESET  := \033[0m

.PHONY: all
all: prep $(TARGETS)
	@echo "$(GREEN)[OK] Compilation complète réussie !$(RESET)"

prep:
	@mkdir -p $(BUILD_DIR) $(BIN_DIR)

$(BIN_DIR)/serveur_mono: $(BUILD_DIR)/serveur_mono.o $(BUILD_DIR)/queue.o $(BUILD_DIR)/http.o
	@echo "$(BLUE)[LINK] $@$(RESET)"
	@$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(BIN_DIR)/serveur_multi: $(BUILD_DIR)/serveur_multi.o $(BUILD_DIR)/queue.o $(BUILD_DIR)/http.o
	@echo "$(BLUE)[LINK] $@$(RESET)"
	@$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(BIN_DIR)/serveur_mono_http: $(BUILD_DIR)/serveur_mono_http.o $(BUILD_DIR)/http.o $(BUILD_DIR)/queue.o
	@echo "$(BLUE)[LINK HTTP] $@$(RESET)"
	@$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(BIN_DIR)/serveur_multi_http: $(BUILD_DIR)/serveur_multi_http.o $(BUILD_DIR)/queue.o $(BUILD_DIR)/http.o
	@echo "$(BLUE)[LINK HTTP] $@$(RESET)"
	@$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(BIN_DIR)/test_queue: $(TEST_OBJ)
	@echo "$(BLUE)[LINK TEST] $@$(RESET)"
	@$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	@echo "$(YELLOW)[CC] $<$(RESET)"
	@$(CC) $(CFLAGS) -c $< -o $@

$(TEST_DIR)/%.o: $(TEST_DIR)/%.c
	@echo "$(YELLOW)[CC TEST] $<$(RESET)"
	@$(CC) $(CFLAGS) -c $< -o $@

.PHONY: debug
debug: CFLAGS := $(CFLAGS) $(DBGFLAGS)
debug: clean all
	@echo "$(GREEN)[DEBUG MODE ACTIVÉ – ASan + UBSan]$(RESET)"

.PHONY: test
test: prep $(BIN_DIR)/test_queue
	@echo "$(BLUE)[RUN] Test unitaire queue.c$(RESET)"
	@$(BIN_DIR)/test_queue

.PHONY: run_mono run_multi run_mono_http run_multi_http kill_servers

run_mono: $(BIN_DIR)/serveur_mono
	$(BIN_DIR)/serveur_mono &

run_multi: $(BIN_DIR)/serveur_multi
	$(BIN_DIR)/serveur_multi &

run_mono_http: $(BIN_DIR)/serveur_mono_http
	$(BIN_DIR)/serveur_mono_http &

run_multi_http: $(BIN_DIR)/serveur_multi_http
	$(BIN_DIR)/serveur_multi_http &

kill_servers:
	@echo "$(RED)→ Arrêt des serveurs...$(RESET)"
	@pkill serveur_mono || true
	@pkill serveur_multi || true
	@pkill serveur_mono_http || true
	@pkill serveur_multi_http || true

.PHONY: clean
clean:
	@echo "$(RED)[CLEAN] Suppression build/ et bin/$(RESET)"
	@rm -rf $(BUILD_DIR) $(BIN_DIR)

