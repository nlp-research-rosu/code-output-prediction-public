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
template <typename _Tp>
void read(_Tp &x) {
  char ch(getchar());
  bool f(false);
  while (!isdigit(ch)) f |= ch == 45, ch = getchar();
  x = ch & 15, ch = getchar();
  while (isdigit(ch)) x = x * 10 + (ch & 15), ch = getchar();
  if (f) x = -x;
}
template <typename _Tp, typename... Args>
void read(_Tp &t, Args &...args) {
  read(t);
  read(args...);
}
const int N = 205;
int n, mod;
template <typename _Tp1, typename _Tp2>
inline void add(_Tp1 &a, _Tp2 b) {
  a = a + b >= mod ? a + b - mod : a + b;
}
template <typename _Tp1, typename _Tp2>
inline void sub(_Tp1 &a, _Tp2 b) {
  a = a - b < 0 ? a - b + mod : a - b;
}
long long fac[N], inv[N], ifac[N];
void init() {
  fac[0] = fac[1] = inv[0] = inv[1] = ifac[0] = ifac[1] = 1;
  for (int i = 2; i < N; ++i)
    fac[i] = fac[i - 1] * i % mod,
    inv[i] = inv[mod % i] * (mod - mod / i) % mod,
    ifac[i] = ifac[i - 1] * inv[i] % mod;
}
int dp[35][N][N];
int solve(int a1) {
  memset(dp, 0, sizeof(dp)), dp[n + 2 - a1][0][0] = 1;
  int i = n + 1 - a1, t = 0;
  for (; i >= 1; --i, ++t) {
    ++__cc_state_visits;
if (__cc_state_visits == 101) {
std::cout << "{\"a1\":";
__cc_json(std::cout, a1);
std::cout << ",\"i\":";
__cc_json(std::cout, i);
std::cout << ",\"n\":";
__cc_json(std::cout, n);
std::cout << ",\"t\":";
__cc_json(std::cout, t);
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}


    for (int j = 0; j <= n; ++j) {
      for (int k = 0; k <= n; ++k)
        if (dp[i + 1][j][k]) {
          for (int c = 0; c * i + k <= a1 && c + j <= n; ++c) {
            add(dp[i][j + c][k + c * i], 1LL * dp[i + 1][j][k] * ifac[c] % mod);
          }
        }
    }
    if (i > 1)
      for (int j = 0; j <= t; ++j) memset(dp[i][j], 0, (n + 3) << 2);
  }
  int ans = 0;
  for (int i = 0; i < n; ++i)
    for (int j = 0; j <= a1; ++j)
      add(ans, 1LL * dp[1][i][j] * ifac[n - i] % mod);
  return fac[n] * ans % mod;
}
int main() {
  read(n, mod);
  init();
  int ans = 1;
  for (int x = std::max(1, n - 30); x <= n; ++x) add(ans, solve(x));
  printf("%d\n", ans);
  return 0;
}
