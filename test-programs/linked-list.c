#include <stdlib.h>
#include <stdbool.h>

#define slotsPerNode 2

struct node {
  int data[slotsPerNode];
  int size;
  struct node* next;
};

struct linked_list {
  struct node* root;
};

void insert(struct linked_list* list, int data) {
  struct node* r = list->root;
  if (r->size < slotsPerNode) {
    int data[slotsPerNode];
    for (int i = 0; i < r->size; i++) {
      data[i] = r->data[i];
    }
    r->data[0] = data;
    for (int i = 0; i < r->size; i++) {
      r->data[i+1] = data[i];
    }
    r->size++;
  } 
  else {
    struct node* nn = (struct node*) malloc(sizeof(struct node));
    nn->data[0] = data;
    nn->size = 1;
    nn->next = r;
    list->root = nn;
  }
}


bool search(struct linked_list* list, int data) {
  struct node* r = list->root;
  while (r) {
    for (int i = 0; i < r->size; i++) {
    //   klee_assume(r->size >= 0);
    //   klee_assume(r->size < slotsPerNode);
      if (r->data[i] == data) {
        return true;
      }
    }
    r = r->next;
  }
  return false;
}

bool delete(struct linked_list* list, int data) {
  struct node* r = list->root;
  struct node* prev = NULL;
  while (r) {
    for (int i = 0; i < r->size; i++) {
    //   klee_assume(r->size >= 0);
    //   klee_assume(r->size < slotsPerNode);
      if (r->data[i] == data) {
        if (r->size == 1) {
          if (prev) {
            prev->next = r->next;
          }
          else {
            list->root = r->next;
          }
          free(r);
          return true;
        }
        else {
          for (int j = i; j < r->size-1; j++) {
            r->data[j] = r->data[j+1];
          }
          r->size--;
        }
      }
    }
    prev = r;
    r = r->next;
  }
  return false;
}