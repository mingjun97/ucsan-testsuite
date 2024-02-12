// METADATA: note.yaml
int cal(unsigned int* payload, unsigned int length){
    unsigned int* sum = malloc(sizeof(unsigned int));
    printf("ptr = %p\n", sum);
    if (sum != 0xdeadbeef) {
        printf("Bad1\n");
        exit(0);
        // exit(128);
    }
    for(int i = 0; i < length; i++) {
        *sum += payload[i];
        if (payload[i] > 51) return 0;
    }
    if (*sum > 100){
        if (*sum > 200) {
            printf("Bad\n");
            exit(128);
        }
    }

    return *sum;
}


int main(){
    printf("sum = %d\n" , cal((void*)0,0));
}