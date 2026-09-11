#ifndef U
#pragma GCC optimize("Ofast,unroll-loops")
#endif
#include <bits/stdc++.h>
using namespace std;

#define int long long
#define rep(i, a, b) for (int i = a; i < (b); ++i)
#define all(x) begin(x), end(x)
#define sz(x) (int) (x).size()
#define eb emplace_back
#define pb push_back
#define vc vector
#define fs first
#define sd second
typedef pair<int, int> pii;
typedef vc<int> vi;

int chmin(auto &u, auto v) { return u > v ? u = v, 1 : 0; }
int chmax(auto &u, auto v) { return u < v ? u = v, 1 : 0; }

signed main() {
  cin.tie(0)->sync_with_stdio(0);
  cin.exceptions(cin.failbit);

  // two sets (0->1, 1->0), also 1->0->1
  //
  // brute force quantity to do 1->0->1
  //
  // subtract from remaining, add cost of operation

  int N;
  cin >> N;

  vi A(N);
  for (auto &e : A) cin >> e;

  vi B(N);
  for (auto &e : B) cin >> e;

  vi C(N);
  for (auto &e : C) cin >> e;

  vi order(N);
  iota(all(order), 0);
  sort(all(order), [&](int a, int b) -> bool { return C[a] > C[b]; });

  int sum1 = 0, sum2 = 0;
  rep(i, 0, N) {
    sum1 += A[i] * C[i];
    sum2 += B[i] * C[i];
  }
  vi ps1(N + 1), ps2(N + 1);
  ps1[0] = ps2[0] = 0;
  rep(i, 0, N) {
    ps1[i + 1] = ps1[i] + A[order[i]] * (1 - B[order[i]]);
    ps2[i + 1] = ps2[i] + B[order[i]] * (1 - A[order[i]]);
  }
  int cost = 0;
  rep(i, 0, N) {
    if (A[order[i]] == 1 and B[order[i]] == 0) {
      cost += sum1;
      cost -= C[order[i]] * (ps1[N] - ps1[i]);
    }
    if (B[order[i]] == 1 and A[order[i]] == 0) {
      cost += sum2;
      cost -= C[order[i]] * (ps2[N] - ps2[i + 1]);
    }
  }
  int ans = cost;
  rep(i, 0, N) {
    if (A[order[i]] == 1) {
      sum1 -= C[order[i]];
    }
    if (A[order[i]] == 1 and B[order[i]] == 1) {
      cost += sum1;
      cost -= C[order[i]] * (ps1[N] - ps1[i + 1]);
      cost += sum2;
      cost -= C[order[i]] * (ps2[N] - ps2[i + 1]);
      chmin(ans, cost);
    }
    if (B[order[i]] == 1) {
      sum2 -= C[order[i]];
    }
  }
  cout << ans << '\n';
}
