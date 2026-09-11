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
long long mod = 998244353;
long double pi = 3.141592653589793238;
void pls() {
  ios_base::sync_with_stdio(0);
  cin.tie(0);
  cout.tie(0);
}
int dp[(1 << 23)];
int arr[23][26];
int mul(long long a, long long b) { return (a % mod * b % mod) % mod; }
void solve() {
  {
    int n;
    cin >> n;
    for (int i = 0; i < n; i++) {
      string s;
      cin >> s;
      for (int j = 0; j < s.size(); j++) arr[i][(s[j] - 'a')]++;
    }
    int cur[26];
    for (int i = 1; i < (1 << n); i++) {
      for (int k = 0; k < 26; k++) cur[k] = INT_MAX;
      int bit = 0;
      for (int j = 0; j < n; j++) {
    ++__cc_state_visits;
if (__cc_state_visits == 101) {
std::cout << "{\"bit\":";
__cc_json(std::cout, bit);
std::cout << ",\"cur[0]\":";
__cc_json(std::cout, cur[0]);
std::cout << ",\"cur[25]\":";
__cc_json(std::cout, cur[25]);
std::cout << ",\"i\":";
__cc_json(std::cout, i);
std::cout << ",\"n\":";
__cc_json(std::cout, n);
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}


        if (i & (1 << j)) {
          for (int k = 0; k < 26; k++) cur[k] = min(cur[k], arr[j][k]);
          bit++;
        }
      }
      int ans = 1;
      for (int i = 0; i < 26; i++) ans = mul(ans, cur[i] + 1);
      if (bit & 1)
        dp[i] = ans;
      else
        dp[i] = (mod - ans) % mod;
    }
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < (1 << n); j++) {
        if (j & (1 << i)) {
          {
            dp[j] += dp[j ^ (1 << i)];
            dp[j] %= mod;
          }
        }
      }
    }
    long long res = 0;
    for (int i = 0; i < (1 << n); i++) {
      long long cur = 0;
      long long kk = 0;
      long long sum = 0;
      for (int j = 0; j < n; j++)
        if (i & (1 << j)) kk++, sum += (j + 1);
      cur = dp[i] * kk * sum;
      res = res ^ cur;
    }
    cout << res << "\n";
  }
}
int main() {
  pls();
  solve();
  return 0;
}
