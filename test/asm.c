// METADATA: note.yaml
int cal(int *a, int b) {
    int x = 500, y = 200, z;

    asm("addl (%%ebx), %%eax;"
        "movl %%eax, %%ecx;"
        : "=c"  (z)
        : "a"   (b), "b" (a)
        :                   /* empty clobber-list */
    );

    if (z == 700)
        __builtin_trap();
    return 0;
}