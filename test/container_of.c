// METADATA: note.yaml
/* METADATA.yaml
entry: cal
scope:
  - foo
*/

struct s {
    int a;
    int c;
    char padding[8];
    int b;
};

int cal(int *b) {
  int sum = 0;
  if (*b != 0xaaaaaa) {
    printf("bad b = %x\n", *b);
    return 0;
    // __builtin_trap();
  }
  void *base = b;
  base = base - __builtin_offsetof(struct s, b);
  struct s *s = (struct s *)base;
  if (s->a == 0xdeadbeef) {
    char * a = s->padding;
    if (a[0] == 'a') {
      printf("bad2\n");
      __builtin_trap();
    }

    printf("bad\n");
    // __builtin_trap();
  }


}

int main() {
  int r = cal(0);
  return 0;
}