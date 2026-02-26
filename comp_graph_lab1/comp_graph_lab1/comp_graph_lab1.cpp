#include <iostream>
#include <cmath>
#include <algorithm>

using namespace std;

const double EPS = 1e-9;

//1. смотрим на площадь треуглоьника(векторное произведение), если точки на одной прямой, то площадь нулевая
bool task1(double x1, double y1,
    double x2, double y2,
    double x3, double y3) {
    double det = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1);
    return fabs(det) < EPS;
}

//2. точки на одну прямую, смотрим на левые концы отрезков и правые. пересечение если макс из левых меньше мин из правых
bool task2(double xa, double ya,
    double xb, double yb,
    double xc, double yc,
    double xd, double yd) {
    double p1, p2, p3, p4; 
    if (fabs(xa - xb) > EPS) {
        p1 = xa; p2 = xb;
        p3 = xc; p4 = xd;
    }
    else {   
        p1 = ya; p2 = yb;
        p3 = yc; p4 = yd;
    }
    if (p1 > p2) swap(p1, p2);
    if (p3 > p4) swap(p3, p4);
    return max(p1, p3) <= min(p2, p4) + EPS;
}

//3. векторное произведение / 2
double task3(double x1, double y1, double z1,
    double x2, double y2, double z2,
    double x3, double y3, double z3) {
    double abx = x2 - x1, aby = y2 - y1, abz = z2 - z1;
    double acx = x3 - x1, acy = y3 - y1, acz = z3 - z1;
    double vx = aby * acz - abz * acy;
    double vy = abz * acx - abx * acz;
    double vz = abx * acy - aby * acx;
    double parallelogArea = sqrt(vx * vx + vy * vy + vz * vz);
    return 0.5 * parallelogArea;
}

//4. смотрим на смешанное произведение, если точки в одной плоскости, то паралелепипед будет плоским
bool task4(double x1, double y1, double z1,
    double x2, double y2, double z2,
    double x3, double y3, double z3,
    double x4, double y4, double z4) {
    double abx = x2 - x1, aby = y2 - y1, abz = z2 - z1;
    double acx = x3 - x1, acy = y3 - y1, acz = z3 - z1;
    double adx = x4 - x1, ady = y4 - y1, adz = z4 - z1;
    //cмешанное произведение - определитель матрицы 3x3
    double det = abx * (acy * adz - acz * ady)
        - aby * (acx * adz - acz * adx)
        + abz * (acx * ady - acy * adx);
    return fabs(det) < EPS;
}

int main() {
    setlocale(LC_ALL, "Russian");

    //задание 1
    cout << "Точки A, B, C на одной прямой? " << (task1(0,0, 1,1, 2,2) ? "Да" : "Нет") << '\n';

    //задание 2
    cout << "Отрезки AB и CD пересекаются? " << (task2(0,0, 5,0, 3,0, 7,0) ? "Да" : "Нет") << '\n';

    //задание 3
    cout << "Площадь треугольника по координатам вершин = " << task3(0,0,0, 1,0,0, 0,1,0) << '\n';

    //задание 4
    cout << "Точки A, B, C, D в одной плоскости? " << (task4(0,0,0, 1,0,0, 0,1,0, 1,1,0) ? "Да" : "Нет") << '\n';

    return 0;
}
