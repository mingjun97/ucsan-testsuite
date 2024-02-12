// METADATA: note.yaml
/* METADATA.yaml
entry: cal
scope:
  - foo
*/
struct node
{
  // char padding[10];
  unsigned int v;
  // int v1;
  struct node* next;
};

int *return_ptr(int *a) {
  return a;
}

int* bar(int *b, int unused) {
  *b += 2;
  return b;
}

int foo(int a) {
  return a + 1;
}


int cal(struct node* head) {
  int sum = 0;
  while (head) {
    sum += head->v;
    if (head->v > 40) return 0;
    head = head->next;
  }
  if (sum > 100) {
    if (sum > 200) {
      printf("Bad1\n");
      __builtin_trap();
    }
  }
  return sum;
}


int main() {
  struct node* head = 0;
  // int* tail = malloc(sizeof(int));
  // *tail = 100;
  //assign label for the first arg
  // dfsan_set_label_for_args(0);
  int r = cal(head);
  printf("sum is %d\n",r);
  return 0;
}