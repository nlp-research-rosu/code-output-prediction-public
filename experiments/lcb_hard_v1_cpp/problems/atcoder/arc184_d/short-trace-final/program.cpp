#include<bits/stdc++.h>

#define nl '\n'
#define ll long long
#define all(x) (x).begin(), (x).end()
#define rall(x) (x).rbegin(), (x).rend()
#define pb push_back
#define eb emplace_back
#define fi first
#define sc second

#define pii pair<int, int>
#define pll pair<ll, ll>
template<typename T> bool chkmin(T &a, T b){return (b < a) ? a = b, 1 : 0;}
template<typename T> bool chkmax(T &a, T b){return (b > a) ? a = b, 1 : 0;}
using namespace std;
using ld = long double;
const int N = 1e6 + 100;
const ll inf = 1e18;
const ll mod = 998244353;

void Add(ll &x, ll y) {
    x = (x + y) % mod;
}

void solve() {
    int n;
    cin >> n;
    vector<pii> vals(n);
    for (int i = 0; i < n; i++) {
        cin >> vals[i].fi >> vals[i].sc;
    }
    sort(all(vals));
    vector<ll> dp(n + 5, 0);
    vector<int> a(n + 2);
    a[0] = n + 1;
    a[n + 1] = 0;
    for (int i = 1; i <= n; i++) {
        a[i] = vals[i - 1].sc;
    }
    dp[0] = 1;
    // for (int i = 0; i <= n + 1; i++) cerr << a[i] << ' ' ; cerr << nl;
    auto valid = [&](int l, int r, int dw, int up) -> bool {
        if (l > r) return 1;
        vector<int> maybe;
        for (int i = l; i <= r; i++) {
            if (a[i] > dw && a[i] < up) {
                maybe.pb(a[i]);
            }
        }
        vector<int> ok(maybe.size(), 0);
        int mn = n + 1;
        for (int i = 0; i < maybe.size(); i++) {
            int nw = maybe[i];
            if (mn < nw) {
                ok[i] = 1;
            } else {
                mn = nw;
            }
        }
        int mx = -1;
        for (int i = maybe.size() - 1; i >= 0; i--) {
            int nw = maybe[i];
            if (mx > nw) {
                ok[i] = 1;
            } else {
                mx = nw;
            }
        }
        // if (ok.size()) cerr << "???" << l << ' ' << r << ' ' << dw << ' ' << up << ' ' << ok[0] << nl;
        return accumulate(all(ok), 0) == maybe.size();
    };
    for (int i = 1; i <= n + 1; i++) {
        for (int j = 0; j < i; j++) {
            if (a[i] < a[j] && valid(j + 1, i - 1, a[i], a[j])) {
                Add(dp[i], dp[j]);
                // cerr << "!!" << j << "->" << i << nl;
            }
        }
        // cerr << "dp" << i << '=' << dp[i] << nl;
    }
    cout << dp[n + 1] << nl;
}

signed main() {
    ios::sync_with_stdio(0);
    cin.tie(0);
    // int tt = 1;
    // cin >> tt;
    // while(tt--)
        solve();
    return 0;
}
