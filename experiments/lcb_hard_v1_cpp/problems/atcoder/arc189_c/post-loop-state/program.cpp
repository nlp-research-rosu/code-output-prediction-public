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

const int N=2e5+9;

int a[N],b[N],p[N],q[N],tr[N],n,rt;
int avis[N],adis[N],bvis[N],bdis[N];
void Add(int x,int k){
    while(x<=n){
        tr[x]=max(tr[x],k);
        x+=x&-x;
    }
}
int Ask(int x){
    int sum=0;
    while(x){
        sum=max(sum,tr[x]);
        x&=x-1;
    }
    return sum;
}

int LIS(vector<int> v){
    vector<int> d;
    for(int x:v){
        auto it=lower_bound(d.begin(),d.end(),x);
        if(it==d.end()) d.push_back(x);
        else *it=x;
    }
    return d.size();

    // int ans=0;
    // for(int x:v){
    //     int f=Ask(x)+1;
    //     Add(x,f);
    //     ans=max(ans,f);
    // }
    // return ans;
}

int main(){
    cin>>n>>rt;
    for(int i=1;i<=n;i++) cin>>a[i];
    for(int i=1;i<=n;i++) cin>>b[i];
    for(int i=1;i<=n;i++) cin>>p[i];
    for(int i=1;i<=n;i++) cin>>q[i];

    vector<int> f,g;
    int tmp=p[rt],cnt=0,flag=0;
    while(tmp!=rt){
        if(a[tmp]) flag=1;
        if(flag) f.push_back(tmp);
        avis[tmp]=1;
        tmp=p[tmp];
    }

    tmp=q[rt],cnt=0,flag=0;
    while(tmp!=rt){
        if(b[tmp]) flag=1;
        if(flag) g.push_back(tmp);
        bvis[tmp]=1;
        tmp=q[tmp];
    }

    avis[rt]=bvis[rt]=1;
    for(int i=1;i<=n;i++){
        if(a[i]&&!avis[i]){
            cout<<-1<<endl;
            return 0;
        }
    }
    for(int i=1;i<=n;i++){
        if(b[i]&&!bvis[i]){
            cout<<-1<<endl;
            return 0;
        }
    }

    cnt=0;
    vector<int> v;
    for(int x:f) adis[x]=++cnt;
    for(int x:g) {

++_lcb_count;
if(adis[x]) v.push_back(adis[x]);
}
if (_lcb_count > 1000) {
std::cout << "{\"cnt\":";
_lcb_json(std::cout, cnt);
std::cout << ",\"f\":";
_lcb_json(std::cout, f);
std::cout << ",\"g\":";
_lcb_json(std::cout, g);
std::cout << ",\"v\":";
_lcb_json(std::cout, v);
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}

    cout<<f.size()+g.size()-LIS(v)<<endl;

    return 0;
}
