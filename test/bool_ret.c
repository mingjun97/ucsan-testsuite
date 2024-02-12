// METADATA: note.yaml
typedef enum { false, true } bool;
bool external(){
    return false;
}

int cal(int a, int b) {
    if (external()){
        __builtin_trap();
    }
}