// METADATA: note.yaml
// FLAG: 152,6
// ENV: trace_bounds

int cal(unsigned int* payload, unsigned int desired){
    char* sum = malloc(6);
    if(*payload == 1) {
        memmove(sum + 1, sum, 6); // OOB
    }
    if(*payload == 2) {
        memcpy(sum + 5, sum, 5); // OOB
    }
    if(*payload == 3) {
        mempcpy(sum + 5, sum, 5); // OOB
    }
    if(*payload == 4) {
        memmove(sum + 1, sum, desired); // OOB
    }
    if(*payload == 5) {
        memcpy(sum + 5, sum, desired); // OOB
    }
    if(*payload == 6) {
        memset(sum, 0, desired); // OOB
    }
    return *sum;
}