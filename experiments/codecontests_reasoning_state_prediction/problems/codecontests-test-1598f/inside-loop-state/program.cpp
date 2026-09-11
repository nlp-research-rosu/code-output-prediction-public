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
struct custom_hash {
  static uint64_t splitmix64(uint64_t x) {
    x += 0x9e3779b97f4a7c15;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9;
    x = (x ^ (x >> 27)) * 0x94d049bb133111eb;
    return x ^ (x >> 31);
  }
  size_t operator()(uint64_t x) const {
    static const uint64_t FIXED_RANDOM =
        chrono::steady_clock::now().time_since_epoch().count();
    return splitmix64(x + FIXED_RANDOM);
  }
};
int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n;
  cin >> n;
  vector<int> mn(n), tot(n), dp(1 << n, -1e9);
  vector<unordered_map<int, int, custom_hash>> cnt(n);
  for (int i = 0; i < n; i++) {
    string s;
    cin >> s;
    int cur = 0;
    for (auto c : s) {
      cur += (c == '(' ? 1 : -1);
      if (cur <= mn[i]) {
        mn[i] = cur;
        cnt[i][cur]++;
      }
      tot[i] = cur;
    }
  }
  dp[0] = 0;
  int ans = 0;
  for (int mask = 0; mask < (1 << n); mask++) {
    int sum = 0;
    for (int i = 0; i < n; i++) {
    ++__cc_state_visits;
if (__cc_state_visits == 101) {
std::cout << "{\"ans\":";
__cc_json(std::cout, ans);
std::cout << ",\"dp[mask]\":";
__cc_json(std::cout, dp[mask]);
std::cout << ",\"mask\":";
__cc_json(std::cout, mask);
std::cout << ",\"n\":";
__cc_json(std::cout, n);
std::cout << ",\"sum\":";
__cc_json(std::cout, sum);
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}


      if (mask >> i & 1) sum += tot[i];
    }
    for (int i = 0; i < n; i++) {
      if (!(mask >> i & 1)) {
        ans = max(ans, dp[mask] + cnt[i][-sum]);
        if (sum + mn[i] >= 0)
          dp[mask | (1 << i)] =
              max(dp[mask | (1 << i)], dp[mask] + cnt[i][-sum]);
      }
    }
  }
  cout << ans << endl;
}
