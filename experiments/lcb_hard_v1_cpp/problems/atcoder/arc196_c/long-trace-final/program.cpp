#include<bits/stdc++.h>
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

inline int ksm(int a,int b=mod-2){
    int ans=1;
    while(b){
        if(b&1)ans=ans*a%mod;
        a=a*a%mod;
        b>>=1;
    }
    return ans;
}
void inc(int &u,int v){((u+=v)>=mod)&&(u-=mod);}
namespace poly{
    int g=3,invg=ksm(3);
    int to[maxn<<3];
    void ntt(vector<int> &a,int fl){
        int n=a.size();
        for(int i=0;i<n;i++)if(i<to[i])swap(a[i],a[to[i]]);
        for(int l=2;l<=n;l<<=1){
            int bas=ksm(fl==1?g:invg,(mod-1)/l),k=l/2;
            for(int i=0;i<n;i+=l){
                int mul=1;
                for(int j=i;j<i+k;j++){
                    int val=a[j+k]*mul%mod;
                    inc(a[j+k]=a[j],mod-val);
                    inc(a[j],val);
                    mul=mul*bas%mod;
                }
            }
        }
        if(fl==-1){
            int inv=ksm(n);
            for(int i=0;i<n;i++)a[i]=a[i]*inv%mod;
        }
    }
    vector<int> mul(vector<int> a,vector<int> b){
        int n=a.size()-1,m=b.size()-1,k=1;
        while(k<n+m+1)k<<=1;
        for(int i=0;i<k;i++)to[i]=(to[i>>1]>>1)|((i&1)?(k>>1):0);
        a.resize(k,0),b.resize(k,0);
        ntt(a,1),ntt(b,1);
        for(int i=0;i<k;i++)a[i]=a[i]*b[i]%mod;
        ntt(a,-1);
        a.resize(n+m+1);
        return a;
    }
}
using poly::mul;
int n;
char s[maxn<<1];
int p[maxn],f[maxn];
int fac[maxn],inv[maxn];
int C(int m,int n){return fac[m]*inv[n]%mod*inv[m-n]%mod;}
void sovle(int l,int r){
    if(l==r){
        if(l>=p[l]-l)f[l]=(C(l,p[l]-l)*fac[p[l]-l]+mod-f[l])%mod;
        else f[l]=0;
        return ;
    }
    int mid=l+r>>1;
    sovle(l,mid);
    int fl=p[l]-l,fr=p[mid]-mid,gl=max(0ll,mid+1-(p[mid]-mid)),gr=max(0ll,r-(p[l]-l));
    vector<int> ff(fr-fl+1),gg(gr-gl+1);
    for(int i=l;i<=mid;i++)if(i>=p[i]-i)(ff[p[i]-i-fl]+=f[i])%=mod;
    for(int i=gl;i<=gr;i++)gg[i-gl]=fac[i];
    vector<int> hh=mul(ff,gg);
    for(int i=mid+1;i<=r;i++)if(i>=p[i]-i)(f[i]+=hh[i-fl-gl]*inv[2*i-p[i]])%=mod;
    sovle(mid+1,r);
}
void work(){
    n=read();scanf("%s",s+1);
    if(s[1]=='W'||s[2*n]=='B'){puts("0");return ;}
    n=0;for(int i=1;s[i]=='W'||s[i]=='B';i++)if(s[i]=='W')p[++n]=i;
    fac[0]=1;for(int i=1;i<=n;i++)fac[i]=fac[i-1]*i%mod;
    inv[n]=ksm(fac[n]);for(int i=n-1;~i;i--)inv[i]=inv[i+1]*(i+1)%mod;
    sovle(1,n);
    // for(int i=1;i<=n;i++){
    //     f[i]=C(i,p[i]-i)*fac[p[i]-i]%mod;
    //     for(int j=1;j<i;j++)(f[i]+=mod-C(i-(p[j]-j),p[i]-i-(p[j]-j))*fac[p[i]-i-(p[j]-j)]%mod*f[j]%mod)%=mod;
    //     // cout<<i<<" "<<p[i]<<" "<<f[i]<<"\n";
    // }
    // for(int i=1;i<=n;i++)cout<<i<<" "<<p[i]<<" "<<f[i]<<"\n";
    printf("%lld\n",f[n]);
}

int T;
signed main(){
    // freopen("A.in","r",stdin);
    // freopen(".out","w",stdout);
    
    T=1;
    while(T--)work();
}
