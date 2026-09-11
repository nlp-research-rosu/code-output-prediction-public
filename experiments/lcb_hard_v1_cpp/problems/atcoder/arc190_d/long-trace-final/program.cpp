#include<bits/stdc++.h>
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
        for(int j=1;j<=n;j++)(ans[i][j]+=pw*b.e[i][j])%=mod;
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
