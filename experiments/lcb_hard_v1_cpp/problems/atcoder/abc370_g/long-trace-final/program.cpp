#include<bits/stdc++.h>

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