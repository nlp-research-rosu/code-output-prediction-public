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
const ll LLINF=0x3f3f3f3f3f3f3f3fLL;
const int MAX=2e5+10;
const int mod=998244353;
namespace NTT
{
	const int g=3;
	const int p=998244353;
	int wn[35];
	int qpow(int a,int b)
	{
		int res=1;
		while(b>0)
		{
			if(b&1) res=1ll*res*a%p;
			a=1ll*a*a%p;
			b>>=1;
		}
		return res;
	}
	void getwn()
	{
		assert(p==mod);
		for(int i=0;i<25;i++) wn[i]=qpow(g,(p-1)/(1LL<<i));
	}
	void ntt(vector<int> &a,int len,int f)
	{
		int i,j=0,t,k,w,id;
		for(i=1;i<len-1;i++)
		{
			for(t=len;j^=t>>=1,~j&t;);
			if(i<j) swap(a[i],a[j]);
		}
		for(i=1,id=1;i<len;i<<=1,id++)
		{
			t=i<<1;
			for(j=0;j<len;j+=t)
			{
				for(k=0,w=1;k<i;k++,w=1ll*w*wn[id]%p)
				{
					int x=a[j+k],y=1ll*w*a[j+k+i]%p;
					a[j+k]=x+y;
					if(a[j+k]>=p) a[j+k]-=p;
					a[j+k+i]=x-y;
					if(a[j+k+i]<0) a[j+k+i]+=p;
				}
			}
		}
		if(f)
		{
			for(i=1,j=len-1;i<j;i++,j--) swap(a[i],a[j]);
			int inv=qpow(len,p-2);
			for(i=0;i<len;i++) a[i]=1ll*a[i]*inv%p;
		}
	}
	vector<int> mul(vector<int> a,vector<int> b)
	{
		int len,i,l1,l2;
		l1=a.size();
		l2=b.size();
		for(len=1;len<l1+l2;len<<=1);
		a.resize(len,0);
		b.resize(len,0);
		ntt(a,len,0);ntt(b,len,0);
		vector<int> res(len);
		for(i=0;i<len;i++) res[i]=1ll*a[i]*b[i]%p;
		ntt(res,len,1);
		res.resize(l1+l2-1);
		return res;
	}
};//NTT::getwn();
ll qpow(ll a,ll b)
{
	ll res=1;
	while(b>0)
	{
		if(b&1) res=res*a%mod;
		a=a*a%mod;
		b>>=1;
	}
	return res;
}
ll inv(ll x){return qpow(x,mod-2);}
int fac[MAX],invfac[MAX];
void init_comb(int n)
{
	assert(n<MAX);
	fac[0]=1;
	for(int i=1;i<=n;i++) fac[i]=1ll*fac[i-1]*i%mod;
	invfac[n]=inv(fac[n]);
	for(int i=n-1;~i;i--) invfac[i]=1ll*invfac[i+1]*(i+1)%mod;
}
ll C(int n,int m)
{
	if(m>n||m<0||n<0) return 0;
	return 1ll*fac[n]*invfac[m]%mod*invfac[n-m]%mod;
}
const int N=2e6+10;
int dig[MAX];
ll pw10[N];
int main()
{
	NTT::getwn();
	init_comb(MAX-10);
	int n,i,j,k,cnt[7],sum[7],x;
	ll ans;
	pw10[0]=1;
	for(i=1;i<N;i++) pw10[i]=pw10[i-1]*10L%mod;
	scanf("%d",&n);
	memset(cnt,0,sizeof cnt);
	memset(sum,0,sizeof sum);
	for(i=1;i<=n;i++)
	{
		dig[i]=to_string(i).length();
		cnt[dig[i]]++;
		sum[dig[i]]=(sum[dig[i]]+i)%mod;
	}
	ans=0;
	for(k=1;k<=6;k++)
	{
		vector<int> res(1,0);
		res[0]=1;
		for(i=1;i<=6;i++)
		{
			if(i==k) x=max(0,cnt[i]-1);
			else x=cnt[i];
			vector<int> tmp(x+1,0);
			for(j=0;j<=x;j++) tmp[j]=pw10[j*i]*C(x,j)%mod;
			res=NTT::mul(res,tmp);
		}
		if(cnt[k]>0) assert(res.size()==n);
		else assert(res.size()==n+1);
		for(i=0;i<res.size();i++)
		{
++_lcb_count;

			ans=(ans+1LL*sum[k]
					*fac[n-i-1]%mod
					*fac[i]%mod
					*res[i])%mod;
		}
if (_lcb_count > 1000) {
std::cout << "{\"ans\":";
_lcb_json(std::cout, ans);
std::cout << ",\"cnt[k]\":";
_lcb_json(std::cout, cnt[k]);
std::cout << ",\"i\":";
_lcb_json(std::cout, i);
std::cout << ",\"k\":";
_lcb_json(std::cout, k);
std::cout << ",\"n\":";
_lcb_json(std::cout, n);
std::cout << ",\"res.size()\":";
_lcb_json(std::cout, res.size());
std::cout << ",\"sum[k]\":";
_lcb_json(std::cout, sum[k]);
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}

	}
	printf("%lld\n",ans);
	return 0;
}
