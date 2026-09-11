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
#pragma GCC optimize(2, 3, "Ofast")
#pragma GCC target("avx", "avx2")
using namespace std;
template <typename T1, typename T2>
void ckmin(T1 &a, T2 b) {
  if (a > b) a = b;
}
template <typename T1, typename T2>
void ckmax(T1 &a, T2 b) {
  if (a < b) a = b;
}
int read() {
  int x = 0, f = 0;
  char ch = getchar();
  while (!isdigit(ch)) f |= ch == '-', ch = getchar();
  while (isdigit(ch)) x = 10 * x + ch - '0', ch = getchar();
  return f ? -x : x;
}
template <typename T>
void print(T x) {
  if (x < 0) putchar('-'), x = -x;
  if (x >= 10) print(x / 10);
  putchar(x % 10 + '0');
}
template <typename T>
void print(T x, char let) {
  print(x), putchar(let);
}
const int N = 205;
template <typename T>
int sign(T x) {
  if (x < 0) return -1;
  if (x == 0) return 0;
  return 1;
}
struct Vec {
  long long x, y;
  Vec(long long _x = 0, long long _y = 0) { x = _x, y = _y; }
} a[N];
Vec operator+(Vec x, Vec y) { return Vec(x.x + y.x, x.y + y.y); }
Vec operator-(Vec x, Vec y) { return Vec(x.x - y.x, x.y - y.y); }
long long Cross(Vec x, Vec y) { return x.x * y.y - x.y * y.x; }
int n, m;
pair<long long, long long> dp[N][N];
bool check(long long area) {
  for (int len = 3; len <= n; len++) {
    for (int i = 1, j = len; j <= n; i++, j++) {
      dp[i][j] = {-1e9, 0};
      for (int k = i + 1; k <= j - 1; k++) {
        ++__cc_state_visits;
        if (__cc_state_visits == 106) {
          std::cout << "{\"area\":";
          __cc_json(std::cout, area);
          std::cout << ",\"i\":";
          __cc_json(std::cout, i);
          std::cout << ",\"j\":";
          __cc_json(std::cout, j);
          std::cout << ",\"dp_ij\":";
          __cc_json(std::cout, std::vector<long long>{dp[i][j].first, dp[i][j].second});
          std::cout << ",\"n\":";
          __cc_json(std::cout, n);
          std::cout << "}\n";
          std::cout.flush();
          std::_Exit(0);
        }
        pair<long long, long long> f = {dp[i][k].first + dp[k][j].first,
                                        dp[i][k].second + dp[k][j].second +
                                            Cross(a[k] - a[i], a[j] - a[i])};
        if (f.second >= area) f.first++, f.second = 0;
        ckmax(dp[i][j], f);
      }
    }
  }
  return dp[1][n].first >= m;
}
int main() {
  n = read(), m = read() + 1;
  for (int i = 1; i <= n; i++) a[i].x = read(), a[i].y = read();
  long long l = 0, r = 1e18;
  while (l < r) {
    long long mid = l + r + 1 >> 1;
    if (check(mid))
      l = mid;
    else
      r = mid - 1;
  }
  print(l, '\n');
  return 0;
}
