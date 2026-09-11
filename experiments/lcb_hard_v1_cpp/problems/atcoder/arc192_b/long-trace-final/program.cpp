#include <bits/stdc++.h>

using namespace std;

int main() {
  cin.tie(0)->sync_with_stdio(0);

  int N;
  cin >> N;

  vector<int> A(N);
  for (auto &e : A) cin >> e;

  int p = 0, P[2] = {0};
  for (auto e : A) {
    (p += e - 1) %= 2;
    P[e % 2]++;
  }
  if (N % 2 == 0) {
    cout << (p == 0 or P[0] == P[1] ? "Snuke" : "Fennec");
  } else {
    cout << (p == 0 or (P[0] + 1 == P[1] and N < 7) or
                     (P[1] + 1 == P[0] and N < 5)
                 ? "Fennec"
                 : "Snuke");
  }
}
