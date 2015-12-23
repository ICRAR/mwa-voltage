g++ -O3 -ftree-loop-distribution -funroll-all-loops -fdata-sections -fstack-protector -I${CFITSIO_ROOT}/include recombine.cpp main.cpp -L${CFITSIO_ROOT}/lib -lcfitsio -o recombine 
cp recombine /group/mwaops/stremblay/CODE/bin/
