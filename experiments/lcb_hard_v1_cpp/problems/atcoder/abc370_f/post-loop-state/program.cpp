#include <bits/stdc++.h>


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

using namespace std;
typedef long long ll;
const int INF=0x3f3f3f3f;
const int MAX=4e5+10;
int a[MAX],n,k;
ll bit[MAX];
int go[62][MAX],now[MAX];
int ck(int x)
{
	int i,j,len,nex;
//	cout<<x<<endl;
	for(i=1;i<=n;i++)
	{
		len=lower_bound(bit+i,bit+1+2*n,bit[i-1]+x)-bit-i+1;
//		cout<<i<<" "<<len<<endl;
		go[0][i]=len;
	}
	for(j=1;j<=20;j++)
	{
		for(i=1;i<=n;i++)
		{
			nex=i+go[j-1][i];
			if(nex>n) nex-=n;
			if(go[j-1][i]>n||go[j-1][nex]>n)
			{
				go[j][i]=n+1;
				continue;
			}
			go[j][i]=go[j-1][i]+go[j-1][nex];
		}
	}
	for(i=1;i<=n;i++) now[i]=0;
	for(i=0;i<=20;i++)
	{
		if(!((k>>i)&1)) continue;
		for(j=1;j<=n;j++)
		{
			nex=j+now[j];
			if(nex>n) nex-=n;
			if(now[j]>n||go[i][nex]>n)
			{
				now[j]=n+1;
				continue;
			}
			now[j]+=go[i][nex];
		}
	}
	for(i=1;i<=n;i++)
	{
//		cout<<i<<" "<<now[i]<<endl;
		if(now[i]<=n) return 1;
	}
	return 0;
}
int main()
{
	int i,ans;
	ll l,r,mid;
	scanf("%d%d",&n,&k);
	bit[0]=0;
	for(i=1;i<=2*n;i++)
	{
		if(i<=n) scanf("%d",&a[i]);
		else a[i]=a[i-n];
		bit[i]=bit[i-1]+a[i];
	}
	bit[2*n+1]=1e18;
	l=1;
	r=2e9;
	while(l<r)
	{
		mid=(l+r)>>1;
		if(ck(mid+1)) l=mid+1;
		else r=mid;
	}
	ans=0;
	ck(l);
	for(i=1;i<=n;i++)
	{
++_lcb_count;

		if(now[i]>n) ans++;
	}
if (_lcb_count > 1000) {
std::cout << "{\"ans\":";
_lcb_json(std::cout, ans);
std::cout << ",\"i\":";
_lcb_json(std::cout, i);
std::cout << ",\"k\":";
_lcb_json(std::cout, k);
std::cout << ",\"l\":";
_lcb_json(std::cout, l);
std::cout << ",\"n\":";
_lcb_json(std::cout, n);
std::cout << ",\"now[i]\":";
_lcb_json(std::cout, now[i]);
std::cout << ",\"r\":";
_lcb_json(std::cout, r);
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}

	printf("%lld %d\n",l,ans);
	return 0;
}
