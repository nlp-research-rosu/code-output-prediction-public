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

#include <cstdio>
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

int n,m,q,x,y,ans;
void work(){
    n=read();m=read();
    vector<vector<int>> a(n+2,vector<int>(m+2)),f(n+2,vector<int>(m+2)),g(n+2,vector<int>(m+2));
    for(int i=1;i<=n;i++){
        for(int j=1;j<=m;j++)a[i][j]=read();
    }
    f[1][1]=1;for(int i=1;i<=n;i++){
        for(int j=(i==1?2:1);j<=m;j++)f[i][j]=(f[i-1][j]*a[i-1][j]+f[i][j-1]*a[i][j-1])%mod;
    }
    g[n][m]=1;for(int i=n;i;i--){
        for(int j=(i==n?m-1:m);j;j--){

++_lcb_count;
g[i][j]=(g[i+1][j]*a[i+1][j]+g[i][j+1]*a[i][j+1])%mod;
}
if (_lcb_count > 1000) {
std::cout << "{\"i\":";
_lcb_json(std::cout, i);
std::cout << ",\"m\":";
_lcb_json(std::cout, m);
std::cout << ",\"n\":";
_lcb_json(std::cout, n);
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}

    }
    ans=f[n][m]*a[n][m]%mod;
    q=read();x=read();y=read();
    while(q--){
        char ch=getchar();while(ch<'A'||ch>'Z')ch=getchar();
        if(ch=='U')x--;
        if(ch=='L')y--;
        if(ch=='D')x++;
        if(ch=='R')y++;
        if(n<m){
            for(int i=(y==1?2:1);i<=n;i++)f[i][y]=(f[i-1][y]*a[i-1][y]+f[i][y-1]*a[i][y-1])%mod;
            for(int i=(y==m?n-1:n);i;i--)g[i][y]=(g[i+1][y]*a[i+1][y]+g[i][y+1]*a[i][y+1])%mod;
        }
        else{
            for(int j=(x==1?2:1);j<=m;j++)f[x][j]=(f[x-1][j]*a[x-1][j]+f[x][j-1]*a[x][j-1])%mod;
            for(int j=(x==n?m-1:m);j;j--)g[x][j]=(g[x+1][j]*a[x+1][j]+g[x][j+1]*a[x][j+1])%mod;
        }
        (ans+=mod-f[x][y]*g[x][y]%mod*a[x][y]%mod)%=mod;
        a[x][y]=read();
        if(n<m){
            for(int i=(y==1?2:1);i<=n;i++)f[i][y]=(f[i-1][y]*a[i-1][y]+f[i][y-1]*a[i][y-1])%mod;
            for(int i=(y==m?n-1:n);i;i--)g[i][y]=(g[i+1][y]*a[i+1][y]+g[i][y+1]*a[i][y+1])%mod;
        }
        else{
            for(int j=(x==1?2:1);j<=m;j++)f[x][j]=(f[x-1][j]*a[x-1][j]+f[x][j-1]*a[x][j-1])%mod;
            for(int j=(x==n?m-1:m);j;j--)g[x][j]=(g[x+1][j]*a[x+1][j]+g[x][j+1]*a[x][j+1])%mod;
        }
        (ans+=f[x][y]*g[x][y]%mod*a[x][y])%=mod;
        printf("%lld\n",ans);
    }
}

int T;
signed main(){
    // freopen("A.in","r",stdin);
    // freopen(".out","w",stdout);
    
    T=1;
    while(T--)work();
}
