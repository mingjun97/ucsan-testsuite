#include <stdlib.h>
#include <pthread.h>
#include <stdbool.h>

// priority queue

typedef struct Node {
    int priority;
    int value;
    int thread_id;
    pthread_mutex_t lock;
} Node;


typedef struct Queue {
    Node *nodes;
    unsigned size;
    unsigned max_size;
    pthread_mutex_t lock;
} Queue;


Queue *queue_create(unsigned size) {
    Queue *queue = (Queue *) malloc(sizeof(Queue));
    queue->nodes = (Node *) malloc(sizeof(Node) * size);
    queue->size = 0;
    queue->max_size = size;
    // pthread_mutex_init(&queue->lock, NULL);
    return queue;
}

bool has_left_child(Queue *queue, unsigned index) {
    return index * 2 < queue->size;
}

bool has_right_child(Queue *queue, unsigned index) {
    return index * 2 + 1 < queue->size;
}

void swap(Node *a, Node *b) {
    Node temp = *a;
    *a = *b;
    *b = temp;
}

void insert(Queue *queue, int priority, int value, int thread_id) {
    // pthread_mutex_lock(&queue->lock);
    klee_assume(queue->size <= 4);
    
    if (queue->size == 4) {
        // pthread_mutex_unlock(&queue->lock);
        return;
    }

    Node node = {
        .priority = priority,
        .value = value,
        .thread_id = thread_id,
    };
    // pthread_mutex_init(&node.lock, NULL);
    
    queue->nodes[queue->size] = node;
    queue->size++;

    unsigned index = queue->size - 1;    
    while (index > 1) {
        unsigned parent = (index - 1) / 2;
        if (queue->nodes[index].priority < queue->nodes[parent].priority) {
            swap(&queue->nodes[index], &queue->nodes[parent]);
            index = parent;
        } else {
            break;
        }
    }

    // pthread_mutex_unlock(&queue->lock);
}


int remove_min(Queue *queue) {
    // pthread_mutex_lock(&queue->lock);
    klee_assume(queue->size <= 4);
    if (queue->size == 0) {
        // pthread_mutex_unlock(&queue->lock);
        return -1;
    }

    int min = queue->nodes[0].value;
    queue->nodes[0] = queue->nodes[queue->size - 1];
    queue->size--;

    unsigned index = 0;
    while (has_left_child(queue, index)) {
        unsigned left = index * 2;
        unsigned right = index * 2 + 1;
        unsigned child = left;
        if (has_right_child(queue, index) && queue->nodes[right].priority < queue->nodes[left].priority) {
            child = right;
        }
        if (queue->nodes[index].priority > queue->nodes[child].priority) {
            swap(&queue->nodes[index], &queue->nodes[child]);
            index = child;
        } else {
            break;
        }
    }

    // pthread_mutex_unlock(&queue->lock);
    return min;
}