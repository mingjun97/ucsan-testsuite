struct s{
    int a;
    int b;
};

int foo(int *arg1) {
    return *arg1 + 1;
}

int cal(){
    int *p;
    int a, b, c;
    *p = 1;
    c = foo(&b);
    if (a) {
        return 1;
    } else {
        return 0;
    }
}