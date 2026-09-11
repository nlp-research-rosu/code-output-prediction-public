#include <bits/stdc++.h>
#define rep(i, a, b) for (int i = a; i < (b); ++i)
#define all(x) begin(x), end(x)
#define sz(x) (int)(x).size()

using namespace std;
using ll = long long;
using pii = pair<int, int>;
using vi = vector<int>;
using vii = vector<pii>;
using vb = vector<bool>;
using vl = vector<ll>;

typedef complex<double> C;
typedef vector<double> vd;
void fft(vector<C>& a) {
  int n = sz(a), L = 31 - __builtin_clz(n);
  static vector<complex<long double>> R(2, 1);
  static vector<C> rt(2, 1);  // (^ 10% faster if double)
  for (static int k = 2; k < n; k *= 2) {
    R.resize(n);
    rt.resize(n);
    auto x = polar(1.0L, acos(-1.0L) / k);
    rep(i, k, 2 * k) rt[i] = R[i] = i & 1 ? R[i / 2] * x : R[i / 2];
  }
  vi rev(n);
  rep(i, 0, n) rev[i] = (rev[i / 2] | (i & 1) << L) / 2;
  rep(i, 0, n) if (i < rev[i]) swap(a[i], a[rev[i]]);
  for (int k = 1; k < n; k *= 2)
    for (int i = 0; i < n; i += 2 * k) rep(j, 0, k) {
        // C z = rt[j+k] * a[i+j+k]; // (25% faster if hand-rolled)  /// include-line
        auto x = (double*)&rt[j + k], y = (double*)&a[i + j + k];   /// exclude-line
        C z(x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]);  /// exclude-line
        a[i + j + k] = a[i + j] - z;
        a[i + j] += z;
      }
}

vl conv(const vl& a, const vl& b) {
  if (a.empty() || b.empty()) return {};
  vd res(sz(a) + sz(b) - 1);
  int L = 32 - __builtin_clz(sz(res)), n = 1 << L;
  vector<C> in(n), out(n);
  copy(all(a), begin(in));
  rep(i, 0, sz(b)) in[i].imag((double)b[i]);
  fft(in);
  for (C& x : in) x *= x;
  rep(i, 0, n) out[i] = in[-i & (n - 1)] - conj(in[i]);
  fft(out);
  rep(i, 0, sz(res)) res[i] = imag(out[i]) / (4 * n);

  vl ans(sz(res));
  rep(i, 0, sz(res)) ans[i] = (ll)(roundl(res[i]));
  return ans;
}

int main() {
  cin.tie(0)->sync_with_stdio(0);

  int n, x;
  cin >> n >> x;

  vl f(x + 1);
  vector<vi> indices(x + 1);
  rep(i, 0, n) {
    int y;
    cin >> y;
    f[y]++;
    indices[y].push_back(i + 1);
  }

  auto ff = conv(f, f);
  rep(i, 0, x + 1) if (i + i <= x) ff[2 * i] -= f[i];

  rep(i, 0, x + 1) {
    if (f[i] == 0 || ff[x - i] == 0) continue;
    if (2 * i <= x && f[i] == 1 && ff[x - i] == 2LL * f[x - 2 * i]) continue;

    rep(j, 0, x - i) {
      if (f[j] - (i == j) == 0) continue;
      int k = x - i - j;
      if (f[k] - (i == k) - (j == k) == 0) continue;

      vi ans = {indices[i][0], indices[j][(i == j)], indices[k][(i == k) + (j == k)]};
      sort(all(ans));
      cout << ans[0] << ' ' << ans[1] << ' ' << ans[2] << '\n';
      return 0;
    }
  }

  cout << -1 << '\n';
}
