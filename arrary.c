int cal(int* payload, unsigned int length){
    unsigned int sum = 0;
    for(int i = 0; i < length; i++) {
        sum += payload[i];
        if (payload[i] > 51) return 0;
    }
    // if (sum > 100){
    //     if (sum > 200) {
    //         printf("Bad");
    //     }
    // }

    return sum;
}

int main(){
 printf("%d", cal((void*)1,0));
}