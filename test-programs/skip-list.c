
#include <stdlib.h>
#include <pthread.h>
#include <stdbool.h>

#define SIZE 4
#define MAX_LEVEL 3

typedef int key_t;
typedef int value_t;

typedef struct Node {
    key_t key;
    value_t value;

    int top_level; 
    struct Node* next[SIZE];

    pthread_mutex_t mutex;
    bool deleted_flag;
    bool fully_linked;
} Node;

typedef struct SkipList {
    Node *head, *tail;
} SkipList;



static inline void skiplist_lock(Node* node) {
    pthread_mutex_lock(&node->mutex);
}

static inline void skiplist_unlock(Node* node) {
    pthread_mutex_unlock(&node->mutex);
}

static inline int node_count_in_buffer(Node** buffer, int size, Node* node) {
    int count = 0;
    for (int i = 0; i < size; i++) {
        if (buffer[i] == node) {
            count++;
        }
    }
    return count;
}

/**
    Randomly generates a number and increments level if number less than or equal to 0.5
    Once more than 0.5, returns the level or available max level.
    This decides until which level a new Node is available.
*/
int get_random_level() {
    int level;

    // static int count = 0;    
    // char name[10];
    // sprintf(name, "level%d", count++);
    
    // klee_make_symbolic(&level, sizeof(level), "level");
    // return level;

    int l = 0;
    while(((float)rand()) / ((float)RAND_MAX) <= 0.5f){
        l++;
    }
    return l > MAX_LEVEL ? MAX_LEVEL : l;
}


int find(Node* head, int key, Node** predecessors, Node** successors) {
    int found = -1;
    Node *prev = head; 
    Node* pred[MAX_LEVEL+1];
    Node* succ[MAX_LEVEL+1];
    for (int level = MAX_LEVEL; level >= 0; level--){
        Node *curr = prev;

        while (curr->next[level] && key > curr->key){
            prev = curr;
            curr = curr->next[level];
        }
        
        if(found == -1 && key == prev->key){
            found = level;
        }

        pred[level] = prev;
        succ[level] = curr;
    }
    if (found == -1) 
        for (int i = 0; i < MAX_LEVEL; i++) {
            predecessors[i] = pred[i];
            successors[i] = succ[i];
        }
    return found;
}


bool skiplist_insert(Node* head, key_t key, value_t value) {
    // Get the level until which the new node must be available
    int top_level = get_random_level();
    klee_assume(top_level >= 0);
    klee_assume(top_level <= MAX_LEVEL);

    // Initialization of references of the predecessors and successors
    Node* preds[MAX_LEVEL + 1]; 
    Node* succs[MAX_LEVEL + 1]; 

    for (size_t i = 0; i < MAX_LEVEL + 1; i++){
        preds[i] = NULL;
        succs[i] = NULL;
    }


    // Keep trying to insert the element into the list. In case predecessors and successors are changed,
    // this loop helps to try the insert again
    for (int t = 0; t < 1; ++t) {

        // Find the predecessors and successors of where the key must be inserted
        int found = find(head, key, preds, succs);

        // If found and marked, wait and continue insert
        // If found and unmarked, wait until it is fully_linked and return. No insert needed
        // If not found, go ahead with insert
        if(found != -1){
            // klee_assume(found >= 0);
            // klee_assume(found <= MAX_LEVEL);
            Node* node_found = succs[found];
            
            if(!node_found->deleted_flag){
                while(! node_found->fully_linked){
                }
                return false;
            }
            continue;
        }

        // Store all the Nodes which lock we acquire in a map
        // Map used so that we don't try to acquire lock to a Node we have already acquired
        // This may happen when we have the same predecessor at different levels
        Node* locked_nodes[MAX_LEVEL];
        int locked_nodes_count = 0;
        // klee_assume(locked_nodes_count >= 0);
        // klee_assume(locked_nodes_count <= MAX_LEVEL);

        // Traverse the skip list and try to acquire the lock of predecessor at every level
        Node* pred;
        Node* succ;

        // Used to check if the predecessor and successors are same from when we tried to read them before
        bool valid = true;

        for (int level = 0; valid && (level <= top_level); level++){
            pred = preds[level];
            succ = succs[level];

            // If not already acquired lock, then acquire the lock 
            if(!(node_count_in_buffer(locked_nodes, locked_nodes_count, pred))){
                // skiplist_lock(pred);
                // klee_assume(locked_nodes_count >= 0);
                // klee_assume(locked_nodes_count < MAX_LEVEL);
                locked_nodes[locked_nodes_count++] = pred;
            }

            // If predecessor marked or if the predecessor and successors change, then abort and try again
            valid = !(pred->deleted_flag) && !(succ->deleted_flag) && pred->next[level]==succ;                
        }

        // Conditons are not met, release locks, abort and try again.
        if(!valid){
            // for (int i = 0; i < locked_nodes_count; i++) {
            //     skiplist_unlock(locked_nodes[i]);
            // }
            continue;
        }
        return true;

        // All conditions satisfied, create the Node and insert it as we have all the required locks
        Node* n = (Node*) malloc(sizeof(Node));
        n->key = key;
        n->value = value;
        n->top_level = top_level;
        n->deleted_flag = false;

        // Update the predecessor and successors
        for (int level = 0; level <= top_level; level++){
            n->next[level] = succs[level];
        }

        for (int level = 0; level <= top_level; level++){
            preds[level]->next[level] = n;
        }

        // Mark the node as completely linked.
        n->fully_linked = true;
        
        // Release lock of all the nodes held once insert is complete
        // for (int i = 0; i < locked_nodes_count; i++) {
            // skiplist_unlock(locked_nodes[i]);
        // }
        
        return true;
    }
    return false;
}


value_t skiplist_search(Node* head, key_t key) {
    Node* preds[MAX_LEVEL + 1]; 
    Node* succs[MAX_LEVEL + 1]; 

    for (size_t i = 0; i <= MAX_LEVEL; i++){
        preds[i] = NULL;
        succs[i] = NULL;
    }

    int found = find(head, key, preds, succs);
    // If not found return empty.
    if(found == -1){ return -1;}

    Node *curr = head; 

    for (int level = MAX_LEVEL; level >= 0; level--){
        while (curr->next[level] && key > curr->next[level]->key) {
            curr = curr->next[level];
        }
    }

    curr = curr->next[0];
    
    // If found, unmarked and fully linked, then return value. Else return empty.
    if ((curr != NULL) && (curr->key == key)){
        return curr->value;
    }else {
        return -1;
    }
}