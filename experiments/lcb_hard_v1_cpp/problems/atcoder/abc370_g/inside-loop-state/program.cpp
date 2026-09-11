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


using namespace std;

#define int long long
const int SQ=1e5+9;
const int mod=998244353;

int pri[SQ],ntp[SQ],cnt;
void InitP(int lim){
    for(int i=2;i<=lim;i++){
        if(!ntp[i]) pri[++cnt]=i;
        for(int j=1;j<=cnt&&pri[j]*i<=lim;j++){
            ntp[pri[j]*i]=1;
            if(i%pri[j]==0) break ;
        }
    }
}
int QPow(int x,int y){
    int res=1;
    while(y){
        if(y&1) res=res*x%mod;
        x=x*x%mod;
        y>>=1;
    }
    return res;
}

int w[SQ<<1],pos[2][SQ],n,sq,m,tot;
#define Get(x) (x>sq?pos[1][n/(x)]:pos[0][(x)])
#define F(x) ((x)%3==2?-1:(x)%3)
void InitPos(){
    for(int l=1,r;l<=n;l=r+1){
        r=n/(n/l);
        w[++tot]=n/l;
        Get(w[tot])=tot;
    }
}
int h[64],g[2][SQ<<1],sp[2][SQ<<1];
void CalcG(){
    h[0]=1;for(int i=1;i<64;i++) h[i]=h[i-1]*(m-1+i)%mod*QPow(i,mod-2)%mod;
    for(int i=1;i<=tot;i++){
        g[0][i]=w[i]-1;
        g[1][i]=(w[i]-1)/3-(w[i]+1)/3;
    }
    for(int i=1;i<=cnt;i++){
        sp[0][i]=i;
        sp[1][i]=sp[1][i-1]+F(pri[i]);
    }
    for(int i=1;i<=cnt;i++){
        for(int j=1;j<=tot&&pri[i]*pri[i]<=w[j];j++){
            int k=Get(w[j]/pri[i]);
            g[0][j]=(g[0][j]-(g[0][k]-sp[0][i-1]+mod)%mod+mod)%mod;
            g[1][j]=(g[1][j]-(g[1][k]-sp[1][i-1]+mod)%mod*F(pri[i])%mod+mod)%mod;
        }
    }
}
int S0(int x,int k){
    if(pri[k]>=x) return 0;
    int ans=(g[0][Get(x)]-sp[0][k]+mod)%mod*m%mod;
    for(int i=k+1;i<=cnt&&pri[i]*pri[i]<=x;i++){
        for(int e=1,pn=pri[i];pn<=x;e++,pn=pn*pri[i]){
            ans=(ans+h[e]*(S0(x/pn,i)+(e>1))%mod)%mod;
        }
    }
    return ans;
}
const int INV2=QPow(2,mod-2);
int S1(int x,int k){
    if(pri[k]>=x) return 0;
    int cur=Get(x);
    int ans=((g[0][cur]-sp[0][k]+mod)%mod+(g[1][cur]-sp[1][k]+mod)%mod
            +(x>=3)-(pri[k]>=3))%mod*m%mod*INV2%mod;
    for(int i=k+1;i<=cnt&&pri[i]*pri[i]<=x;i++){
        for(int e=1,pn=pri[i],sum=1;pn<=x;e++,pn=pn*pri[i]){
++_lcb_count;
if (_lcb_count == 502) {
std::cout << "{\"ans\":";
_lcb_json(std::cout, ans);
std::cout << ",\"i\":";
_lcb_json(std::cout, i);
std::cout << ",\"k\":";
_lcb_json(std::cout, k);
std::cout << ",\"x\":";
_lcb_json(std::cout, x);
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}

            sum=(sum*pri[i]+1)%3;
            if(sum) ans=(ans+h[e]*(S1(x/pn,i)+(e>1))%mod)%mod;
        }
    }
    return ans;
}

signed main(){
    cin>>n>>m;
    sq=sqrt(n);
    InitP(sq);
    InitPos();
    CalcG();
    cout<<(S0(n,0)-S1(n,0)+mod)%mod<<endl;

    return 0;
}