#include<bits/stdc++.h>

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
