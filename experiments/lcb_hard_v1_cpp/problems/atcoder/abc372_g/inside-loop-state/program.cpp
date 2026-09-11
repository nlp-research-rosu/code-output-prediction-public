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
#define bint __int128
#define Clp(x,l,r) min(r,max(x,l))
#define Allc(x) x.begin(),x.end()
const int inf=1e18;


bint F(bint n,bint a,bint b,bint c){
    if(!a||!n) return (n+1)*(b/c);
    else if(c<0) return F(n,-a,-b,-c);
    else if(a>=c||b>=c) return n*(n+1)/2*(a/c)+(n+1)*(b/c)+F(n,a%c,b%c,c);
    else if(a<0||b<0) return n*(n+1)/2*(a/c-1)+(n+1)*(b/c-1)+F(n,a%c+c,b%c+c,c);
    else return (a*n+b)/c*n-F((a*n+b)/c-1,c,c-b-1,a);
}
void Solve(){
    int n;
    cin>>n;
    vector<array<int,3>> a(n),stk;
    for(int i=0;i<n;i++) cin>>a[i][0]>>a[i][1]>>a[i][2];
    sort(Allc(a),[](auto x,auto y){
        if(x[0]*y[1]!=x[1]*y[0]) return x[0]*y[1]<x[1]*y[0];
        else return x[0]*y[2]>x[2]*y[0];
    });

    int lim=inf;
    vector<int> pos;
    for(auto x:a){
        if(stk.size()){
            auto y=stk.back();
            if(x[0]*y[1]==x[1]*y[0]) continue ;
        }
        while(stk.size()>1){
++_lcb_count;
if (_lcb_count == 502) {
std::cout << "{";
std::cout << "\"lim\":";
_lcb_json(std::cout, lim);
std::cout << ",\"pos\":";
_lcb_json(std::cout, pos);
std::cout << ",\"stk.size()\":";
_lcb_json(std::cout, stk.size());
std::cout << ",\"x[0]\":";
_lcb_json(std::cout, x[0]);
std::cout << ",\"x[1]\":";
_lcb_json(std::cout, x[1]);
std::cout << ",\"x[2]\":";
_lcb_json(std::cout, x[2]);
std::cout << "}\n";
std::exit(0);
}

            auto y=stk.back();
            int p=(y[1]*x[2]-x[1]*y[2]-1)/(x[0]*y[1]-x[1]*y[0])+1;
            if(p>pos.back()) break ;
            stk.pop_back();
            pos.pop_back();
        }
        if(!pos.size()){
            pos.push_back(-inf);
            stk.push_back(x);
        }else{
            auto y=stk.back();
            pos.push_back((y[1]*x[2]-x[1]*y[2]-1)/(x[0]*y[1]-x[1]*y[0])+1);
            stk.push_back(x);
        }
        lim=min(lim,(x[2]+x[0]-1)/x[0]);
    }
    pos.push_back(inf);

    bint ans=0;
    for(int i=0;i<stk.size();i++){
        int l=Clp(pos[i],1ll,lim)-1,r=Clp(pos[i+1],1ll,lim)-1;
        ans+=F(r,-stk[i][0],stk[i][2]-1,stk[i][1])-F(l,-stk[i][0],stk[i][2]-1,stk[i][1]);
    }
    cout<<(int)ans<<endl;
}

signed main(){
    int T;
    cin>>T;
    while(T--) Solve();
    return 0;
}
