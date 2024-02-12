// METADATA: note.yaml
/* METADATA.yaml
entry: cal
scope:
  - foo
*/

int cal(long* a) {
  int sum;
  long ptr = *a;
  sum = *(int *)ptr + 1;
  if (sum > 5) {
    printf("bad\n");
    __builtin_trap();
  };
}


int main() {
  int r = cal(0);
  return 0;
}