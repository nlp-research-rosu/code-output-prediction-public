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

int n,m;
int f[maxn<<2];
int fd(int x){
    if(f[x]==x)return x;
    return f[x]=fd(f[x]);
}
void work(){
    n=read();m=read();
    for(int i=1;i<=4*n;i++)f[i]=i;
    for(int i=1;i<=m;i++){
        int u=read(),v=read(),c=read();
        if(!c)f[fd(u)]=fd(v+n),f[fd(u+2*n)]=fd(v+3*n);
        else f[fd(u)]=fd(v+3*n),f[fd(u+2*n)]=fd(v+n);
    }
    for(int i=1;i<=2*n;i++)if(fd(i)==fd(i+2*n)){puts("-1");return ;}
    for(int i=1;i<=n;i++){
        if(fd(i)==fd(i+n))putchar('0');
        else if(fd(i)==fd(i+3*n))putchar('1');
        else{
            putchar('0');
            f[fd(i)]=fd(i+n),f[fd(i+2*n)]=fd(i+3*n);
        }
    }
}

int T;
signed main(){
    // freopen("A.in","r",stdin);
    // freopen(".out","w",stdout);
    
    T=1;
    while(T--)work();
}
