#include<bits/stdc++.h>
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
        for(int j=(i==n?m-1:m);j;j--)g[i][j]=(g[i+1][j]*a[i+1][j]+g[i][j+1]*a[i][j+1])%mod;
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
