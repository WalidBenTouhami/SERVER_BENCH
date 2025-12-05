#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include "queue.h"

#define NB_ITEMS 1000

typedef struct {
    queue_t *q;
    int count;
} thread_arg_t;

void *producer(void *arg) {
    thread_arg_t *ctx = (thread_arg_t*)arg;
    for (int i = 0; i < ctx->count; i++) {
        int *v = (int*)malloc(sizeof(int));
        *v = i;
        if (queue_push(ctx->q, v) < 0) {
            fprintf(stderr, "[TEST] producer: queue_push failed\n");
            free(v);
            break;
        }
    }
    return NULL;
}

void *consumer(void *arg) {
    thread_arg_t *ctx = (thread_arg_t*)arg;
    int received = 0;
    for (;;) {
        int *v = (int*)queue_pop(ctx->q);
        if (!v) break;
        received++;
        free(v);
    }
    printf("[TEST] consumer received %d items\n", received);
    return NULL;
}

int main(void) {
    queue_t q;
    queue_init(&q, 128);

    pthread_t prod, cons;
    thread_arg_t arg = { .q = &q, .count = NB_ITEMS };

    if (pthread_create(&prod, NULL, producer, &arg) != 0) {
        perror("pthread_create producer");
        return EXIT_FAILURE;
    }
    if (pthread_create(&cons, NULL, consumer, &arg) != 0) {
        perror("pthread_create consumer");
        return EXIT_FAILURE;
    }

    pthread_join(prod, NULL);
    queue_shutdown(&q);
    pthread_join(cons, NULL);
    queue_destroy(&q);
    printf("[TEST] test_queue terminé.\n");
    return EXIT_SUCCESS;
}
