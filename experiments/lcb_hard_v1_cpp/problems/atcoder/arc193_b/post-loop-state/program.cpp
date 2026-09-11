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

#define ll long long
#define eb emplace_back
#define ep emplace
#define pii pair<int,int>
#define fi first
#define se second
#define debug(...) fprintf(stderr,__VA_ARGS__)
#define mems(arr,x) memset(arr,x,sizeof(arr))
#define memc(arr1,arr2) memcpy(arr1,arr2,sizeof(arr2))
using namespace std;
const int maxn=1e6+10,mod=998244353;
namespace FastMod{
    inline void madd(int &x,int y){x+=y;(x>=mod)&&(x-=mod);}
    inline void mdel(int &x,int y){x-=y;(x<0)&&(x+=mod);}
    inline void mmul(int &x,int y){x=1ull*x*y%mod;}
    inline int imadd(int x,int y){madd(x,y);return x;}
    inline int imdel(int x,int y){mdel(x,y);return x;}
    inline int immul(int x,int y){mmul(x,y);return x;}
    inline int qpow(int x,int y){int res=1;while(y){if(y&1) mmul(res,x);mmul(x,x);y>>=1;}return res;}
}
using namespace FastMod;
int n;
// dp[i][0/1][0/1] 表示前 i 个位置是否有 n->1，是否有 i+1 -> i 是否可行
int a[maxn],f[maxn][16];
bool dp[2][2],g[2][2];
int main(){
    scanf("%d",&n);
    for(int i=1;i<=n;i++)   scanf("%1d",&a[i]);
    // deg[1]=0
    f[1][1]=1;
    // deg[1]=1
    if(a[1])    f[1][7]=1;
    else    f[1][6]=1;
    // deg[1]=2
    if(a[1])    f[1][14]=1;
    else    f[1][8]=1;
    // deg[1]=3
    if(a[1])    f[1][8]=1;
    for(int i=2;i<=n;i++){
        for(int j=1;j<16;j++){
            if(!f[i-1][j])    continue;
            dp[0][0]=j&1;dp[0][1]=(j>>1)&1;dp[1][0]=(j>>2)&1;dp[1][1]=j>>3;
            for(int d=0;d<=2+a[i];d++){
                mems(g,0);
                if(a[i]){
                    for(int k:{0,1}){
                        if(d<=1)    g[k][0]=dp[k][!d];
                        if(d==1||d==2)  g[k][0]|=dp[k][!(d-1)];
                        if(d==1||d==2)  g[k][1]=dp[k][!(d-1)];
                        if(d==2||d==3)  g[k][1]|=dp[k][!(d-2)];
                    }
                }
                else{
                    for(int k:{0,1}){
++_lcb_count;

                        if(d<=1)    g[k][0]=dp[k][!d];
                        if(d==1||d==2)  g[k][1]|=dp[k][!(d-1)];
                    }
if (_lcb_count > 1000) {
std::cout << "{\"a[i]\":";
_lcb_json(std::cout, a[i]);
std::cout << ",\"d\":";
_lcb_json(std::cout, d);
std::cout << ",\"dp[0][0]\":";
_lcb_json(std::cout, dp[0][0]);
std::cout << ",\"dp[0][1]\":";
_lcb_json(std::cout, dp[0][1]);
std::cout << ",\"dp[1][0]\":";
_lcb_json(std::cout, dp[1][0]);
std::cout << ",\"dp[1][1]\":";
_lcb_json(std::cout, dp[1][1]);
std::cout << ",\"i\":";
_lcb_json(std::cout, i);
std::cout << ",\"j\":";
_lcb_json(std::cout, j);
std::cout << ",\"n\":";
_lcb_json(std::cout, n);
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}

                }
                int sta=g[0][0]|(g[0][1]<<1)|(g[1][0]<<2)|(g[1][1]<<3);
                madd(f[i][sta],f[i-1][j]);
            }
        }
    }
    int ans=0;
	for(int i=0;i<16;i++)if((i&2)||(i&4))madd(ans,f[n][i]);
    printf("%d\n",ans);
    // for(int i=2;i<n;i++){
    //     for(int a:{0,1})for(int b:{0,1})for(int c:{0,1,2,3})for(int d:{0,1}){
    //         if(::a[i]){
    //             madd(f[i][a][d][!b+d],f[i-1][a][b][c]);
    //             madd(f[i][a][d][!b+d+1],f[i-1][a][b][c]);
    //         }
    //         else    madd(f[i][a][d][!b+d],f[i-1][a][b][c]);
    //     }
    // }
    // int ans=0;
    // for(int a:{0,1})for(int b:{0,1})for(int c:{0,1,2,3}){
    //     if(a[n]){
    //         madd(ans,f[n-1][a][b][c]);
    //     }
    // }
}
