#include <iostream>

int main() {
    long long A = 0;
    long long B = 0;
    if (!(std::cin >> A >> B)) {
        return 0;
    }
    std::cout << (A + B) << '\n';
    return 0;
}
