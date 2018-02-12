CXX=`which g++`
CXX_FLAGS="-O3 -ftree-loop-distribution -funroll-all-loops -fdata-sections -fstack-protector"
${CXX} -c ${CXX_FLAGS} -I${CFITSIO_ROOT}/include main.cpp -o main.o
${CXX} -c ${CXX_FLAGS} -I${CFITSIO_ROOT}/include recombine.cpp -o recombine.o
${CXX} ${CXX_FLAGS} main.o recombine.o -o recombine -L${CFITSIO_ROOT}/lib -L/usr/lib64 -lcfitio -lcurl

#g++ -O3 -ftree-loop-distribution -funroll-all-loops -fdata-sections -fstack-protector -I${CFITSIO_ROOT}/include recombine.cpp main.cpp -L${CFITSIO_ROOT}/lib -lcfitsio -o recombine 
#cp recombine /group/mwaops/stremblay/CODE/bin/
