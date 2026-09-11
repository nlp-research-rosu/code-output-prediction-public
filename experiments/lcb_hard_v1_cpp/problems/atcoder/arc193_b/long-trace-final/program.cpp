#include<bits/stdc++.h>
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
                        if(d<=1)    g[k][0]=dp[k][!d];
                        if(d==1||d==2)  g[k][1]|=dp[k][!(d-1)];
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
