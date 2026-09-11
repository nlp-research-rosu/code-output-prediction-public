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

#define int long long
#define mod 998244353ll
#define pii pair<int,int>
#define fi first
#define se second
#define pb push_back
using namespace std;
inline int read(){
    int x=0,fl=1;char ch=getchar();
    while(ch<'0'||ch>'9'){if(ch=='-')fl=-1;ch=getchar();}
    while(ch>='0'&&ch<='9'){x=x*10+ch-'0';ch=getchar();}
    return x*fl;
}
const int maxn=200010;
const int inf=1e9;

inline int ksm(int a,int b=mod-2){
    int ans=1;
    while(b){
        if(b&1)ans=ans*a%mod;
        a=a*a%mod;
        b>>=1;
    }
    return ans;
}
void inc(int &u,int v){((u+=v)>=mod)&&(u-=mod);}
namespace poly{
    int g=3,invg=ksm(3);
    int to[maxn<<3];
    void ntt(vector<int> &a,int fl){
        int n=a.size();
        for(int i=0;i<n;i++)if(i<to[i])swap(a[i],a[to[i]]);
        for(int l=2;l<=n;l<<=1){
            int bas=ksm(fl==1?g:invg,(mod-1)/l),k=l/2;
            for(int i=0;i<n;i+=l){
                int mul=1;
                for(int j=i;j<i+k;j++){
                    int val=a[j+k]*mul%mod;
                    inc(a[j+k]=a[j],mod-val);
                    inc(a[j],val);
                    mul=mul*bas%mod;
                }
            }
        }
        if(fl==-1){
            int inv=ksm(n);
            for(int i=0;i<n;i++)a[i]=a[i]*inv%mod;
        }
    }
    vector<int> mul(vector<int> a,vector<int> b){
        int n=a.size()-1,m=b.size()-1,k=1;
        while(k<n+m+1)k<<=1;
        for(int i=0;i<k;i++)to[i]=(to[i>>1]>>1)|((i&1)?(k>>1):0);
        a.resize(k,0),b.resize(k,0);
        ntt(a,1),ntt(b,1);
        for(int i=0;i<k;i++)a[i]=a[i]*b[i]%mod;
        ntt(a,-1);
        a.resize(n+m+1);
        return a;
    }
}
using poly::mul;
int n;
char s[maxn<<1];
int p[maxn],f[maxn];
int fac[maxn],inv[maxn];
int C(int m,int n){return fac[m]*inv[n]%mod*inv[m-n]%mod;}
void sovle(int l,int r){
    if(l==r){
        if(l>=p[l]-l)f[l]=(C(l,p[l]-l)*fac[p[l]-l]+mod-f[l])%mod;
        else f[l]=0;
        return ;
    }
    int mid=l+r>>1;
    sovle(l,mid);
    int fl=p[l]-l,fr=p[mid]-mid,gl=max(0ll,mid+1-(p[mid]-mid)),gr=max(0ll,r-(p[l]-l));
    vector<int> ff(fr-fl+1),gg(gr-gl+1);
    for(int i=l;i<=mid;i++)if(i>=p[i]-i)(ff[p[i]-i-fl]+=f[i])%=mod;
    for(int i=gl;i<=gr;i++)gg[i-gl]=fac[i];
    vector<int> hh=mul(ff,gg);
    for(int i=mid+1;i<=r;i++)if(i>=p[i]-i)(f[i]+=hh[i-fl-gl]*inv[2*i-p[i]])%=mod;
    sovle(mid+1,r);
}
void work(){
    n=read();scanf("%s",s+1);
    if(s[1]=='W'||s[2*n]=='B'){puts("0");return ;}
    n=0;for(int i=1;s[i]=='W'||s[i]=='B';i++)if(s[i]=='W')p[++n]=i;
    fac[0]=1;for(int i=1;i<=n;i++)fac[i]=fac[i-1]*i%mod;
    inv[n]=ksm(fac[n]);for(int i=n-1;~i;i--){

++_lcb_count;
inv[i]=inv[i+1]*(i+1)%mod;
}
if (_lcb_count > 1000) {
std::cout << "{\"fac[n]\":";
_lcb_json(std::cout, fac[n]);
std::cout << ",\"inv[0]\":";
_lcb_json(std::cout, inv[0]);
std::cout << ",\"inv[n/2]\":";
_lcb_json(std::cout, inv[n/2]);
std::cout << ",\"inv[n]\":";
_lcb_json(std::cout, inv[n]);
std::cout << ",\"n\":";
_lcb_json(std::cout, n);
std::cout << ",\"p[n]\":";
_lcb_json(std::cout, p[n]);
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}

    sovle(1,n);
    // for(int i=1;i<=n;i++){
    //     f[i]=C(i,p[i]-i)*fac[p[i]-i]%mod;
    //     for(int j=1;j<i;j++)(f[i]+=mod-C(i-(p[j]-j),p[i]-i-(p[j]-j))*fac[p[i]-i-(p[j]-j)]%mod*f[j]%mod)%=mod;
    //     // cout<<i<<" "<<p[i]<<" "<<f[i]<<"\n";
    // }
    // for(int i=1;i<=n;i++)cout<<i<<" "<<p[i]<<" "<<f[i]<<"\n";
    printf("%lld\n",f[n]);
}

int T;
signed main(){
    // freopen("A.in","r",stdin);
    // freopen(".out","w",stdout);
    
    T=1;
    while(T--)work();
}
