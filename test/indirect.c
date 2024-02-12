// METADATA: note.yaml
// ENV: KO_WRAP_INDIRECT_CALL
/* METADATA.yaml
entry: cal
scope:
  - foo
*/

int cal(int (*a)(int, int*)) {
  int sum = 0;
  if (sum > 0) {
    __builtin_trap();
  }
  if (a(sum, &sum) > 1) {
    printf("bad\n");
    __builtin_trap();
  };
  return sum;
}


int main() {
  int r = cal(0);
  return 0;
}