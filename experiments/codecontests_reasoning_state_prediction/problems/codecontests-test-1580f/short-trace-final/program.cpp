#include <bits/stdc++.h>
using namespace std;
const int N = 280010;
const int mod = 998244353, gn = 3;
const int inf = 2147483647;
long long read() {
  long long x = 0, f = 1;
  char ch = getchar();
  while (ch < '0' || ch > '9') {
    if (ch == '-') f = -1;
    ch = getchar();
  }
  while (ch >= '0' && ch <= '9') x = x * 10ll + ch - '0', ch = getchar();
  return x * f;
}
void up(int& x, int y) {
  x += y;
  if (x >= mod) x -= mod;
}
int Pow(int x, int y) {
  if (!y) return 1;
  int t = Pow(x, y >> 1);
  t = (long long)t * t % mod;
  if (y & 1) t = (long long)t * x % mod;
  return t;
}
int n, m, ans;
struct Poly {
  int pw[2][N], rev[N];
  void pre() {
    for (int i = 1; i < N; i++)
      pw[0][i] = Pow(gn, (mod - 1) / (i << 1)),
      pw[1][i] = Pow(gn, mod - 1 - (mod - 1) / (i << 1));
  }
  void init(int n) {
    rev[0] = 0;
    for (int i = 1; i < n; i++)
      rev[i] = ((rev[i >> 1] >> 1) | ((i & 1) * (n >> 1)));
  }
  void print(vector<int> a) {
    for (int x : a) printf("%d ", x);
    puts("");
  }
  void NTT(vector<int>& a, int n, int o) {
    for (int i = 0; i < n; i++)
      if (i < rev[i]) swap(a[i], a[rev[i]]);
    for (int i = 1; i < n; i <<= 1) {
      int wn;
      if (o == 1)
        wn = pw[0][i];
      else
        wn = pw[1][i];
      for (int j = 0; j < n; j += (i << 1)) {
        int w = 1;
        for (int k = 0; k < i; k++) {
          int t = (long long)w * a[i + j + k] % mod;
          w = (long long)w * wn % mod;
          a[i + j + k] = (a[j + k] - t + mod) % mod;
          a[j + k] = (a[j + k] + t) % mod;
        }
      }
    }
    if (o == -1) {
      int INV = Pow(n, mod - 2);
      for (int i = 0; i <= n; i++) a[i] = (long long)a[i] * INV % mod;
    }
  }
  vector<int> Inv(vector<int> a, int deg) {
    if (deg == 1) {
      vector<int> b(1);
      b[0] = Pow(a[0], mod - 2);
      return b;
    }
    vector<int> b = Inv(a, (deg + 1) >> 1);
    int n = 1;
    while (n <= (deg << 1)) n <<= 1;
    init(n);
    a.resize(n), b.resize(n);
    vector<int> c(n);
    for (int i = 0; i < n; i++) c[i] = (i < deg ? a[i] : 0);
    NTT(b, n, 1), NTT(c, n, 1);
    for (int i = 0; i < n; i++)
      b[i] = (2ll - (long long)c[i] * b[i] % mod + mod) % mod * b[i] % mod;
    NTT(b, n, -1);
    b.resize(deg);
    return b;
  }
  vector<int> solve(int m) {
    if (!m) {
      vector<int> t(n + 1);
      t[0] = 1;
      return t;
    }
    vector<int> A = solve(m >> 1), B(n + 1);
    A[1] = (m + 1) / 2;
    for (int i = 0; i <= n; i += 2) B[i] = A[i], A[i] = 0;
    vector<int> InvA(n + 1);
    for (int i = 1; i <= n; i++) InvA[i] = (mod - A[i]) % mod;
    InvA[0] = 1;
    InvA = Inv(InvA, n + 1);
    int tmp = ans;
    ans = InvA[n];
    if (!(n & 1)) up(ans, 2 * tmp % mod);
    for (int i = 3; i <= n; i += 2)
      up(ans, (long long)A[i] * InvA[n - i] % mod * (i - 1) % mod);
    int len = 1;
    while (len <= n * 3 + 1) len <<= 1;
    init(len);
    B.resize(len);
    InvA.resize(len);
    NTT(B, len, 1), NTT(InvA, len, 1);
    for (int i = 0; i <= len; i++)
      B[i] = (long long)B[i] * B[i] % mod * InvA[i] % mod;
    NTT(B, len, -1);
    for (int i = 0; i <= n; i++) up(A[i], B[i]);
    A.resize(n + 1);
    return A;
  }
} Poly;
int main() {
  Poly.pre();
  n = read(), m = read();
  Poly.solve(m);
  printf("%d\n", ans);
  return 0;
}
