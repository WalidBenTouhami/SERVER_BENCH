#include "queue.h"
#include <stdlib.h>

void queue_init(queue_t *q, size_t size_max) {
    q->head = q->tail = NULL;
    q->size = 0;
    q->size_max = size_max;  // 0 = illimité
    q->shutdown = false;
    pthread_mutex_init(&q->mutex, NULL);
    pthread_cond_init(&q->not_empty, NULL);
    pthread_cond_init(&q->not_full, NULL);
}

int queue_push(queue_t *q, void *data) {
    pthread_mutex_lock(&q->mutex);

    while (!q->shutdown &&
           q->size_max > 0 &&
           q->size >= q->size_max) {
        pthread_cond_wait(&q->not_full, &q->mutex);
    }

    if (q->shutdown) {
        pthread_mutex_unlock(&q->mutex);
        return -1;
    }

    queue_node_t *node = (queue_node_t*)malloc(sizeof(queue_node_t));
    if (!node) {
        pthread_mutex_unlock(&q->mutex);
        return -1;
    }
    node->data = data;
    node->next = NULL;

    if (q->tail)
        q->tail->next = node;
    else
        q->head = node;

    q->tail = node;
    q->size++;

    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->mutex);
    return 0;
}

void *queue_pop(queue_t *q) {
    pthread_mutex_lock(&q->mutex);

    while (q->size == 0 && !q->shutdown) {
        pthread_cond_wait(&q->not_empty, &q->mutex);
    }

    if (q->shutdown && q->size == 0) {
        pthread_mutex_unlock(&q->mutex);
        return NULL;
    }

    queue_node_t *node = q->head;
    q->head = node->next;
    if (!q->head)
        q->tail = NULL;

    q->size--;
    void *data = node->data;
    free(node);

    if (q->size_max == 0 || q->size < q->size_max) {
        pthread_cond_signal(&q->not_full);
    }

    pthread_mutex_unlock(&q->mutex);
    return data;
}

void queue_shutdown(queue_t *q) {
    pthread_mutex_lock(&q->mutex);
    q->shutdown = true;
    pthread_cond_broadcast(&q->not_empty);
    pthread_cond_broadcast(&q->not_full);
    pthread_mutex_unlock(&q->mutex);
}

void queue_destroy(queue_t *q) {
    pthread_mutex_lock(&q->mutex);
    queue_node_t *cur = q->head;
    while (cur) {
        queue_node_t *next = cur->next;
        free(cur);
        cur = next;
    }
    pthread_mutex_unlock(&q->mutex);

    pthread_mutex_destroy(&q->mutex);
    pthread_cond_destroy(&q->not_empty);
    pthread_cond_destroy(&q->not_full);
}
