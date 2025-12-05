#ifndef QUEUE_H
#define QUEUE_H

#include <pthread.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct queue_node {
    void *data;
    struct queue_node *next;
} queue_node_t;

/**
 * Queue FIFO thread-safe, bornée.
 * - mutex + condition variables not_empty / not_full
 * - shutdown permet de réveiller tous les threads en attente.
 */
typedef struct queue {
    queue_node_t *head;
    queue_node_t *tail;
    pthread_mutex_t mutex;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
    bool shutdown;
    size_t size;
    size_t size_max;  // capacité maximale (0 = illimitée)
} queue_t;

void queue_init(queue_t *q, size_t size_max);
int queue_push(queue_t *q, void *data);
void *queue_pop(queue_t *q);
void queue_shutdown(queue_t *q);
void queue_destroy(queue_t *q);

#endif
