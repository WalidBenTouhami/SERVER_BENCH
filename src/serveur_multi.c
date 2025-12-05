#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <math.h>
#include <signal.h>
#include <string.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <time.h>
#include <stdint.h>
#include <pthread.h>
#include "queue.h"

#define PORT 5051
#define BACKLOG 50
#define WORKER_COUNT 8
#define QUEUE_CAPACITY 128

static int server_fd = -1;
static queue_t job_queue;
static volatile sig_atomic_t running = 1;

static uint64_t htonll(uint64_t x) {
#if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
    return __builtin_bswap64(x);
#else
    return x;
#endif
}

static void traitement_lourd(void) {
    double x = 0.0;
    for (int i = 0; i < 100000; i++)
        x += sqrt(i);
    (void)x;
    usleep((rand() % 90 + 10) * 1000);
}

static int64_t timestamp_us(void) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (int64_t)tv.tv_sec * 1000000LL + tv.tv_usec;
}

static void handle_sigint(int sig) {
    (void)sig;
    printf("\n[MULTI] Arrêt via Ctrl+C...\n");
    running = 0;
    if (server_fd >= 0) close(server_fd);
    queue_shutdown(&job_queue);
}

static void *worker_func(void *arg) {
    (void)arg;
    for (;;) {
        int *fd_ptr = (int*)queue_pop(&job_queue);
        if (!fd_ptr) {
            if (!running)
                break;
            else
                continue;
        }
        int client_fd = *fd_ptr;
        free(fd_ptr);

        int32_t number_net;
        ssize_t r = recv(client_fd, &number_net, sizeof(number_net), 0);
        if (r != (ssize_t)sizeof(number_net)) {
            close(client_fd);
            continue;
        }

        int32_t number = ntohl(number_net);
        traitement_lourd();

        int32_t result_net = htonl(number * number);
        int64_t ts = timestamp_us();
        uint64_t ts_net = htonll((uint64_t)ts);

        ssize_t s1 = send(client_fd, &result_net, sizeof(result_net), 0);
        ssize_t s2 = send(client_fd, &ts_net, sizeof(ts_net), 0);
        (void)s1; (void)s2;

        close(client_fd);
    }
    return NULL;
}

int main(void) {
    signal(SIGINT, handle_sigint);
    srand((unsigned)time(NULL));

    queue_init(&job_queue, QUEUE_CAPACITY);

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) { perror("socket"); exit(EXIT_FAILURE); }

    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0)
        perror("setsockopt");

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind"); exit(EXIT_FAILURE);
    }
    if (listen(server_fd, BACKLOG) < 0) {
        perror("listen"); exit(EXIT_FAILURE);
    }

    printf("[MULTI] Serveur multi-thread sur port %d\n", PORT);

    pthread_t workers[WORKER_COUNT];
    for (int i = 0; i < WORKER_COUNT; i++) {
        int err = pthread_create(&workers[i], NULL, worker_func, NULL);
        if (err != 0) {
            fprintf(stderr, "pthread_create error\n");
            running = 0;
            queue_shutdown(&job_queue);
            for (int j = 0; j < i; j++)
                pthread_join(workers[j], NULL);
            close(server_fd);
            queue_destroy(&job_queue);
            return EXIT_FAILURE;
        }
    }

    while (running) {
        struct sockaddr_in client;
        socklen_t len = sizeof(client);
        int client_fd = accept(server_fd, (struct sockaddr*)&client, &len);
        if (client_fd < 0) {
            if (!running) break;
            perror("accept");
            continue;
        }

        int *fd_ptr = (int*)malloc(sizeof(int));
        if (!fd_ptr) {
            fprintf(stderr, "malloc fd_ptr failed\n");
            close(client_fd);
            continue;
        }
        *fd_ptr = client_fd;

        if (queue_push(&job_queue, fd_ptr) < 0) {
            close(client_fd);
            free(fd_ptr);
            break;
        }
    }

    running = 0;
    queue_shutdown(&job_queue);

    for (int i = 0; i < WORKER_COUNT; i++)
        pthread_join(workers[i], NULL);

    queue_destroy(&job_queue);
    return 0;
}
