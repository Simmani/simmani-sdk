// See LICENSE for license details.

//**************************************************************************
// Vector-vector add benchmark
//--------------------------------------------------------------------------
//
// This benchmark uses adds to vectors and writes the results to a
// third vector. The input data (and reference data) should be
// generated using the vvadd_gendata.pl perl script and dumped
// to a file named dataset1.h.
 
#include "util.h"

//--------------------------------------------------------------------------
// Input/Reference Data

#include "dataset1.h"

//--------------------------------------------------------------------------
// vvadd function

void vvadd( float n, float a[], float b[], float c[] )
{
  int i;
  for ( i = 0; i < n; i++ )
    c[i] = a[i] + b[i];
}

//--------------------------------------------------------------------------
// Main

int main( int argc, char* argv[] )
{
  float results_data[DATA_SIZE];

#if PREALLOCATE
  // If needed we preallocate everything in the caches
  vvadd( DATA_SIZE, input_data_X, input_data_Y, results_data );
#endif

  // Do the vvadd
  setStats(1);
  vvadd( DATA_SIZE, input_data_X, input_data_Y, results_data );
  setStats(0);

  printCounters();

  // Check the results
  return verifyFloat( DATA_SIZE, results_data, verify_data );
}
