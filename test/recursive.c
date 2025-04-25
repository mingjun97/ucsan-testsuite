// METADATA: note.yaml
// --FLAG: 200

void foo(int * args) {
    if (args[0] == 0) {
        foo(args + 1);
    } 
}


int cal(int* args) {
    foo(args);
}