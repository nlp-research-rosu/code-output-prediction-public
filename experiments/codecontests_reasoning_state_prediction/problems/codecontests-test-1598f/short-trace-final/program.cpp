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
