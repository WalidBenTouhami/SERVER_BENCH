#include <stdio.h>
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
