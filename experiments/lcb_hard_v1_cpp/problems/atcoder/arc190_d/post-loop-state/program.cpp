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
// #define mod 998244353ll
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
const int maxn=110;
const int inf=1e9;

int n,m,pw,mod;
int a[maxn][maxn],ans[maxn][maxn];
struct mat{
    int e[maxn][maxn];
    mat(){memset(e,0,sizeof(e));}
    mat operator*(const mat&tmp)const{
        mat res;
        for(int i=1;i<=n;i++){
            for(int k=1;k<=n;k++){
                for(int j=1;j<=n;j++)(res.e[i][j]+=e[i][k]*tmp.e[k][j])%=mod;
            }
        }
        return res;
    }
}b;
mat one(){
    mat res;for(int i=1;i<=n;i++)res.e[i][i]=1;return res;
}
mat ksm(mat a,int b){
    mat ans=one();
    while(b){
        if(b&1)ans=ans*a;
        a=a*a;
        b>>=1;
    }
    return ans;
}
void work(){
    n=read();mod=read();
    for(int i=1;i<=n;i++){
        for(int j=1;j<=n;j++)a[i][j]=read(),m+=(a[i][j]==0);
    }
    pw=1;for(int i=1;i<=m;i++)pw=pw*(mod-1)%mod;
    if(mod==2){
        for(int i=1;i<=n;i++){
            for(int j=1;j<=n;j++)b.e[i][j]=1;
        }
        b=ksm(b,mod);
        for(int i=1;i<=n;i++){
            for(int j=1;j<=n;j++)printf("%lld ",b.e[i][j]);
        }
        return ;
    }
    for(int i=1;i<=n;i++)if(!a[i][i]){
        for(int j=1;j<=n;j++){
            if(a[j][i])(ans[j][i]+=pw*a[j][i])%=mod;
            if(a[i][j])(ans[i][j]+=pw*a[i][j])%=mod;
        }
    }
    if(mod==3){
        for(int i=1;i<=n;i++){
            for(int j=1;j<=n;j++)if(!a[i][j]&&a[j][i])(ans[i][j]+=pw*a[j][i])%=mod;
        }
    }
    for(int i=1;i<=n;i++){
        for(int j=1;j<=n;j++)b.e[i][j]=a[i][j];
    }
    b=ksm(b,mod);
    for(int i=1;i<=n;i++){
        for(int j=1;j<=n;j++){

++_lcb_count;
(ans[i][j]+=pw*b.e[i][j])%=mod;
}
if (_lcb_count > 1000) {
std::cout << "{\"i\":";
_lcb_json(std::cout, i);
std::cout << ",\"mod\":";
_lcb_json(std::cout, mod);
std::cout << ",\"n\":";
_lcb_json(std::cout, n);
std::cout << ",\"pw\":";
_lcb_json(std::cout, pw);
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}

    }
    for(int i=1;i<=n;i++){
        for(int j=1;j<=n;j++)printf("%lld ",ans[i][j]);puts("");
    }
}

int T;
signed main(){
    // freopen("A.in","r",stdin);
    // freopen(".out","w",stdout);
    
    T=1;
    while(T--)work();
}
