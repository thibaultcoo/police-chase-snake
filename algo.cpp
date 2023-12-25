#include <iostream>
#include <cstddef>
#include <string>
#include <vector>
#include "matrix.h"

// sandbox cpp file for testing matrix class (working well, still corner cases to look into)
int main()
{
    size_t nRows = 5;
    size_t nCols = 5;
    matrix mat(nRows, nCols);
    matrix invert(nRows, nCols);
    matrix testingInvert(nRows, nCols);
    
    mat.m_M[0][0] = 1;
    mat.m_M[0][1] = 3;
    mat.m_M[0][2] = -5.14;
    mat.m_M[0][3] = -1;
    mat.m_M[0][4] = 3;
    mat.m_M[1][0] = 3.31;
    mat.m_M[1][1] = -11;
    mat.m_M[1][2] = -4.4344;
    mat.m_M[1][3] = -1.4344;
    mat.m_M[1][4] = 9;
    mat.m_M[2][0] = -3.1111;
    mat.m_M[2][1] = -2.43433;
    mat.m_M[2][2] = 1;
    mat.m_M[2][3] = -4;
    mat.m_M[2][4] = -41;
    mat.m_M[3][0] = 12;
    mat.m_M[3][1] = 2.43433;
    mat.m_M[3][2] = -3;
    mat.m_M[3][3] = 0.8;
    mat.m_M[3][4] = 2.8;
    mat.m_M[4][0] = 9;
    mat.m_M[4][1] = 2;
    mat.m_M[4][2] = -3.9;
    mat.m_M[4][3] = 10;
    mat.m_M[4][4] = 9;

    invert = mat.inversion();
    testingInvert = mat * invert;
    
    double sum = 0;
    for (int i = 0; i < nRows; i++) {
        for (int j = 0; j < nCols; j++) {
            sum += testingInvert.m_M[i][j];
            std::cout << " " << testingInvert.m_M[i][j];
        }
        std::cout << std::endl;
    }
    
    if (sum = nCols) {
        std::cout << "Inversion was successful" << std::endl;
    } else {
        std::cout << "Inversion failed !" << std::endl;
    }

}