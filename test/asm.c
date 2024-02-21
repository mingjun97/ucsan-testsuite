// METADATA: note.yaml
//-- FLAG: 200
int cal(int *a, int b) {
    int x = 500, y = 200, z;

    asm("addl (%%ebx), %%eax;"
        "movl %%eax, %%ecx;"
        : "=c"  (z)
        : "a"   (b), "b" (a)
        :                   /* empty clobber-list */
    );

    if (z == 700)
        exit(200);

    return 0;
}