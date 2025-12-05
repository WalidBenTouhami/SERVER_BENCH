###############################################################################
#                           MAKEFILE PRO – C/POSIX SERVER
#                     Serveur Mono & Multi-thread + Queue FIFO
#                     Auteur : Walid Ben Touhami (projet système)
###############################################################################

# Dossiers
SRC_DIR  := src
TEST_DIR := tests
BUILD_DIR := build
BIN_DIR  := bin

# Compilateur & flags (NE PAS METTRE AVANT !)
CC       := gcc
CFLAGS   := -Wall -Wextra -O2 -pthread -I$(SRC_DIR)
DBGFLAGS := -g -fsanitize=address,undefined -DDEBUG -I$(SRC_DIR)
LDFLAGS  := -lm -pthread


# Programmes à générer
TARGETS := $(BIN_DIR)/serveur_mono $(BIN_DIR)/serveur_multi $(BIN_DIR)/test_queue

# Trouve tous les .c dans src/
SRC_FILES := $(wildcard $(SRC_DIR)/*.c)

# Convertit .c → build/*.o
OBJ := $(SRC_FILES:$(SRC_DIR)/%.c=$(BUILD_DIR)/%.o)

# Test queue
TEST_OBJ := $(TEST_DIR)/test_queue.o $(BUILD_DIR)/queue.o

# Couleurs
GREEN  := \033[1;32m
BLUE   := \033[1;34m
YELLOW := \033[1;33m
RED    := \033[1;31m
RESET  := \033[0m

###############################################################################
#                            RÈGLE PRINCIPALE
###############################################################################
.PHONY: all
all: prep $(TARGETS)
	@echo "$(GREEN)[OK] Compilation complète réussie !$(RESET)"

###############################################################################
#                            PRÉPARATION DOSSIERS
###############################################################################
prep:
	@mkdir -p $(BUILD_DIR) $(BIN_DIR)

###############################################################################
#                         COMPILATION DES PROGRAMMES
###############################################################################

# Serveur mono-thread
$(BIN_DIR)/serveur_mono: $(BUILD_DIR)/serveur_mono.o $(BUILD_DIR)/queue.o
	@echo "$(BLUE)[LINK] $@$(RESET)"
	@$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

# Serveur multi-thread
$(BIN_DIR)/serveur_multi: $(BUILD_DIR)/serveur_multi.o $(BUILD_DIR)/queue.o
	@echo "$(BLUE)[LINK] $@$(RESET)"
	@$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

# Test unitaire queue
$(BIN_DIR)/test_queue: $(TEST_OBJ)
	@echo "$(BLUE)[LINK TEST] $@$(RESET)"
	@$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

###############################################################################
#                  RÈGLE GÉNÉRIQUE : .c → .o dans build/
###############################################################################
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	@echo "$(YELLOW)[CC] $<$(RESET)"
	@$(CC) $(CFLAGS) -c $< -o $@

###############################################################################
#                  RÈGLE GÉNÉRIQUE POUR LES TESTS
###############################################################################
$(TEST_DIR)/%.o: $(TEST_DIR)/%.c
	@echo "$(YELLOW)[CC TEST] $<$(RESET)"
	@$(CC) $(CFLAGS) -c $< -o $@

###############################################################################
#                           MODE DEBUG AVEC SANITIZERS
###############################################################################
.PHONY: debug
debug: CFLAGS += $(DBGFLAGS)
debug: clean all
	@echo "$(GREEN)[DEBUG MODE ACTIVÉ] Sanitizers ASan + UBSan$(RESET)"

###############################################################################
#                                   TESTS
###############################################################################
.PHONY: test
test: prep $(BIN_DIR)/test_queue
	@echo "$(BLUE)[RUN] Test unitaire queue.c$(RESET)"
	@$(BIN_DIR)/test_queue

###############################################################################
#                         COMMANDES PRATIQUES (RUN)
###############################################################################
.PHONY: run_mono run_multi kill_servers

run_mono: $(BIN_DIR)/serveur_mono
	@echo "$(GREEN)→ Lancement du serveur mono-thread (port 5050)...$(RESET)"
	@$(BIN_DIR)/serveur_mono &

run_multi: $(BIN_DIR)/serveur_multi
	@echo "$(GREEN)→ Lancement du serveur multi-thread (port 5051)...$(RESET)"
	@$(BIN_DIR)/serveur_multi &

kill_servers:
	@echo "$(RED)→ Arrêt des serveurs...$(RESET)"
	@pkill serveur_mono || true
	@pkill serveur_multi || true

###############################################################################
#                                   CLEAN
###############################################################################
.PHONY: clean
clean:
	@echo "$(RED)[CLEAN] Suppression binaires & objets$(RESET)"
	rm -rf $(BUILD_DIR) $(BIN_DIR)

