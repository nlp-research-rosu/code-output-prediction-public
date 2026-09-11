#include <atcoder/all>
#include <iostream>
#include <memory>

using namespace atcoder;
using namespace std;

using mint = modint998244353;
using vm = vector<mint>;
using v2m = vector<vm>;
using v3m = vector<v2m>;

#define vm(n, i) vm(n, i)
#define v2m(n, m, i) v2m(n, vm(m, i))
#define v3m(n, m, k, i) v3m(n, v2m(m, k, i))

struct state {
  shared_ptr<v3m> _xxx;
  shared_ptr<v3m> _xxy;
  shared_ptr<v3m> _xyx;
  shared_ptr<v3m> _yxx;

  state(int n) {
    this->_xxx = make_shared<v3m>(v3m(n, n, n, 0));
    this->_xxy = make_shared<v3m>(v3m(n, n, n, 0));
    this->_xyx = make_shared<v3m>(v3m(n, n, n, 0));
    this->_yxx = make_shared<v3m>(v3m(n, n, n, 0));
  }

  mint& xxx(int a, int b, int c) { return (*_xxx)[a][b][c]; }
  mint& xxy(int a, int b, int c) { return (*_xxy)[a][b][c]; }
  mint& xyx(int a, int b, int c) { return (*_xyx)[a][b][c]; }
  mint& yxx(int a, int b, int c) { return (*_yxx)[a][b][c]; }
};

int main() {
  int n, k;
  cin >> n >> k;

  string s;
  cin >> s;

  state dp(1);
  dp.xxx(0, 0, 0) = 1;
  for (int i = 1; i <= n; i++) {
    char ch = s[i - 1];
    state dp0(i + 1);

    for (int a = 0; a < i; a++) {
      for (int b = 0; b < i; b++) {
        for (int c = 0; c < i; c++) {
          if (ch == 'A' || ch == '?') {
            dp0.xxy(a + 1, b, c) += dp.xxx(a, b, c);
            dp0.xxx(a, b, c) += dp.xxy(a, b, c);
            dp0.yxx(a, b, c + 1) += dp.xyx(a, b, c);
            dp0.xyx(a, b + 1, c) += dp.yxx(a, b, c);
          }

          if (ch == 'B' || ch == '?') {
            dp0.xyx(a, b + 1, c) += dp.xxx(a, b, c);
            dp0.yxx(a, b, c + 1) += dp.xxy(a, b, c);
            dp0.xxx(a, b, c) += dp.xyx(a, b, c);
            dp0.xxy(a + 1, b, c) += dp.yxx(a, b, c);
          }

          if (ch == 'C' || ch == '?') {
            dp0.yxx(a, b, c + 1) += dp.xxx(a, b, c);
            dp0.xyx(a, b + 1, c) += dp.xxy(a, b, c);
            dp0.xxy(a + 1, b, c) += dp.xyx(a, b, c);
            dp0.xxx(a, b, c) += dp.yxx(a, b, c);
          }
        }
      }
    }
    dp = dp0;
  }

  mint ans = 0;
  for (int a = 0; a <= n; a++) {
    for (int b = 0; b <= n; b++) {
      for (int c = 0; c <= n; c++) {
        int d = n + 1 - (a + b + c);
        int aa = a * (a - 1) / 2;
        int bb = b * (b - 1) / 2;
        int cc = c * (c - 1) / 2;
        int dd = d * (d - 1) / 2;
        if (aa + bb + cc + dd >= k) {
          ans += dp.xxx(a, b, c);
          ans += dp.xxy(a, b, c);
          ans += dp.xyx(a, b, c);
          ans += dp.yxx(a, b, c);
        }
      }
    }
  }
  cout << ans.val() << endl;

  return 0;
}
