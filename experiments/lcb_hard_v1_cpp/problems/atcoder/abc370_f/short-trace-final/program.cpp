#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const int INF=0x3f3f3f3f;
const int MAX=4e5+10;
int a[MAX],n,k;
ll bit[MAX];
int go[62][MAX],now[MAX];
int ck(int x)
{
	int i,j,len,nex;
//	cout<<x<<endl;
	for(i=1;i<=n;i++)
	{
		len=lower_bound(bit+i,bit+1+2*n,bit[i-1]+x)-bit-i+1;
//		cout<<i<<" "<<len<<endl;
		go[0][i]=len;
	}
	for(j=1;j<=20;j++)
	{
		for(i=1;i<=n;i++)
		{
			nex=i+go[j-1][i];
			if(nex>n) nex-=n;
			if(go[j-1][i]>n||go[j-1][nex]>n)
			{
				go[j][i]=n+1;
				continue;
			}
			go[j][i]=go[j-1][i]+go[j-1][nex];
		}
	}
	for(i=1;i<=n;i++) now[i]=0;
	for(i=0;i<=20;i++)
	{
		if(!((k>>i)&1)) continue;
		for(j=1;j<=n;j++)
		{
			nex=j+now[j];
			if(nex>n) nex-=n;
			if(now[j]>n||go[i][nex]>n)
			{
				now[j]=n+1;
				continue;
			}
			now[j]+=go[i][nex];
		}
	}
	for(i=1;i<=n;i++)
	{
//		cout<<i<<" "<<now[i]<<endl;
		if(now[i]<=n) return 1;
	}
	return 0;
}
int main()
{
	int i,ans;
	ll l,r,mid;
	scanf("%d%d",&n,&k);
	bit[0]=0;
	for(i=1;i<=2*n;i++)
	{
		if(i<=n) scanf("%d",&a[i]);
		else a[i]=a[i-n];
		bit[i]=bit[i-1]+a[i];
	}
	bit[2*n+1]=1e18;
	l=1;
	r=2e9;
	while(l<r)
	{
		mid=(l+r)>>1;
		if(ck(mid+1)) l=mid+1;
		else r=mid;
	}
	ans=0;
	ck(l);
	for(i=1;i<=n;i++)
	{
		if(now[i]>n) ans++;
	}
	printf("%lld %d\n",l,ans);
	return 0;
}
