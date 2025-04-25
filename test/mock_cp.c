// METADATA: note.yaml
// FLAG: 200
// ENV: trace_bounds

#include <stdio.h>
#include <unistd.h>

char items[3][10];

int cal()
{
    char* buff;
    int i = 0;
    do{
        printf("input item:");
        buff = &items[i][0];
        i++;
        fgets(buff, 40, stdin);
        buff[strcspn(buff, "\n")] = 0;
    }while(strlen(buff)!=0);
    i--;

    
    printf("done adding items\n");
    int j;
    printf("display item #:");
    // scanf("%d", &j);
    char buffer[40];
    fgets(buffer, 40, stdin);
    j = atoi(buffer);
    buff = &items[j][0];
    printf("item %d: %s\n", j, buff);


    return 0;
}
