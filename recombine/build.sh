g++ -O3 -ftree-loop-distribution -funroll-all-loops -fdata-sections -fstack-protector recombine.cpp main.cpp -lcfitsio -o recombine 
