#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
create_http_files.py
--------------------
Script officiel de génération des fichiers HTTP C.

Il génère automatiquement :
  • src/http.h
  • src/http.c
  • src/serveur_mono_http.c
  • src/serveur_multi_http.c

Avec :
  ✔ parseur HTTP robuste
  ✔ réponses HTTP 1.1 standardisées
  ✔ workers multi-thread corrigés (return NULL)
  ✔ structure POSIX propre
"""

from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
SRC.mkdir(exist_ok=True)


# ============================================================
# HTTP.H TEMPLATE
# ============================================================

HTTP_H = textwrap.dedent(r"""
#ifndef HTTP_H
#define HTTP_H

void parse_http_request(const char *req, char *method, char *path, char *query);

void send_http_response(int client_fd,
                        const char *status,
                        const char *content_type,
                        const char *body);

#endif
""")


# ============================================================
# HTTP.C TEMPLATE
# ============================================================

HTTP_C = textwrap.dedent(r"""
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include "http.h"

void parse_http_request(const char *req, char *method, char *path, char *query) {
    char line[1024] = {0};

    /* extraire la première ligne */
    const char *end = strstr(req, "\r\n");
    if (end) {
        size_t len = end - req;
        if (len > 1023) len = 1023;
        memcpy(line, req, len);
        line[len] = '\0';
    } else {
        strncpy(line, req, sizeof(line) - 1);
    }

    char raw_path[512] = {0};
    sscanf(line, "%s %s", method, raw_path);

    char *q = strchr(raw_path, '?');
    if (q) {
        strcpy(query, q + 1);
        *q = '\0';
    } else {
        query[0] = '\0';
    }

    strcpy(path, raw_path);
}

void send_http_response(int client_fd,
                        const char *status,
                        const char *content_type,
                        const char *body) {

    char header[2048];
    int content_length = strlen(body);

    int n = snprintf(header, sizeof(header),
        "HTTP/1.1 %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %d\r\n"
        "Connection: close\r\n\r\n",
        status, content_type, content_length
    );

    send(client_fd, header, n, 0);
    send(client_fd, body, content_length, 0);
}
""")


# ============================================================
# SERVEUR MONO HTTP
# ============================================================

MONO_HTTP = textwrap.dedent(r"""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include "http.h"

#define HTTP_PORT 8080
#define BACKLOG   32

int main(void) {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) { perror("socket"); exit(1); }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr = {0};
    addr.sin_family      = AF_INET;
    addr.sin_port        = htons(HTTP_PORT);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind"); exit(1);
    }
    if (listen(server_fd, BACKLOG) < 0) {
        perror("listen"); exit(1);
    }

    printf("[HTTP-MONO] Serveur HTTP mono-thread sur port %d\n", HTTP_PORT);

    for (;;) {
        int client = accept(server_fd, NULL, NULL);
        if (client < 0) { perror("accept"); continue; }

        char buffer[4096];
        ssize_t n = recv(client, buffer, sizeof(buffer) - 1, 0);
        if (n <= 0) { close(client); continue; }

        buffer[n] = '\0';

        char method[16] = {0};
        char path[256]  = {0};
        char query[256] = {0};

        parse_http_request(buffer, method, path, query);
        printf("[MONO_HTTP] METHOD='%s' | PATH='%s'\n", method, path);

        if (strcmp(path, "/hello") == 0) {
            send_http_response(client,
                               "200 OK",
                               "application/json",
                               "{\"msg\":\"Bonjour depuis serveur mono-thread\"}");
        } else {
            send_http_response(client,
                               "404 Not Found",
                               "text/plain",
                               "404 NOT FOUND");
        }

        close(client);
    }

    return 0;
}
""")


# ============================================================
# SERVEUR MULTI HTTP (AVEC WORKER CORRIGÉ)
# ============================================================

MULTI_HTTP = textwrap.dedent(r"""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <arpa/inet.h>
#include "queue.h"
#include "http.h"

#define HTTP_PORT    8081
#define BACKLOG      64
#define WORKERS      8
#define BUFFER_SIZE  4096

typedef struct {
    int client_fd;
} job_t;

static queue_t job_queue;

static void* worker(void *arg) {
    (void)arg;

    for (;;) {
        job_t *job = queue_pop(&job_queue);
        if (!job) continue;

        char buffer[BUFFER_SIZE];
        ssize_t n = recv(job->client_fd, buffer, sizeof(buffer)-1, 0);

        if (n <= 0) {
            close(job->client_fd);
            free(job);
            continue;
        }

        buffer[n] = '\0';

        printf("[MULTI_HTTP] Requête reçue : %.*s\n", (int)n, buffer);

        char method[16] = {0};
        char path[256]  = {0};
        char query[256] = {0};

        parse_http_request(buffer, method, path, query);

        if (strcmp(path, "/hello") == 0) {
            send_http_response(job->client_fd, "200 OK", "application/json",
                               "{\"msg\":\"Hello depuis serveur multi-thread\"}");
        } else {
            send_http_response(job->client_fd, "404 Not Found", "text/plain",
                               "404 NOT FOUND");
        }

        close(job->client_fd);
        free(job);
    }

    return NULL;  // 🔥 correction du warning GCC
}

int main(void) {
    queue_init(&job_queue, 128);

    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) { perror("socket"); exit(1); }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr = {0};
    addr.sin_family      = AF_INET;
    addr.sin_port        = htons(HTTP_PORT);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind"); exit(1);
    }
    if (listen(server_fd, BACKLOG) < 0) {
        perror("listen"); exit(1);
    }

    printf("[HTTP-MULTI] Serveur HTTP multi-thread sur port %d\n", HTTP_PORT);

    pthread_t threads[WORKERS];
    for (int i = 0; i < WORKERS; i++)
        pthread_create(&threads[i], NULL, worker, NULL);

    for (;;) {
        int client_fd = accept(server_fd, NULL, NULL);
        if (client_fd < 0) continue;

        job_t *job = malloc(sizeof(job_t));
        job->client_fd = client_fd;

        queue_push(&job_queue, job);
    }

    return 0;
}
""")


# ============================================================
# FILE WRITER
# ============================================================

def write(path, content):
    path.write_text(content, encoding="utf-8")
    print(f"✔ Généré : {path}")


def main():
    print("──────────────────────────────────────────────")
    print("🛠  Génération des fichiers HTTP C")
    print("──────────────────────────────────────────────")

    write(SRC / "http.h", HTTP_H)
    write(SRC / "http.c", HTTP_C)
    write(SRC / "serveur_mono_http.c", MONO_HTTP)
    write(SRC / "serveur_multi_http.c", MULTI_HTTP)

    print("\n✔ Tous les fichiers HTTP ont été régénérés.")
    print("💡 Prochaine étape : make clean && make -j\n")


if __name__ == "__main__":
    main()

