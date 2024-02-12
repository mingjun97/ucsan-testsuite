// METADATA: note.yaml
// ENV: KO_WRAP_INDIRECT_CALL
static int a;
static int *b;
static struct {
    int a;
    int b;
} c;
static int (*calls[10])(int) ;

int cal() {
    int *d;
    if (*d == 0xdeadbeef) {
        printf("Bad \n");
        __builtin_trap();
    }
    if (a == 0xaaaaaaaa && *b == 0xbbbbbbbb){
        printf("Bad1 \n");
        __builtin_trap();
    }
    if (c.a == 0xcacacaca && c.b == 0xcbcbcbcb){
        printf("Bad2 \n");
        __builtin_trap();
    }
    if (calls[2](0) == 0xffffffff) {
        printf("Bad3 \n");
        __builtin_trap();
    }
}