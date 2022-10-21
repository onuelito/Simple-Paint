#include <limits.h>
#include <stdlib.h>
#include <stdbool.h>

#define QUEUE_EMPTY INT_MIN

int QUEUE_WIDTH; //Important for 1D array assignment

typedef struct node{
    int x, y;
    struct node *next;
}node_t;

typedef struct queue{
    node_t *head;
    node_t *tail;
}queue_t;

void QUEUE_INITIALIZE(queue_t *q, int width){
    q->head = NULL;
    q->tail = NULL;
    QUEUE_WIDTH = width;
}

bool QUEUE_ENQUEUE(queue_t *q, int x, int y){
    node_t *newnode = malloc(sizeof * newnode);
    if(newnode == NULL) return false;
    newnode->x  = x;
    newnode->y 	= y;
    newnode->next   = NULL;

    if(q->tail != NULL) q->tail->next = newnode;
    q->tail = newnode;

    if(q->head == NULL) q->head = newnode;
    return true;
}

int QUEUE_DEQUEUE(queue_t *q, int *x, int *y){
    if(q->head == NULL) return QUEUE_EMPTY;
    node_t *tmp = q->head;
    *x = tmp->x;
    *y = tmp->y;
    
    q->head = q->head->next;
    if(q->head == NULL) q->tail = NULL;
    free(tmp);
    return ((*x)+(*y*QUEUE_WIDTH));
}
