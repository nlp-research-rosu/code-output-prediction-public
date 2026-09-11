#include <iomanip>
#include <iostream>
#include <type_traits>
#include <vector>
static unsigned long long __cc_state_visits = 0;
static void __cc_json(std::ostream& out, bool value) { out << (value ? "true" : "false"); }
template <typename T>
static typename std::enable_if<std::is_integral<T>::value && !std::is_same<T, bool>::value>::type
__cc_json(std::ostream& out, T value) { out << value; }
template <typename T>
static typename std::enable_if<std::is_floating_point<T>::value>::type
__cc_json(std::ostream& out, T value) { out << std::setprecision(17) << value; }
template <typename T>
static void __cc_json(std::ostream& out, const std::vector<T>& values) {
  out << '[';
  for (std::size_t index = 0; index < values.size(); ++index) {
    if (index) out << ',';
    __cc_json(out, values[index]);
  }
  out << ']';
}
#include <bits/stdc++.h>
using namespace std;
const int NMAX = 100;
int N, M, K, P;
int memo[NMAX + 2][NMAX + 2][NMAX + 2];
int fact[NMAX + 2], c[NMAX + 2][NMAX + 2];
int comb(int k, int n) { return c[n][k]; }
int ways(int len, int levels_deep, int count) {
  if (memo[len][levels_deep][count] != -1) {
    return memo[len][levels_deep][count];
  }
  if (count > len || (len > 1 && count > len / 2 + 1)) {
    return memo[len][levels_deep][count] = 0;
  }
  if (len == 0) {
    if (count == 0) {
      return memo[len][levels_deep][count] = 1;
    } else {
      return memo[len][levels_deep][count] = 0;
    }
  }
  if (levels_deep == 1) {
    if (count <= 0 || count >= 2) {
      return memo[len][levels_deep][count] = 0;
    }
    return memo[len][levels_deep][count] = fact[len];
  }
  int res = 0;
  res = (res + ways(len - 1, levels_deep - 1, count)) % P;
  for (int pos_me = 2; pos_me < len; pos_me++) {
    int sum = 0;
    for (int c1 = 0; c1 <= count; c1++) {
      sum = (sum + 1LL * ways(pos_me - 1, levels_deep - 1, c1) *
                       ways(len - pos_me, levels_deep - 1, count - c1)) %
            P;
    }
    res = (res + 1LL * comb(pos_me - 1, len - 1) * sum % P) % P;
  }
  if (len != 1) {
    res = (res + ways(len - 1, levels_deep - 1, count)) % P;
  }
  return memo[len][levels_deep][count] = res;
}
int main() {
  ios_base::sync_with_stdio(false);
  cin.tie(nullptr);
  cin >> N >> M >> K >> P;
  fact[0] = 1;
  for (int i = 1; i <= N; i++) {
    fact[i] = (1LL * i * fact[i - 1]) % P;
  }
  c[0][0] = 1;
  for (int i = 1; i <= N; i++) {
    c[i][0] = c[i][i] = 1;
    for (int j = 1; j < i; j++) {
    ++__cc_state_visits;
if (__cc_state_visits == 101) {
std::cout << "{\"N\":";
__cc_json(std::cout, N);
std::cout << ",\"P\":";
__cc_json(std::cout, P);
std::cout << ",\"i\":";
__cc_json(std::cout, i);
std::cout << ",\"vector<int>(c[i],c[i]+i+1)\":";
__cc_json(std::cout, vector<int>(c[i],c[i]+i+1));
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}


      c[i][j] = (c[i - 1][j] + c[i - 1][j - 1]) % P;
    }
  }
  for (int i = 0; i <= N; i++) {
    for (int j = 0; j <= N; j++) {
      for (int k = 0; k <= N; k++) {
        memo[i][j][k] = -1;
      }
    }
  }
  cout << ways(N, M, K) << '\n';
  return 0;
}
