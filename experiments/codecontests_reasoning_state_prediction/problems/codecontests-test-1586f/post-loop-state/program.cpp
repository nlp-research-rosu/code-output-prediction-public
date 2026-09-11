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
const int sz = 1005;
int ans, g[sz][sz];
void fnc(vector<int> a, vector<int> b) {
  for (int x : a) {
    ++__cc_state_visits;


    for (int y : b) {
      g[x][y] = g[y][x] = ans;
    }
  }
if (__cc_state_visits >= 101) {
std::cout << "{\"a.size()\":";
__cc_json(std::cout, a.size());
std::cout << ",\"ans\":";
__cc_json(std::cout, ans);
std::cout << ",\"b.size()\":";
__cc_json(std::cout, b.size());
std::cout << ",\"g[a.front()][b.front()]\":";
__cc_json(std::cout, g[a.front()][b.front()]);
std::cout << ",\"g[a.back()][b.back()]\":";
__cc_json(std::cout, g[a.back()][b.back()]);
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}

}
int main() {
  int n, k;
  cin >> n >> k;
  vector<vector<int>> a;
  for (int i = 1; i <= n; i++) a.push_back({i});
  while (a.size() > 1) {
    ans++;
    int z = a.size();
    vector<vector<int>> b;
    for (int l = 0; l < z; l += k) {
      int r = min(z, l + k);
      for (int i = l; i < r; i++) {
        for (int j = i + 1; j < r; j++) {
          fnc(a[i], a[j]);
        }
      }
      vector<int> now;
      for (int i = l; i < r; i++) {
        for (int x : a[i]) now.push_back(x);
      }
      b.push_back(now);
    }
    a = b;
  }
  printf("%d\n", ans);
  for (int i = 1; i <= n; i++) {
    for (int j = i + 1; j <= n; j++) {
      printf("%d ", g[i][j]);
    }
  }
}
