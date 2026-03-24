#include <iostream>

int main() {
    int A = 0;
    int B = 0;
    if (!(std::cin >> A >> B)) {
        return 0;
    }
    std::cout << (A + B) << '\n';
    return 0;
}
