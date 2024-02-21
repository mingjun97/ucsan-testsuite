// METADATA: note.yaml
// FLAG: 200
// ENV: KO_WRAP_INDIRECT_CALL

int cal(int (*a)(int, int*)) {
  int sum = 0;
  if (sum > 0) {
    __builtin_trap();
  }
  if (a(sum, &sum) > 1) {
    exit(200);
  };
  return sum;
}