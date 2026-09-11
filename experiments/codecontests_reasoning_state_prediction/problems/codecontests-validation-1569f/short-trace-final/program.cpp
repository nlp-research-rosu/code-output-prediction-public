#include <bits/stdc++.h>
using namespace std;
int rev[1 << 20];
int dp[1 << 13][13][13];
int visit[1 << 13][13][13];
bool visit2[1 << 20];
int maps[13], c[13];
int a[13][13];
int n, m, r;
long long ans = 0;
int stage;
vector<pair<int, int> > v[1 << 13][13][13];
vector<int> edges[1 << 20];
long long A(int r, int g) {
  int ans = 1;
  for (int i = 1; i <= g; i++) ans *= (r - i + 1);
  return ans;
}
bool vis[1 << 20];
bool dfs2(int x, int y, int state) {
  if (state == (1 << n) - 1) {
    visit[state][x][y] = stage;
    return dp[state][x][y] = true;
  }
  if (visit[state][x][y] == stage) return false;
  for (int i = 0; i < v[state][x][y].size(); i++) {
    int p = v[state][x][y][i].first;
    int q = v[state][x][y][i].second;
    if (maps[p] == maps[q] && dfs2(p, q, state | (1 << p) | (1 << q))) {
      visit[state][x][y] = stage;
      return dp[state][x][y] = true;
    }
  }
  visit[state][x][y] = stage;
  return dp[state][x][y] = false;
}
bool check() {
  for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
      if (a[i][j] && maps[i] == maps[j] && dfs2(i, j, (1 << i) | (1 << j)))
        return true;
  return false;
}
int flag;
unordered_map<int, int> mp;
int get_state(int a[]) {
  int state = 0;
  for (int i = 0; i < n; i++) state = 6 * state + a[i] - 1;
  return state;
}
void decode_state(int maps[], int state) {
  for (int i = n - 1; i >= 0; i--) {
    maps[i] = state % 6 + 1;
    state /= 6;
  }
}
void dfs(int pos, int group) {
  stage++;
  if (group > min(6, r) || pos + flag > n) return;
  if (pos == n) {
    int id = get_state(maps);
    int sz = mp.size();
    mp[id] = sz;
    rev[sz] = id;
    if ((group == r || group * 2 == n) && check()) {
      vis[sz] = true;
    }
    return;
  }
  c[group + 1]++;
  flag++;
  maps[pos] = group + 1;
  dfs(pos + 1, group + 1);
  flag--;
  c[group + 1]--;
  for (int i = 1; i <= group; i++) {
    c[i]++;
    if (c[i] & 1)
      flag++;
    else
      flag--;
    maps[pos] = i;
    dfs(pos + 1, group);
    if (c[i] & 1)
      flag--;
    else
      flag++;
    c[i]--;
  }
}
int main() {
  scanf("%d%d%d", &n, &m, &r);
  while (m--) {
    int x, y;
    scanf("%d%d", &x, &y);
    x--, y--;
    a[x][y] = a[y][x] = 1;
  }
  for (int i = 0; i < (1 << n); i++) {
    int cnt = 0;
    for (int j = 0; j < n; j++)
      if (i & (1 << j)) cnt++;
    if (cnt & 1) continue;
    for (int j = 0; j < n; j++)
      for (int k = 0; k < n; k++)
        if ((i & (1 << j)) && (i & (1 << k)))
          for (int p = 0; p < n; p++)
            for (int q = 0; q < n; q++)
              if (a[j][p] && a[k][q] && p != q && !(i & (1 << p)) &&
                  !(i & (1 << q)))
                v[i][j][k].push_back(make_pair(p, q));
  }
  dfs(0, 0);
  for (unordered_map<int, int>::iterator it = mp.begin(); it != mp.end();
       it++) {
    decode_state(maps, it->first);
    int maps2[13];
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++)
        if (maps[i] != maps[j]) {
          for (int k = 0; k < n; k++) maps2[k] = maps[k];
          int id = min(maps[i], maps[j]);
          int id2 = max(maps[i], maps[j]);
          for (int k = 0; k < n; k++)
            if (maps[j] == maps[k]) maps2[k] = id;
          for (int k = 0; k < n; k++)
            if (maps2[k] > id2) maps2[k]--;
          int x = get_state(maps2);
          edges[it->second].push_back(mp[x]);
        }
    }
  }
  queue<int> q;
  for (int i = 0; i < mp.size(); i++) {
    if (vis[i]) q.push(i), visit2[i] = true;
  }
  while (!q.empty()) {
    int u = q.front();
    q.pop();
    decode_state(maps, rev[u]);
    int mx = 0;
    for (int i = 0; i < n; i++) mx = max(mx, maps[i]);
    ans += A(r, mx);
    for (int i = 0; i < edges[u].size(); i++) {
      int x = edges[u][i];
      if (visit2[x]) continue;
      q.push(x);
      visit2[x] = true;
    }
  }
  cout << ans << endl;
  return 0;
}
