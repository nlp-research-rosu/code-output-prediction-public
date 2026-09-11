#include<iostream>
#include<algorithm>
#include<set>
using namespace std;

int n, a[300005], b[300005];
multiset<int> ms[4];
long long ans;

int main() {
	scanf("%d", &n);
	for (int i = 0; i < n; i++) {
		scanf("%d", &a[i]);
		b[i] = a[i];
	}
	
	if (n % 2 == 0) {
		sort(b, b + n);
		for (int i = 0; i < n / 2; i++) {
			ans -= b[i];
		}
		for (int i = n / 2; i < n; i++) {
			ans += b[i];
		}
	} else {
		long long pl = 0;
		long long mi = 0;
		sort(b + 1, b + n);
		for (int i = 1; i < (n + 1) / 2; i++) {
			mi += b[i];
			ms[2].insert(b[i]);
		}
		for (int i = (n + 1) / 2; i < n; i++) {
			pl += b[i];
			ms[3].insert(b[i]);
		}
		ans = pl - mi;

		for (int i = 0; i + 2 < n; i += 2) {
			ms[0].insert(a[i]);
			ms[0].insert(a[i + 1]);
			mi += a[i] + a[i + 1];
			
			{
				auto x = ms[0].end();
				x--;
				int y = *x;
				mi -= y;
				pl += y;
				ms[1].insert(y);
				ms[0].erase(x);
			}
			
			{
				auto u = ms[0].end();
				u--;
				auto v = ms[1].begin();
				int x = *u;
				int y = *v;
				if (x > y) {
					ms[0].erase(u);
					ms[1].erase(v);
					ms[0].insert(y);
					ms[1].insert(x);
					mi += y - x;
					pl += x - y;
				}
			}
			
			if (ms[2].find(a[i + 1]) != ms[2].end()) {
				ms[2].erase(ms[2].lower_bound(a[i + 1]));
				mi -= a[i + 1];
			} else {
				ms[3].erase(ms[3].lower_bound(a[i + 1]));
				pl -= a[i + 1];
			}
			
			if (ms[2].find(a[i + 2]) != ms[2].end()) {
				ms[2].erase(ms[2].find(a[i + 2]));
				mi -= a[i + 2];
			} else {
				ms[3].erase(ms[3].find(a[i + 2]));
				pl -= a[i + 2];
			}
			
			if (ms[2].size() < ms[3].size()) {
				auto x = ms[3].begin();
				mi += *x;
				pl -= *x;
				ms[2].insert(*x);
				ms[3].erase(x);
			} else if (ms[2].size() > ms[3].size()) {
				auto x = ms[2].end();
				x--;
				mi -= *x;
				pl += *x;
				ms[3].insert(*x);
				ms[2].erase(x);
			}

			ans = max(ans, pl - mi);
		}
	}
	
	printf("%lld\n", ans);
	
	return 0;
}
