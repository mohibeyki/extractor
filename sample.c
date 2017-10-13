#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <time.h>
#define _DEBUG 0

/*
 Returns the current time in miliseconds.
*/
double getMilitime(){
        struct timeval ret;
        gettimeofday(&ret, NULL);
        return ((ret.tv_sec ) * 1000000u + ret.tv_usec) / 1.e6;
}

void print_matrix_1D_float(float *A, int nr_rows_A) {

  int i;
  for(i = 0; i < nr_rows_A; ++i){
    printf("%f ",A[i]);
  }
  printf("\n");
}
void print_matrix_1D_int(int *A, int nr_rows_A) {
  
  int i;  
  for(i = 0; i < nr_rows_A; ++i){
    printf("%d ",A[i]);
  }
  printf("\n");

}

void print_matrix_2D(float **A, int nr_rows_A, int nr_cols_A) {
  int i,j;
  for(i = 0; i < nr_rows_A; ++i){
    for(j = 0; j < nr_cols_A; ++j){
      printf("%f ",A[i][j]);
    }
    printf("\n");
  }
  printf("\n");
}



void matrix_mult(float**A,float**B,float**C,int m,int n,int k);
void find_row_min(float**C,int m,int n,int k,int*row_min_array);

int main(int argc, char* argv[])
{
  int i,j;
 
  if(argc<4){
    printf("Input Error\n");
    return 1;
  }
  int m = atoi(argv[1]);
  int n = atoi(argv[2]);
  int k = atoi(argv[3]);

  int *row_min_array = (int*)malloc(sizeof(int) * m);
  float** A = (float**)malloc(sizeof(float*) * m);
  float** B = (float**)malloc(sizeof(float*) * n);
  float** C = (float**)malloc(sizeof(float*) * m);
  for(i=0;i<m;++i)
  {
    A[i]=(float*)malloc(sizeof(float) * n);
  }
  for(i=0;i<n;++i)
  {
    B[i]=(float*)malloc(sizeof(float) * k);
  }
  for(i=0;i<m;++i)
  {
    C[i]=(float*)calloc(k,sizeof(float));//fill C[i][j] elements by zero
  }

  //fill A(m,n) B(n,k)
  srand((unsigned)13960522);
  for (i=0; i<m; i++)
    for (j=0; j<n; j++)
      A[i][j] =(rand()%100)/10.0;//(i*j)%3+1

  for (i=0; i<n; i++)
    for (j=0; j<k; j++)  
      B[i][j] = (rand()%100)/10.0;//(i*j)%3+1
 
  //print input
  if(_DEBUG){
    printf("A:\n");
    print_matrix_2D(A,m,n);
    printf("B:\n");
    print_matrix_2D(B,n,k);
  }
  printf("start timing\tm=%d,n=%d,k=%d\n",m,n,k);
  double start_all = getMilitime();
  double start_matrix_mullt = getMilitime();

  matrix_mult(A,B,C,m,n,k);

  double matrix_mullt_elapsed_time =  getMilitime() - start_matrix_mullt;
  double start_find_row_min = getMilitime();
  
  find_row_min(C,m,n,k,row_min_array);
  
  printf("elapsed time (matrix_mullt): %f sec\n", matrix_mullt_elapsed_time);
  printf("elapsed time (find_row_min): %f sec\n", getMilitime()-start_find_row_min);
  printf("elapsed time: %f sec\n", getMilitime()-start_all);
  
  //print results
  if(_DEBUG)
  {
    printf("C:\n");
    print_matrix_2D(C,m,k);
    printf("row_min_array:\n");
    print_matrix_1D_int(row_min_array,m);
  }
  //write row_min_array in file
  FILE*fp;
  fp = fopen("row_min_array.output","w+");
  for(i=0;i<m;++i)
    fprintf(fp,"%d\n",row_min_array[i]); 
  fclose(fp);
  
  //free
  free(row_min_array);
  for(i=0;i<m;++i)
    free(A[i]);
  for(i=0;i<n;++i)
    free(B[i]);
  for(i=0;i<m;++i)
    free(C[i]);
  free(A);
  free(B);
  free(C);
  return 0;
}

void matrix_mult(float**A,float**B,float**C,int m,int n,int k)
{
  int i,j,count;
  for(i=0;i<m;++i)
    for(j=0;j<k;++j)
      for(count=0;count<n;++count)
        {
          C[i][j] += A[i][count] * B[count][j];
        }
}
void find_row_min(float**C,int m,int n,int k,int*row_min_array)
{
  int i,j;
  for(i=0;i<m;++i){
    row_min_array[i]=0;//index of first element of i-th row
    for(j=1;j<k;++j){
        if(C[i][row_min_array[i]]>C[i][j])
          row_min_array[i]=j;
    }
  }
}

