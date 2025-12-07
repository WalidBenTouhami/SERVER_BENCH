
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
