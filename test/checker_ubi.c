// METADATA: note.yaml
// ENV: KO_CHECKER_UBI
// FLAG: 150,2
struct s{
    int a;
    int b;
};

int cal(int branch){
    int *p;
    int a, b, c;
    if (branch) {
        *p = 1;
    } else {
        c = b + 1;
    }
    if (c) {
        return 1;
    } else {
        return 0;
    }
}