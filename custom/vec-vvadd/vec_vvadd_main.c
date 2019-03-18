// See LICENSE for license details.

//**************************************************************************
// Vector VVADD benchmark for Hwacha v4
//--------------------------------------------------------------------------
//

#include "util.h"
#include "vec_vvadd.h"
#include <assert.h>

//--------------------------------------------------------------------------
// Input/Reference Data

#include "dataset1.h"

//--------------------------------------------------------------------------
// vvadd function

void vvadd( float n, float c[], float a[], float b[] )
{
  int i;
  for ( i = 0; i < n; i++ )
    c[i] = a[i] + b[i];
}


//--------------------------------------------------------------------------
// Main

int main( int argc, char* argv[] )
{
  float result[DATA_SIZE];

#if PREALLOCATE
  // If needed we preallocate everything in the caches
  vvadd( DATA_SIZE, result, input_data_X, input_data_Y );
#endif

  // We need touch data to make sure there's no page-fault by hwacha
  // And also for performance comparisons
  setStats(1);
  vvadd( DATA_SIZE, result, input_data_X, input_data_Y );
  setStats(0);

  printf("[vvadd]\n");
  printCounters();

  assert(verifyFloat( DATA_SIZE, result, verify_data ) == 0);

#if PREALLOCATE
  // If needed we preallocate everything in the caches
  vvadd( DATA_SIZE, result, input_data_X, input_data_Y );
#endif

  setStats(1);
  vec_vvadd_asm(DATA_SIZE, result, input_data_X, input_data_Y);
  setStats(0);

  printf("[vec-vvadd]\n");
  printCounters();

  // Check the results
  return verifyFloat(DATA_SIZE, result, verify_data);
}
