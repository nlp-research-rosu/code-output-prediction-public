#include<bits/stdc++.h>


#include <algorithm>
#include <array>
#include <cstdlib>
#include <deque>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <type_traits>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
static long long _lcb_count = 0;
static void _lcb_json_string(std::ostream& out, const std::string& value) {
    out << '"';
    for (unsigned char character : value) {
        switch (character) {
        case '"': out << "\\\""; break;
        case '\\': out << "\\\\"; break;
        case '\b': out << "\\b"; break;
        case '\f': out << "\\f"; break;
        case '\n': out << "\\n"; break;
        case '\r': out << "\\r"; break;
        case '\t': out << "\\t"; break;
        default:
            if (character < 0x20) {
                out << "\\u00" << std::hex << std::setw(2)
                    << std::setfill('0') << static_cast<int>(character)
                    << std::dec << std::setfill(' ');
            } else {
                out << static_cast<char>(character);
            }
        }
    }
    out << '"';
}
static void _lcb_json(std::ostream& out, const std::string& value) {
    _lcb_json_string(out, value);
}
static void _lcb_json(std::ostream& out, const char* value) {
    _lcb_json_string(out, value);
}
static void _lcb_json(std::ostream& out, char value) {
    _lcb_json_string(out, std::string(1, value));
}
static void _lcb_json(std::ostream& out, bool value) {
    out << (value ? "true" : "false");
}
template <class T>
static std::enable_if_t<std::is_integral_v<T> && !std::is_same_v<T, bool>>
_lcb_json(std::ostream& out, T value) {
    out << value;
}
template <class T>
static std::enable_if_t<std::is_floating_point_v<T>>
_lcb_json(std::ostream& out, T value) {
    out << std::setprecision(17) << value;
}
template <class First, class Second>
static void _lcb_json(std::ostream& out, const std::pair<First, Second>& value) {
    out << '[';
    _lcb_json(out, value.first);
    out << ',';
    _lcb_json(out, value.second);
    out << ']';
}
template <class Range>
static void _lcb_json_range(std::ostream& out, const Range& values) {
    out << '[';
    bool first = true;
    for (const auto& value : values) {
        if (!first) out << ',';
        first = false;
        _lcb_json(out, value);
    }
    out << ']';
}
template <class T, class Allocator>
static void _lcb_json(std::ostream& out, const std::vector<T, Allocator>& value) {
    _lcb_json_range(out, value);
}
template <class T, std::size_t Size>
static void _lcb_json(std::ostream& out, const std::array<T, Size>& value) {
    _lcb_json_range(out, value);
}
template <class T, class Allocator>
static void _lcb_json(std::ostream& out, const std::deque<T, Allocator>& value) {
    _lcb_json_range(out, value);
}
template <class Key, class Compare, class Allocator>
static void _lcb_json(std::ostream& out, const std::set<Key, Compare, Allocator>& value) {
    _lcb_json_range(out, value);
}
template <class Key, class Hash, class Equal, class Allocator>
static void _lcb_json(std::ostream& out, const std::unordered_set<Key, Hash, Equal, Allocator>& value) {
    std::vector<Key> ordered(value.begin(), value.end());
    std::sort(ordered.begin(), ordered.end());
    _lcb_json_range(out, ordered);
}
template <class Key, class Value, class Compare, class Allocator>
static void _lcb_json(std::ostream& out, const std::map<Key, Value, Compare, Allocator>& value) {
    _lcb_json_range(out, value);
}
template <class Key, class Value, class Hash, class Equal, class Allocator>
static void _lcb_json(std::ostream& out, const std::unordered_map<Key, Value, Hash, Equal, Allocator>& value) {
    std::vector<std::pair<Key, Value>> ordered(value.begin(), value.end());
    std::sort(ordered.begin(), ordered.end());
    _lcb_json_range(out, ordered);
}

const int N=2e5+10,MOD=998244353;
int siz[N],sum[N],val[N];
struct block{
	int sum,siz,rt;
	bool operator<(const block& b)const{
		return 1ll*sum*b.siz<1ll*b.sum*siz;
	}
};
int pa[N],sz[N];
std::priority_queue<block> q;
int p[N],a[N];
int findp(int x){
	if(x==pa[x]) return x;
	return pa[x]=findp(pa[x]);
}
int qpow(int a,int b){
	int ret=1;
	while(b){
		if(b&1) ret=1ll*ret*a%MOD;
		a=1ll*a*a%MOD;b>>=1;
	}
	return ret;
}
int main(){
	int T;scanf("%d",&T);
	while(T--){
		int n,S=0;scanf("%d",&n);
		for(int i=1;i<=n;i++)
			scanf("%d",p+i);
		for(int i=1;i<=n;i++)
			scanf("%d",a+i),S+=a[i];
		std::copy(a,a+n+1,sum);
		std::fill(siz,siz+n+1,1);siz[0]=0;
		std::iota(pa,pa+n+1,0);
		std::fill(sz,sz+n+1,1);
		std::copy(a,a+n+1,val);
		for(int i=0;i<=n;i++) q.push({sum[i],siz[i],i});
		while(!q.empty()){
++_lcb_count;

			block qt=q.top();int u=qt.rt;q.pop();
			if(!u||siz[u]!=qt.siz) continue;
			int f=findp(p[u]);pa[u]=f;
			val[f]=((val[f]+val[u])%MOD+1ll*siz[f]*sum[u]%MOD)%MOD;
			siz[f]+=siz[u];sum[f]+=sum[u];
			q.push({sum[f],siz[f],f});
		}
if (_lcb_count > 1000) {
std::cout << "{\"S\":";
_lcb_json(std::cout, S);
std::cout << ",\"n\":";
_lcb_json(std::cout, n);
std::cout << ",\"q.size()\":";
_lcb_json(std::cout, q.size());
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}

		int ans=1ll*val[0]*qpow(S,MOD-2)%MOD;
		printf("%d\n",ans);
	}
}
