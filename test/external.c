// METADATA: note.yaml
/* METADATA.yaml
entry: cal
scope:
  - foo
*/

struct d{int f1; struct d* f2;};


_Bool external(){
    return 0;
}

struct node
{
  char padding[10];
  unsigned int v;
  // int v1;
  struct node* next;
  struct d d;
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
  return_ptr((int*)&head->d.f1);

  int sum = 0, *p_sum = &sum;
  sum += head->v;

  if (external()) {
    printf("Bad1\n");
    __builtin_trap();
  }

  if (foo(sum) > 10) {
    printf("Bad2\n");
    __builtin_trap();
  }
  if (*bar(&sum, 0) > 66) {
    printf("Bad3\n");
    __builtin_trap();
  }
    if (sum > 1024) {
    printf("Bad6\n");
    __builtin_trap();
  }
  bar(p_sum, 0);
  if (sum > 404) {
    printf("Bad4\n");
    __builtin_trap();
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