#include <algorithm>
#include <iostream>
#include <vector>

using i128 = __int128_t;
using u128 = __uint128_t;

bool is_mountain(u128 position) {
    while ((position & 1) == 0) {
        position >>= 1;
    }
    return (position & 3) == 3;
}

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int n;
    std::cin >> n;
    std::vector<i128> a(n);
    for (int i = 0; i < n; ++i) {
        long long value;
        std::cin >> value;
        a[i] = value;
    }

    std::vector<i128> candidates;
    for (i128 value : a) {
        for (int bit = 0; bit <= 65; ++bit) {
            i128 one = i128(1) << bit;
            i128 modulus = i128(1) << (bit + 2);
            i128 residue = (3 * one - value) % modulus;
            if (residue < 0) {
                residue += modulus;
            }
            if (residue == 0) {
                residue = modulus;
            }
            candidates.push_back(residue);
        }
    }
    std::sort(candidates.begin(), candidates.end());
    candidates.erase(
        std::unique(candidates.begin(), candidates.end()), candidates.end()
    );

    int answer = 0;
    for (i128 start : candidates) {
        int count = 0;
        for (i128 offset : a) {
            count += is_mountain(u128(start + offset));
        }
        answer = std::max(answer, count);
    }
    std::cout << answer << '\n';
}
