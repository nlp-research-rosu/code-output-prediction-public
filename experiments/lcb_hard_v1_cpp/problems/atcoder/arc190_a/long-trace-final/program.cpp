// competitive-verifier: PROBLEM
#ifdef ATCODER
#pragma GCC target("sse4.2,avx512f,avx512dq,avx512ifma,avx512cd,avx512bw,avx512vl,bmi2")
#endif
#pragma GCC optimize("Ofast,fast-math,unroll-all-loops")
#include <bits/stdc++.h>
#ifndef ATCODER

#endif
template <class T, class U>
constexpr bool chmax(T &a, const U &b) {
    return a < (T)b ? a = (T)b, true : false;
}
template <class T, class U>
constexpr bool chmin(T &a, const U &b) {
    return (T)b < a ? a = (T)b, true : false;
}
constexpr std::int64_t INF = 1000000000000000003;
constexpr int Inf = 1000000003;
constexpr double EPS = 1e-7;
constexpr double PI = 3.14159265358979323846;
#define FOR(i, m, n) for (int i = (m); i < int(n); ++i)
#define FORR(i, m, n) for (int i = (m)-1; i >= int(n); --i)
#define FORL(i, m, n) for (int64_t i = (m); i < int64_t(n); ++i)
#define rep(i, n) FOR (i, 0, n)
#define repn(i, n) FOR (i, 1, n + 1)
#define repr(i, n) FORR (i, n, 0)
#define repnr(i, n) FORR (i, n + 1, 1)
#define all(s) (s).begin(), (s).end()
struct Sonic {
    Sonic() {
        std::ios::sync_with_stdio(false);
        std::cin.tie(nullptr);
        std::cout << std::fixed << std::setprecision(20);
    }
    constexpr void operator()() const {}
} sonic;
using namespace std;
using ll = std::int64_t;
using ld = long double;
template <class T, class U>
std::istream &operator>>(std::istream &is, std::pair<T, U> &p) {
    return is >> p.first >> p.second;
}
template <class T>
std::istream &operator>>(std::istream &is, std::vector<T> &v) {
    for (T &i : v) is >> i;
    return is;
}
template <class T, class U>
std::ostream &operator<<(std::ostream &os, const std::pair<T, U> &p) {
    return os << '(' << p.first << ',' << p.second << ')';
}
template <class T>
std::ostream &operator<<(std::ostream &os, const std::vector<T> &v) {
    for (auto it = v.begin(); it != v.end(); ++it) os << (it == v.begin() ? "" : " ") << *it;
    return os;
}
template <class Head, class... Tail>
void co(Head &&head, Tail &&...tail) {
    if constexpr (sizeof...(tail) == 0) std::cout << head << '\n';
    else std::cout << head << ' ', co(std::forward<Tail>(tail)...);
}
template <class Head, class... Tail>
void ce(Head &&head, Tail &&...tail) {
    if constexpr (sizeof...(tail) == 0) std::cerr << head << '\n';
    else std::cerr << head << ' ', ce(std::forward<Tail>(tail)...);
}
void Yes(bool is_correct = true) { std::cout << (is_correct ? "Yes\n" : "No\n"); }
void No(bool is_not_correct = true) { Yes(!is_not_correct); }
void YES(bool is_correct = true) { std::cout << (is_correct ? "YES\n" : "NO\n"); }
void NO(bool is_not_correct = true) { YES(!is_not_correct); }
void Takahashi(bool is_correct = true) { std::cout << (is_correct ? "Takahashi" : "Aoki") << '\n'; }
void Aoki(bool is_not_correct = true) { Takahashi(!is_not_correct); }
int main(void) {
    int n, m;
    cin >> n >> m;
    vector<int> l(m), r(m);
    rep (i, m) cin >> l[i] >> r[i];
    vector<int> ans(m);
    bool f = false;
    {
        rep (i, m) {
            if (l[i] == 1 && r[i] == n) {
                f = true;
                ans[i] = 1;
                break;
            }
        }
        if (f) {
            co(1);
            co(ans);
            return 0;
        }
    }
    if (m == 1) {
        co(-1);
        return 0;
    }
    {
        vector<int> ord(m);
        iota(all(ord), 0);
        sort(all(ord), [&](int x, int y) {
            if (l[x] == l[y])
                return r[x] > r[y];
            return l[x] < l[y];
        });
        int minR = Inf, maxR = 0;
        int minIdx = -1, maxIdx = -1;
        for (int i : ord) {
            if (minR < l[i]) {
                f = true;
                ans[minIdx] = 2;
                ans[i] = 2;
                break;
            }
            if (r[i] <= maxR) {
                f = true;
                ans[maxIdx] = 1;
                ans[i] = 2;
                break;
            }
            if (chmin(minR, r[i]))
                minIdx = i;
            if (chmax(maxR, r[i]))
                maxIdx = i;
        }
        if (f) {
            co(2);
            co(ans);
            return 0;
        }
    }
    {
        int maxR = 0, minL = Inf;
        int maxIdx = -1, minIdx = -1;
        rep (i, m) {
            if (l[i] == 1 && chmax(maxR, r[i]))
                maxIdx = i;
            if (r[i] == n && chmin(minL, l[i]))
                minIdx = i;
        }
        if (minIdx != -1 && maxIdx != -1 && maxR + 1 >= minL) {
            ans[minIdx] = 1;
            ans[maxIdx] = 1;
            co(2);
            co(ans);
            return 0;
        }
    }
    if (m == 2) {
        co(-1);
        return 0;
    }
    {
        int maxR = 0, minL = Inf;
        int maxIdx = -1, minIdx = -1;
        rep (i, m) {
            if (chmax(maxR, r[i]))
                maxIdx = i;
            if (chmin(minL, l[i]))
                minIdx = i;
        }
        rep (i, m) {
            if (minIdx != i && maxIdx != i && minL <= l[i] && r[i] <= maxR) {
                f = true;
                ans[minIdx] = 1;
                ans[maxIdx] = 1;
                ans[i] = 2;
                break;
            }
        }
        if (f) {
            co(3);
            co(ans);
            return 0;
        }
    }
    {
        int minR = Inf, maxL = 0;
        int minIdx = -1, maxIdx = -1;
        rep (i, m) {
            if (chmin(minR, r[i]))
                minIdx = i;
            if (chmax(maxL, l[i]))
                maxIdx = i;
        }
        rep (i, m) {
            if (minIdx != i && maxIdx != i && l[i] <= maxL && minR <= r[i]) {
                f = true;
                ans[minIdx] = 2;
                ans[maxIdx] = 2;
                ans[i] = 1;
                break;
            }
        }
        if (f) {
            co(3);
            co(ans);
            return 0;
        }
    }
    co(-1);
    return 0;
}
