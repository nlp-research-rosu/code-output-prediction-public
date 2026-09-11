#include<bits/stdc++.h>
const int N=2e5+10,MOD=998244353;
int siz[N],sum[N],val[N];
struct block{
	int sum,siz,rt;
	bool operator<(const block& b)const{
		return 1ll*sum*b.siz<1ll*b.sum*siz;
	}
};
int pa[N],sz[N];
std::priority_queue<block> q;
int p[N],a[N];
int findp(int x){
	if(x==pa[x]) return x;
	return pa[x]=findp(pa[x]);
}
int qpow(int a,int b){
	int ret=1;
	while(b){
		if(b&1) ret=1ll*ret*a%MOD;
		a=1ll*a*a%MOD;b>>=1;
	}
	return ret;
}
int main(){
	int T;scanf("%d",&T);
	while(T--){
		int n,S=0;scanf("%d",&n);
		for(int i=1;i<=n;i++)
			scanf("%d",p+i);
		for(int i=1;i<=n;i++)
			scanf("%d",a+i),S+=a[i];
		std::copy(a,a+n+1,sum);
		std::fill(siz,siz+n+1,1);siz[0]=0;
		std::iota(pa,pa+n+1,0);
		std::fill(sz,sz+n+1,1);
		std::copy(a,a+n+1,val);
		for(int i=0;i<=n;i++) q.push({sum[i],siz[i],i});
		while(!q.empty()){
			block qt=q.top();int u=qt.rt;q.pop();
			if(!u||siz[u]!=qt.siz) continue;
			int f=findp(p[u]);pa[u]=f;
			val[f]=((val[f]+val[u])%MOD+1ll*siz[f]*sum[u]%MOD)%MOD;
			siz[f]+=siz[u];sum[f]+=sum[u];
			q.push({sum[f],siz[f],f});
		}
		int ans=1ll*val[0]*qpow(S,MOD-2)%MOD;
		printf("%d\n",ans);
	}
}
