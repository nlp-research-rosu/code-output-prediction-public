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
using std::pair;
using std::queue;
using std::set;
const int N = ((1 << 20) + 5);
int id[N], mx[N], tp;
set<pair<int, int> > st;
const int M = 100005;
struct edge {
  int nxt, to, fl, c;
} e[M];
queue<int> q;
int S, T, head[N], dis[N], pr[N], in[N], top = 1, ans;
inline void adde(int first, int second, int fl, int c) {
  e[++top] = edge{head[first], second, fl, c};
  head[first] = top;
}
inline void add(int first, int second, int fl, int c) {
  adde(first, second, fl, c);
  adde(second, first, 0, -c);
}
inline void spfa(void) {
  for (int i = 1; i <= tp; ++i) dis[id[i]] = -1;
  dis[S] = 0;
  q.push(S);
  in[S] = 1;
  while (!q.empty()) {
    int u = q.front();
    q.pop();
    in[u] = 0;
    for (int i = head[u]; i; i = e[i].nxt) {
    ++__cc_state_visits;
if (__cc_state_visits == 114) {
std::cout << "{\"ans\":";
__cc_json(std::cout, ans);
std::cout << ",\"q.size()\":";
__cc_json(std::cout, q.size());
std::cout << ",\"u\":";
__cc_json(std::cout, u);
std::cout << ",\"([&](){ std::vector<int> state; for (int x = 1; x <= tp; ++x) { state.push_back(dis[id[x]]); state.push_back(pr[id[x]]); } return state; })()\":";
__cc_json(std::cout, ([&](){ std::vector<int> state; for (int x = 1; x <= tp; ++x) { state.push_back(dis[id[x]]); state.push_back(pr[id[x]]); } return state; })());
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}


      int v = e[i].to;
      if (e[i].fl && dis[v] < dis[u] + e[i].c) {
        dis[v] = dis[u] + e[i].c;
        pr[v] = i ^ 1;
        if (!in[v]) q.push(v), in[v] = 1;
      }
    }
  }
}
int n, k, a[N], ok[N], is[N];
inline void ins(int s) {
  if (__builtin_popcount(s) & 1) {
    ok[s] = 1;
    add(S, s, 1, a[s]);
    for (int i = 0; i < n; ++i)
      if (ok[s ^ (1 << i)]) add(s, s ^ (1 << i), 1, 0);
  } else {
    ok[s] = 1;
    add(s, T, 1, a[s]);
    for (int i = 0; i < n; ++i)
      if (ok[s ^ (1 << i)]) add(s ^ (1 << i), s, 1, 0);
  }
  id[++tp] = s;
}
inline void rp(int first, bool fl = 1) {
  if (fl) {
    st.erase(std::make_pair(a[first] + a[mx[first]], first));
    if (!ok[first]) ins(first);
  }
  mx[first] = 1 << n;
  for (int i = 0; i < n; ++i)
    if (!is[first ^ (1 << i)] && a[first ^ (1 << i)] > a[mx[first]])
      mx[first] = first ^ (1 << i);
  st.insert(std::make_pair(a[first] + a[mx[first]], first));
}
inline void run(void) {
  spfa();
  if (!st.empty() && st.rbegin()->first > dis[T]) {
    int u = st.rbegin()->second;
    st.erase(prev(st.end()));
    if (!ok[u]) ins(u);
    if (!ok[mx[u]]) ins(mx[u]);
    spfa();
  }
  if (dis[T] == -1) return;
  int u = T, v = e[pr[T]].to;
  while (e[pr[u]].to != S) {
    ++e[pr[u]].fl;
    --e[pr[u] ^ 1].fl;
    u = e[pr[u]].to;
  }
  ++e[pr[u]].fl;
  --e[pr[u] ^ 1].fl;
  is[u] = is[v] = 1;
  ans += a[u] + a[v];
  st.erase(std::make_pair(a[u] + a[mx[u]], u));
  for (int i = 0; i < n; ++i)
    if (!is[v ^ (1 << i)]) {
      rp(v ^ (1 << i));
    }
  for (int i = 0; i < n; ++i)
    if (!ok[u ^ (1 << i)]) {
      ins(u ^ (1 << i));
    }
}
int main() {
  scanf("%d%d", &n, &k);
  S = 1 << n, T = S + 1;
  a[S] = -0x3f3f3f3f;
  id[1] = S, id[2] = T;
  tp = 2;
  for (int i = 0; i < (1 << n); ++i) scanf("%d", a + i);
  for (int s = 0; s < (1 << n); ++s) {
    if (__builtin_popcount(s) & 1) {
      rp(s, 0);
    }
  }
  while (k--) run();
  printf("%d\n", ans);
  return 0;
}
