// METADATA: note.yaml
extern int a;
int* b = &a;
int cal(unsigned int* arr) {
    if (arr != (void*)0xdeadbeef) {
        return 0;
    }
    unsigned int i = 0;
    unsigned int sum = 0;
    while (arr[i] != 0xbb) {
        if (arr[i] > 6) {
            break;
        }
        sum += arr[i];
        i++;
    }
    if (i < 6 && sum == 0x1e) {
        printf("Bad1: i = %d\n", i);
        __builtin_trap();
    }
    return sum;
}

