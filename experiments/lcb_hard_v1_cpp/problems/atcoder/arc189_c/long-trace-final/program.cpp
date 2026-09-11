#include<bits/stdc++.h>

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
    for(int x:g) if(adis[x]) v.push_back(adis[x]);
    cout<<f.size()+g.size()-LIS(v)<<endl;

    return 0;
}
