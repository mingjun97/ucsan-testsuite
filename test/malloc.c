// METADATA: note.yaml
// FLAG" 200
int cal(unsigned int* payload, unsigned int length){
    unsigned int* sum = malloc(sizeof(unsigned int));
    if (sum != 0xdeadbeef) {
        exit(0);
        // exit(128);
    }
    for(int i = 0; i < length; i++) {
        *sum += payload[i];
        if (payload[i] > 51) return 0;
    }
    if (*sum > 100){
        if (*sum > 200) {
            exit(200);
        }
    }

    return *sum;
}