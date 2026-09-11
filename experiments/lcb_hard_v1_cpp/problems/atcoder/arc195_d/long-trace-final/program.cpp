#include<bits/stdc++.h>

using namespace std;

const int N=2e5+9;

int f[N][2],a[N],n;

signed main(){
    ios::sync_with_stdio(0);
    cin.tie(0),cout.tie(0);
    #define endl '\n'

    int T;
    cin>>T;
    while(T--){
        cin>>n;
        for(int i=1;i<=n;i++) cin>>a[i];

        f[0][0]=0,f[0][1]=1e9;
        for(int i=1;i<=n;i++){
            f[i][0]=min(f[i-1][0]+(a[i]!=a[i-1]),f[i-1][1]+(i<=1||a[i]!=a[i-2]));
            if(i>1) f[i][1]=min(f[i-2][0]+(a[i]!=a[i-2]),f[i-2][1]+(i<=2||a[i]!=a[i-3]))+(a[i]!=a[i-1])+1;
            else f[i][1]=1e9;
        }

        cout<<min(f[n][0],f[n][1])<<endl;
    }

    return 0;
}
