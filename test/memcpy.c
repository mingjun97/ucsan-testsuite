// METADATA: note.yaml
// FLAG: 100 152
// ENV: trace_bounds


int cal(unsigned int* payload, int size){
    char* sum = malloc(10);
    mempcpy(sum, payload, 8);
    if (sum[2] == 'a') {
        exit(100); // memcpy propogate functional
    }

    char* sum2 = malloc(size);
    char* sum3 = malloc(size);
    memcpy(sum2, sum3, *payload); // should be OOB
    return 0;
}