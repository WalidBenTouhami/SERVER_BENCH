#!/usr/bin/env python3
import os

SRC_DIR = "src"
os.makedirs(SRC_DIR, exist_ok=True)

print("📦 Génération des fichiers HTTP…")

# --------------------------------------------------------------------------
# http.h
# --------------------------------------------------------------------------
http_h = """#ifndef HTTP_H
#define HTTP_H

void parse_http_request(const char *req, char *method, char *path, char *query);
void send_http_response(int client_fd, const char *content_type, const char *body);

#endif
"""

# --------------------------------------------------------------------------
# http.c – version finalisée PRO, robuste
# --------------------------------------------------------------------------
http_c = r"""#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/socket.h>
#include "http.h"

void parse_http_request(const char *req, char *method, char *path, char *query) {
    char line[1024];
    const char *end = strpbrk(req, "\r\n");

    if (end) {
        size_t len = end - req;
        if (len >= sizeof(line)) len = sizeof(line) - 1;
        memcpy(line, req, len);
        line[len] = '\0';
    } else {
        strncpy(line, req, sizeof(line) - 1);
        line[sizeof(line) - 1] = '\0';
    }

    char url[512] = {0};
    sscanf(line, "%s %s", method, url);

    char *qmark = strchr(url, '?');
    if (qmark) {
        strcpy(query, qmark + 1);
        *qmark = '\0';
    } else {
        query[0] = '\0';
    }

    strcpy(path, url);
}

void send_http_response(int client_fd, const char *content_type, const char *body) {
    char header[4096];

    snprintf(header, sizeof(header),
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %ld\r\n"
        "Connection: close\r\n\r\n",
        content_type, (long)strlen(body)
    );

    send(client_fd, header, strlen(header), 0);
    send(client_fd, body, strlen(body), 0);
}
"""

# --------------------------------------------------------------------------
# serveur_mono_http.c
# --------------------------------------------------------------------------
mono_http = r"""#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>
#include "http.h"

#define PORT 5050

int main() {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);

    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);
    addr.sin_addr.s_addr = INADDR_ANY;

    bind(server_fd, (struct sockaddr*)&addr, sizeof(addr));
    listen(server_fd, 10);

    printf("Serveur HTTP mono-thread sur port %d...\n", PORT);

    char buffer[4096];

    while (1) {
        int client_fd = accept(server_fd, NULL, NULL);
        int n = recv(client_fd, buffer, sizeof(buffer)-1, 0);
        if (n <= 0) { close(client_fd); continue; }

        buffer[n] = '\0';

        char method[16], path[256], query[256];
        parse_http_request(buffer, method, path, query);

        printf("→ METHOD=%s | PATH=%s\n", method, path);

        if (strcmp(path, "/hello") == 0) {
            send_http_response(client_fd, "application/json",
                "{\"msg\":\"Bonjour depuis mono-thread\"}");
        } else {
            send_http_response(client_fd, "text/plain", "404 NOT FOUND");
        }
        close(client_fd);
    }
    return 0;
}
"""

# --------------------------------------------------------------------------
# serveur_multi_http.c – version stable et robuste
# --------------------------------------------------------------------------
multi_http = r"""#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>

#include "queue.h"
#include "http.h"

#define PORT 5051
#define WORKERS     8
#define BUFFER_SIZE 4096

typedef struct {
    int client_fd;
} job_t;

queue_t job_queue;

void* worker(void *arg) {
    (void)arg;

    while (1) {
        job_t *job = (job_t*) queue_pop(&job_queue);
        if (!job) continue;

        char buffer[BUFFER_SIZE];
        int n = recv(job->client_fd, buffer, sizeof(buffer) - 1, 0);
        if (n <= 0) { close(job->client_fd); free(job); continue; }

        buffer[n] = '\0';

        printf("\n==== RAW HTTP REQUEST ====\n%s\n", buffer);

        char method[16] = {0};
        char path[256]  = {0};
        char query[256] = {0};

        parse_http_request(buffer, method, path, query);

        printf("METHOD='%s' | PATH='%s' | QUERY='%s'\n", method, path, query);

        if (strcmp(path, "/hello") == 0) {
            send_http_response(job->client_fd, "application/json",
                "{\"msg\":\"Hello from multi-thread HTTP server\"}");
        }
        else {
            send_http_response(job->client_fd, "text/plain",
                "404 NOT FOUND");
        }

        close(job->client_fd);
        free(job);
    }
}

int main() {
    queue_init(&job_queue, 64);

    int server_fd = socket(AF_INET, SOCK_STREAM, 0);

    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_port   = htons(PORT);
    addr.sin_addr.s_addr = INADDR_ANY;

    bind(server_fd, (struct sockaddr*)&addr, sizeof(addr));
    listen(server_fd, 50);

    printf("Serveur HTTP multi-thread en écoute sur port %d...\n", PORT);

    pthread_t w[WORKERS];
    for (int i = 0; i < WORKERS; i++)
        pthread_create(&w[i], NULL, worker, NULL);

    while (1) {
        int client_fd = accept(server_fd, NULL, NULL);

        job_t *job = malloc(sizeof(job_t));
        job->client_fd = client_fd;

        queue_push(&job_queue, job);
    }

    return 0;
}
"""

# --------------------------------------------------------------------------
# Écriture des fichiers
# --------------------------------------------------------------------------
files = {
    "http.h": http_h,
    "http.c": http_c,
    "serveur_mono_http.c": mono_http,
    "serveur_multi_http.c": multi_http
}

for name, content in files.items():
    path = os.path.join(SRC_DIR, name)
    with open(path, "w") as f:
        f.write(content)
    print(f"✔ Fichier généré : {path}")

print("\n🎉 Génération terminée : HTTP C files updated.\n")

