#include <bits/stdc++.h>
using namespace std;
long long a, b, q, w, e, ann, u[1200001], cn, fl, v1[1200001], v2[1200001];
struct p {
  long long q, w, id;
};
vector<p> qu[4];
struct seg {
  struct pp {
    long long sum;
  } l[2400001];
  void pushup(long long qq) { l[qq].sum = l[qq << 1].sum + l[qq << 1 | 1].sum; }
  void change(long long x, long long ll, long long rr, long long qq,
              long long ww) {
    if (ll == rr) {
      l[x].sum = ww;
      return;
    }
    long long mid = ((ll + rr) >> 1);
    if (mid >= qq)
      change(x << 1, ll, mid, qq, ww);
    else
      change(x << 1 | 1, mid + 1, rr, qq, ww);
    pushup(x);
  }
  long long query(long long x, long long ll, long long rr, long long qq) {
    if (l[x].sum < qq) return -1;
    if (ll == rr) return ll;
    long long mid = ((ll + rr) >> 1);
    if (l[x << 1].sum >= qq) return query(x << 1, ll, mid, qq);
    return query(x << 1 | 1, mid + 1, rr, qq - l[x << 1].sum);
  }
  long long query2(long long x, long long ll, long long rr, long long qq) {
    if (l[x].sum < qq) return -1;
    if (ll == rr) return ll;
    long long mid = ((ll + rr) >> 1);
    if (l[x << 1 | 1].sum >= qq) return query2(x << 1 | 1, mid + 1, rr, qq);
    return query2(x << 1, ll, mid, qq - l[x << 1 | 1].sum);
  }
  long long query1(long long x, long long ll, long long rr, long long qq,
                   long long ww) {
    if (qq > ww) return 0;
    if (ll >= qq && rr <= ww) return l[x].sum;
    long long mid = ((ll + rr) >> 1);
    if (mid >= ww)
      return query1(x << 1, ll, mid, qq, ww);
    else if (mid < qq)
      return query1(x << 1 | 1, mid + 1, rr, qq, ww);
    return query1(x << 1, ll, mid, qq, ww) +
           query1(x << 1 | 1, mid + 1, rr, qq, ww);
  }
  void build(long long x, long long ll, long long rr) {
    if (ll == rr) {
      l[x].sum = v1[ll];
      return;
    }
    long long mid = ((ll + rr) >> 1);
    build(x << 1, ll, mid);
    build(x << 1 | 1, mid + 1, rr);
    pushup(x);
  }
} seg[8], s;
void work1(long long qq, long long ww, long long ee, long long ff) {
  if (fl) return;
  long long t1 = seg[qq].query(1, 1, cn, ff);
  if (t1 == -1) return;
  long long tt = seg[ww].query1(1, 1, cn, 1, t1);
  long long t2 = seg[ww].query(1, 1, cn, ff + tt);
  if (t2 == -1) return;
  tt = seg[ee].query1(1, 1, cn, 1, t2);
  long long t3 = seg[ee].query(1, 1, cn, ff + tt);
  if (t3 == -1) return;
  fl = 1;
}
void work2(long long qq, long long ww, long long ee, long long ff) {
  if (fl) return;
  long long t1 = seg[qq + 3].query(1, 1, cn, ff);
  if (t1 == -1) return;
  long long tt = seg[ww + 3].query1(1, 1, cn, 1, t1);
  long long t2 = seg[ww + 3].query(1, 1, cn, ff + tt);
  if (t2 == -1) return;
  tt = seg[ee + 3].query1(1, 1, cn, 1, t2);
  long long t3 = seg[ee + 3].query(1, 1, cn, ff + tt);
  if (t3 == -1) return;
  fl = 1;
}
void work3(long long qq, long long ww, long long ee, long long ff) {
  if (fl) return;
  long long t1 = seg[qq].query(1, 1, cn, ff);
  if (t1 == -1) return;
  memset(v1, 0, sizeof(v1));
  for (int i = 0; i < qu[ww].size(); i++)
    if (qu[ww][i].q > t1) v1[qu[ww][i].w]++;
  s.build(1, 1, cn);
  memset(v1, 0, sizeof(v1));
  long long t2 = s.query(1, 1, cn, ff);
  if (t2 == -1) return;
  for (int i = 0; i < qu[ee].size(); i++)
    if (qu[ee][i].q > t1) v1[qu[ee][i].w]++;
  s.build(1, 1, cn);
  long long tt = s.query1(1, 1, cn, 1, t2);
  long long t3 = s.query(1, 1, cn, ff + tt);
  if (t3 == -1) return;
  fl = 1;
}
void work4(long long qq, long long ww, long long ee, long long ff) {
  if (fl) return;
  long long t1 = seg[qq + 3].query(1, 1, cn, ff);
  if (t1 == -1) return;
  memset(v1, 0, sizeof(v1));
  for (int i = 0; i < qu[ww].size(); i++)
    if (qu[ww][i].w > t1) v1[qu[ww][i].q]++;
  s.build(1, 1, cn);
  memset(v1, 0, sizeof(v1));
  long long t2 = s.query(1, 1, cn, ff);
  if (t2 == -1) return;
  for (int i = 0; i < qu[ee].size(); i++)
    if (qu[ee][i].w > t1) v1[qu[ee][i].q]++;
  s.build(1, 1, cn);
  long long tt = s.query1(1, 1, cn, 1, t2);
  long long t3 = s.query(1, 1, cn, ff + tt);
  if (t3 == -1) return;
  fl = 1;
}
void work5(long long qq, long long ww, long long ee, long long ff) {
  if (fl) return;
  long long t1 = seg[qq].query2(1, 1, cn, ff);
  if (t1 == -1) return;
  memset(v1, 0, sizeof(v1));
  for (int i = 0; i < qu[ww].size(); i++)
    if (qu[ww][i].q < t1) v1[qu[ww][i].w]++;
  s.build(1, 1, cn);
  memset(v1, 0, sizeof(v1));
  long long t2 = s.query(1, 1, cn, ff);
  if (t2 == -1) return;
  for (int i = 0; i < qu[ee].size(); i++)
    if (qu[ee][i].q < t1) v1[qu[ee][i].w]++;
  s.build(1, 1, cn);
  long long tt = s.query1(1, 1, cn, 1, t2);
  long long t3 = s.query(1, 1, cn, ff + tt);
  if (t3 == -1) return;
  fl = 1;
}
void work6(long long qq, long long ww, long long ee, long long ff) {
  if (fl) return;
  long long t1 = seg[qq + 3].query2(1, 1, cn, ff);
  if (t1 == -1) return;
  memset(v1, 0, sizeof(v1));
  for (int i = 0; i < qu[ww].size(); i++)
    if (qu[ww][i].w < t1) v1[qu[ww][i].q]++;
  s.build(1, 1, cn);
  memset(v1, 0, sizeof(v1));
  long long t2 = s.query(1, 1, cn, ff);
  if (t2 == -1) return;
  for (int i = 0; i < qu[ee].size(); i++)
    if (qu[ee][i].w < t1) v1[qu[ee][i].q]++;
  s.build(1, 1, cn);
  long long tt = s.query1(1, 1, cn, 1, t2);
  long long t3 = s.query(1, 1, cn, ff + tt);
  if (t3 == -1) return;
  fl = 1;
}
bool ch(long long qq) {
  fl = 0;
  work1(1, 2, 3, qq);
  work1(1, 3, 2, qq);
  work1(2, 1, 3, qq);
  work1(2, 3, 1, qq);
  work1(3, 1, 2, qq);
  work1(3, 2, 1, qq);
  work2(1, 2, 3, qq);
  work2(1, 3, 2, qq);
  work2(2, 1, 3, qq);
  work2(2, 3, 1, qq);
  work2(3, 1, 2, qq);
  work2(3, 2, 1, qq);
  work3(1, 2, 3, qq);
  work3(1, 3, 2, qq);
  work3(2, 1, 3, qq);
  work3(2, 3, 1, qq);
  work3(3, 1, 2, qq);
  work3(3, 2, 1, qq);
  work4(1, 2, 3, qq);
  work4(1, 3, 2, qq);
  work4(2, 1, 3, qq);
  work4(2, 3, 1, qq);
  work4(3, 1, 2, qq);
  work4(3, 2, 1, qq);
  work5(1, 2, 3, qq);
  work5(1, 3, 2, qq);
  work5(2, 1, 3, qq);
  work5(2, 3, 1, qq);
  work5(3, 1, 2, qq);
  work5(3, 2, 1, qq);
  work6(1, 2, 3, qq);
  work6(1, 3, 2, qq);
  work6(2, 1, 3, qq);
  work6(2, 3, 1, qq);
  work6(3, 1, 2, qq);
  work6(3, 2, 1, qq);
  return fl;
}
int main() {
  scanf("%lld", &a);
  for (int i = 1; i <= a; i++) {
    scanf("%lld%lld%lld", &q, &w, &e);
    qu[e].push_back(p{q, w, i});
    u[++cn] = q;
    u[++cn] = w;
  }
  sort(u + 1, u + cn + 1);
  cn = unique(u + 1, u + cn + 1) - u - 1;
  for (int i = 1; i <= 3; i++)
    for (int j = 0; j < qu[i].size(); j++)
      qu[i][j].q = lower_bound(u + 1, u + cn + 1, qu[i][j].q) - u,
      qu[i][j].w = lower_bound(u + 1, u + cn + 1, qu[i][j].w) - u;
  for (int i = 1; i <= 3; i++) {
    memset(v1, 0, sizeof(v1));
    memset(v2, 0, sizeof(v2));
    for (int j = 0; j < qu[i].size(); j++) v1[qu[i][j].q]++, v2[qu[i][j].w]++;
    for (int j = 1; j <= cn; j++) {
      seg[i].change(1, 1, cn, j, v1[j]);
      seg[i + 3].change(1, 1, cn, j, v2[j]);
    }
  }
  long long ll = 1, rr = a / 3;
  while (ll <= rr) {
    long long mid = ((ll + rr) >> 1);
    if (ch(mid))
      ll = mid + 1, ann = mid;
    else
      rr = mid - 1;
  }
  printf("%lld", ann * 3);
  return 0;
}
