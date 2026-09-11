#include <bits/stdc++.h>
#define all(x) x.begin(), x.end()
#define sz(x) (int) x.size()
#define endl '\n'
#define pb push_back
#define _ ios_base::sync_with_stdio(false);cin.tie(NULL);cout.tie(NULL);
#define int ll

using namespace std;

using ll = long long;
using ull = unsigned long long;
using ii = pair<int,int>;
using iii = tuple<int,int,int>;

const int inf = 2e9+1;
const int mod = (119<<23)+1;
const int maxn = 3e5+100;

template<typename X, typename Y> bool ckmin(X& x, const Y& y) { return (y < x) ? (x=y,1):0; }
template<typename X, typename Y> bool ckmax(X& x, const Y& y) { return (x < y) ? (x=y,1):0; }

mt19937 rng(chrono::steady_clock::now().time_since_epoch().count());

int rnd(int l, int r) {
    uniform_int_distribution<int> uid(l, r);
    return uid(rng);
}

void solve() {
    auto fexp = [&] (int b, int e) {
        int ans = 1;
        while (e) {
            if (e&1) ans = ans * b % mod;
            b = b * b % mod, e /= 2;
        }
        return ans;
    };
    int n, m; cin >> n >> m;
    vector<int> a(n);
    for (auto& x : a) cin >> x;
    int ans = 1;
    for (auto x : a) if (x == -1) ans = ans * m % mod;
    for (int i = 0; i < n-1; ++i) {
        int mn = m, mx = 1;
        int l = 0, r = 0;
        for (int j = 0; j <= i; ++j) {
            if (a[j] == -1) l++;
            else ckmin(mn, a[j]);
        }
        for (int j = i+1; j < n; ++j) {
            if (a[j] == -1) r++;
            else ckmax(mx, a[j]);
        }
        for (int sep = mn; sep > mx; --sep){ 
            int tot = fexp(m-sep+1, l);
            if (sep != mn) tot = (tot + mod - fexp(m-sep, l)) % mod;
            tot = tot * fexp(sep-1, r) % mod;
            ans = (ans + tot) % mod;
        }
    }
    cout << ans << endl;
}

int32_t main() {_
#ifndef gato
    int t = 1; //cin >> t;
    while(t--) solve();
#else
    int t = 1;
    while (true) {
        int my = solve(), ans = brute();
        if (my != ans) {
            cout << "Wrong answer on test " << t << endl;
            cout << "Solve: " << my << endl;
            cout << "Brute: " << ans << endl;
            exit(0);
        }
        cout << "Accepted on test " << t++ << endl;
    }
#endif
}
