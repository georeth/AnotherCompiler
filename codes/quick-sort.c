#include <stdio.h>
int arr[30];
void quicksort(int *arr, int from, int to){
    int pivot, left, right, temp;
    left = from + 1;
    if (left >= to)
        return;
    pivot = arr[from];
    right = to - 1;
    while (left <= right){
        if (arr[left] < pivot)
            left = left + 1;
        else {
            temp = arr[left];
            arr[left] = arr[right];
            arr[right] = temp;
            right = right - 1;
        }
    }
    arr[from] = arr[right];
    arr[right] = pivot;

    quicksort(arr, from, right);
    quicksort(arr, left, to);
}
int main(){
    int i;
    arr[0] = 77726;
    arr[1] = 68610;
    arr[2] = 39002;
    arr[3] = 93549;
    arr[4] = 92911;
    arr[5] = 2083;
    arr[6] = 26349;
    arr[7] = 42982;
    arr[8] = 53518;
    arr[9] = 68650;
    arr[10] = 52580;
    arr[11] = 19762;
    arr[12] = 45137;
    arr[13] = 83427;
    arr[14] = 25072;
    arr[15] = 36143;
    arr[16] = 97471;
    arr[17] = 49178;
    arr[18] = 97011;
    arr[19] = 28716;
    arr[20] = 96825;
    arr[21] = 48507;
    arr[22] = 79181;
    arr[23] = 43650;
    arr[24] = 99288;
    arr[25] = 6265;
    arr[26] = 20931;
    arr[27] = 55334;
    arr[28] = 67905;
    arr[29] = 92;
    quicksort(arr, 0, 30);
    for (i=0; i<30; i++)
        printf("%d\n", arr[i]);
}
