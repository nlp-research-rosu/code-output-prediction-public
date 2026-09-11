#pragma once

#include <bits/stdc++.h>

namespace __cc_state {
inline long long base_cells = 0;
inline long long container_cells = 0;
inline long long peak_state_size = 0;
inline unsigned long long cumulative_state_load = 0;
inline unsigned long long state_observation_count = 0;

inline void observe() {
  const long long current_state_size = base_cells + container_cells;
  peak_state_size = std::max(peak_state_size, current_state_size);
  cumulative_state_load += static_cast<unsigned long long>(current_state_size);
  ++state_observation_count;
}

inline void change_container(long long delta) {
  container_cells += delta;
  observe();
}

struct binding_guard {
  long long cells;
  explicit binding_guard(long long cell_value) : cells(cell_value) {
    base_cells += cells;
    observe();
  }
  ~binding_guard() {
    base_cells -= cells;
    observe();
  }
  binding_guard(const binding_guard &) = delete;
  binding_guard &operator=(const binding_guard &) = delete;
};

template <class T> struct cell_count {
  static constexpr long long value = 1;
};
template <class T, std::size_t N> struct cell_count<T[N]> {
  static constexpr long long value = 1 + N * cell_count<T>::value;
};
template <class T, std::size_t N> struct cell_count<std::array<T, N>> {
  static constexpr long long value = 1 + N * cell_count<T>::value;
};
template <class A, class B> struct cell_count<std::pair<A, B>> {
  static constexpr long long value =
      1 + cell_count<A>::value + cell_count<B>::value;
};
template <class... T> struct cell_count<std::tuple<T...>> {
  static constexpr long long value = 1 + (cell_count<T>::value + ... + 0);
};

struct reporter {
  ~reporter() {
    std::fprintf(stderr, "\n__CC_STATE_SIZE__ %lld\n", peak_state_size);
    std::fprintf(stderr, "__CC_STATE_LOAD__ %llu\n", cumulative_state_load);
    std::fprintf(stderr, "__CC_STATE_OBSERVATIONS__ %llu\n", state_observation_count);
  }
};
inline reporter final_report;
} // namespace __cc_state

namespace std {
template <class T, class A = allocator<T>> class __cc_vector : public vector<T, A> {
  using B = vector<T, A>;
  using S = typename B::size_type;
  long long cells() const { return 1 + (long long)this->size() * __cc_state::cell_count<T>::value; }
  void born() { __cc_state::change_container(cells()); }
  void changed(long long old) { __cc_state::change_container(cells() - old); }
public:
  __cc_vector() : B() { born(); }
  explicit __cc_vector(const A &a) : B(a) { born(); }
  explicit __cc_vector(S n, const A &a = A()) : B(n, a) { born(); }
  __cc_vector(S n, const T &v, const A &a = A()) : B(n, v, a) { born(); }
  template <class I> __cc_vector(I a, I b, const A &x = A()) : B(a, b, x) { born(); }
  __cc_vector(initializer_list<T> x, const A &a = A()) : B(x, a) { born(); }
  __cc_vector(const __cc_vector &x) : B(static_cast<const B &>(x)) { born(); }
  __cc_vector(__cc_vector &&x) : B(static_cast<const B &>(x)) { born(); }
  __cc_vector(const B &x) : B(x) { born(); }
  ~__cc_vector() { __cc_state::change_container(-cells()); }
  __cc_vector &operator=(const __cc_vector &x) { long long o=cells(); B::operator=(static_cast<const B&>(x)); changed(o); return *this; }
  __cc_vector &operator=(initializer_list<T> x) { long long o=cells(); B::operator=(x); changed(o); return *this; }
  void push_back(const T &x) { long long o=cells(); B::push_back(x); changed(o); }
  void push_back(T &&x) { long long o=cells(); B::push_back(std::move(x)); changed(o); }
  template <class... X> decltype(auto) emplace_back(X&&... x) { long long o=cells(); decltype(auto) r=B::emplace_back(std::forward<X>(x)...); changed(o); return r; }
  void pop_back() { long long o=cells(); B::pop_back(); changed(o); }
  void resize(S n) { long long o=cells(); B::resize(n); changed(o); }
  void resize(S n, const T &x) { long long o=cells(); B::resize(n,x); changed(o); }
  void clear() noexcept { long long o=cells(); B::clear(); changed(o); }
  template <class... X> auto insert(X&&... x) { long long o=cells(); auto r=B::insert(std::forward<X>(x)...); changed(o); return r; }
  template <class... X> auto emplace(X&&... x) { long long o=cells(); auto r=B::emplace(std::forward<X>(x)...); changed(o); return r; }
  auto erase(typename B::const_iterator x) { long long o=cells(); auto r=B::erase(x); changed(o); return r; }
  auto erase(typename B::const_iterator a, typename B::const_iterator b) { long long o=cells(); auto r=B::erase(a,b); changed(o); return r; }
  template <class... X> void assign(X&&... x) { long long o=cells(); B::assign(std::forward<X>(x)...); changed(o); }
};

template <class T, class A = allocator<T>> class __cc_deque : public deque<T, A> {
  using B=deque<T,A>; using S=typename B::size_type;
  long long cells() const { return 1 + (long long)this->size()*__cc_state::cell_count<T>::value; }
  void born(){__cc_state::change_container(cells());} void changed(long long o){__cc_state::change_container(cells()-o);}
public:
  __cc_deque():B(){born();} explicit __cc_deque(S n):B(n){born();} __cc_deque(S n,const T&x):B(n,x){born();}
  template<class I> __cc_deque(I a,I b):B(a,b){born();} __cc_deque(initializer_list<T>x):B(x){born();}
  __cc_deque(const __cc_deque&x):B(static_cast<const B&>(x)){born();} ~__cc_deque(){__cc_state::change_container(-cells());}
  void push_back(const T&x){auto o=cells();B::push_back(x);changed(o);} void push_front(const T&x){auto o=cells();B::push_front(x);changed(o);}
  void pop_back(){auto o=cells();B::pop_back();changed(o);} void pop_front(){auto o=cells();B::pop_front();changed(o);}
  void clear(){auto o=cells();B::clear();changed(o);} void resize(S n){auto o=cells();B::resize(n);changed(o);}
};

template <class K, class V, class C = less<K>, class A = allocator<pair<const K,V>>> class __cc_map : public map<K,V,C,A> {
  using B=map<K,V,C,A>;
  long long cells() const { return 1 + (long long)this->size()*(__cc_state::cell_count<K>::value+__cc_state::cell_count<V>::value); }
  void born(){__cc_state::change_container(cells());} void changed(long long o){__cc_state::change_container(cells()-o);}
public:
  __cc_map():B(){born();} __cc_map(initializer_list<typename B::value_type>x):B(x){born();} __cc_map(const __cc_map&x):B(static_cast<const B&>(x)){born();} ~__cc_map(){__cc_state::change_container(-cells());}
  V& operator[](const K&k){auto o=cells();V&r=B::operator[](k);changed(o);return r;}
  V& operator[](K&&k){auto o=cells();V&r=B::operator[](std::move(k));changed(o);return r;}
  template<class...X> auto insert(X&&...x){auto o=cells();auto r=B::insert(std::forward<X>(x)...);changed(o);return r;}
  template<class...X> auto emplace(X&&...x){auto o=cells();auto r=B::emplace(std::forward<X>(x)...);changed(o);return r;}
  auto erase(const K&k){auto o=cells();auto r=B::erase(k);changed(o);return r;}
  auto erase(typename B::const_iterator x){auto o=cells();auto r=B::erase(x);changed(o);return r;}
  auto erase(typename B::const_iterator a,typename B::const_iterator b){auto o=cells();auto r=B::erase(a,b);changed(o);return r;}
  void clear(){auto o=cells();B::clear();changed(o);}
};

template <class K, class V, class H = hash<K>, class E = equal_to<K>, class A = allocator<pair<const K,V>>> class __cc_unordered_map : public unordered_map<K,V,H,E,A> {
  using B=unordered_map<K,V,H,E,A>;
  long long cells() const { return 1 + (long long)this->size()*(__cc_state::cell_count<K>::value+__cc_state::cell_count<V>::value); }
  void born(){__cc_state::change_container(cells());} void changed(long long o){__cc_state::change_container(cells()-o);}
public:
  __cc_unordered_map():B(){born();} __cc_unordered_map(const __cc_unordered_map&x):B(static_cast<const B&>(x)){born();} ~__cc_unordered_map(){__cc_state::change_container(-cells());}
  V& operator[](const K&k){auto o=cells();V&r=B::operator[](k);changed(o);return r;}
  template<class...X> auto insert(X&&...x){auto o=cells();auto r=B::insert(std::forward<X>(x)...);changed(o);return r;}
  template<class...X> auto emplace(X&&...x){auto o=cells();auto r=B::emplace(std::forward<X>(x)...);changed(o);return r;}
  auto erase(const K&k){auto o=cells();auto r=B::erase(k);changed(o);return r;}
  auto erase(typename B::const_iterator x){auto o=cells();auto r=B::erase(x);changed(o);return r;}
  auto erase(typename B::const_iterator a,typename B::const_iterator b){auto o=cells();auto r=B::erase(a,b);changed(o);return r;}
  void clear(){auto o=cells();B::clear();changed(o);}
};

template <class K, class C = less<K>, class A = allocator<K>> class __cc_set : public set<K,C,A> {
  using B=set<K,C,A>; long long cells()const{return 1+(long long)this->size()*__cc_state::cell_count<K>::value;}
  void born(){__cc_state::change_container(cells());} void changed(long long o){__cc_state::change_container(cells()-o);}
public:
  __cc_set():B(){born();} __cc_set(initializer_list<K>x):B(x){born();} __cc_set(const __cc_set&x):B(static_cast<const B&>(x)){born();} ~__cc_set(){__cc_state::change_container(-cells());}
  template<class...X> auto insert(X&&...x){auto o=cells();auto r=B::insert(std::forward<X>(x)...);changed(o);return r;}
  template<class...X> auto emplace(X&&...x){auto o=cells();auto r=B::emplace(std::forward<X>(x)...);changed(o);return r;}
  auto erase(const K&k){auto o=cells();auto r=B::erase(k);changed(o);return r;}
  auto erase(typename B::const_iterator x){auto o=cells();auto r=B::erase(x);changed(o);return r;}
  auto erase(typename B::const_iterator a,typename B::const_iterator b){auto o=cells();auto r=B::erase(a,b);changed(o);return r;}
  void clear(){auto o=cells();B::clear();changed(o);}
};

class __cc_string : public string {
  using B=string; long long cells()const{return 1+(long long)this->size();}
  void born(){__cc_state::change_container(cells());} void changed(long long o){__cc_state::change_container(cells()-o);}
public:
  __cc_string():B(){born();} __cc_string(const char*x):B(x){born();} __cc_string(const B&x):B(x){born();} __cc_string(const __cc_string&x):B(static_cast<const B&>(x)){born();}
  __cc_string(size_t n,char c):B(n,c){born();} ~__cc_string(){__cc_state::change_container(-cells());}
  __cc_string& operator=(const __cc_string&x){auto o=cells();B::operator=(static_cast<const B&>(x));changed(o);return *this;}
  __cc_string& operator=(const char*x){auto o=cells();B::operator=(x);changed(o);return *this;}
  __cc_string& operator+=(char x){auto o=cells();B::operator+=(x);changed(o);return *this;}
  __cc_string& operator+=(const B&x){auto o=cells();B::operator+=(x);changed(o);return *this;}
  void push_back(char x){auto o=cells();B::push_back(x);changed(o);} void pop_back(){auto o=cells();B::pop_back();changed(o);}
  void resize(size_t n){auto o=cells();B::resize(n);changed(o);} void clear(){auto o=cells();B::clear();changed(o);}
  friend istream& operator>>(istream&in,__cc_string&x){auto o=x.cells();in>>static_cast<B&>(x);x.changed(o);return in;}
};

template<class T,class C=deque<T>> class __cc_queue : public queue<T,C> {
  using B=queue<T,C>; long long cells()const{return 1+(long long)this->size()*__cc_state::cell_count<T>::value;}
  void changed(long long o){__cc_state::change_container(cells()-o);}
public: __cc_queue():B(){__cc_state::change_container(cells());} ~__cc_queue(){__cc_state::change_container(-cells());}
  void push(const T&x){auto o=cells();B::push(x);changed(o);} template<class...X>void emplace(X&&...x){auto o=cells();B::emplace(std::forward<X>(x)...);changed(o);} void pop(){auto o=cells();B::pop();changed(o);}
};
template<class T,class C=deque<T>> class __cc_stack : public stack<T,C> {
  using B=stack<T,C>; long long cells()const{return 1+(long long)this->size()*__cc_state::cell_count<T>::value;} void changed(long long o){__cc_state::change_container(cells()-o);}
public: __cc_stack():B(){__cc_state::change_container(cells());} ~__cc_stack(){__cc_state::change_container(-cells());} void push(const T&x){auto o=cells();B::push(x);changed(o);} void pop(){auto o=cells();B::pop();changed(o);}
};
template<class T,class C=vector<T>,class P=less<typename C::value_type>> class __cc_priority_queue : public priority_queue<T,C,P> {
  using B=priority_queue<T,C,P>; long long cells()const{return 1+(long long)this->size()*__cc_state::cell_count<T>::value;} void changed(long long o){__cc_state::change_container(cells()-o);}
public: __cc_priority_queue():B(){__cc_state::change_container(cells());} ~__cc_priority_queue(){__cc_state::change_container(-cells());} void push(const T&x){auto o=cells();B::push(x);changed(o);} void pop(){auto o=cells();B::pop();changed(o);}
};
} // namespace std

namespace __cc_state {
template<class T,class A> struct cell_count<std::__cc_vector<T,A>> { static constexpr long long value=0; };
template<class T,class A> struct cell_count<std::__cc_deque<T,A>> { static constexpr long long value=0; };
template<class K,class V,class C,class A> struct cell_count<std::__cc_map<K,V,C,A>> { static constexpr long long value=0; };
template<class K,class V,class H,class E,class A> struct cell_count<std::__cc_unordered_map<K,V,H,E,A>> { static constexpr long long value=0; };
template<class K,class C,class A> struct cell_count<std::__cc_set<K,C,A>> { static constexpr long long value=0; };
template<> struct cell_count<std::__cc_string> { static constexpr long long value=0; };
template<class T,class C> struct cell_count<std::__cc_queue<T,C>> { static constexpr long long value=0; };
template<class T,class C> struct cell_count<std::__cc_stack<T,C>> { static constexpr long long value=0; };
template<class T,class C,class P> struct cell_count<std::__cc_priority_queue<T,C,P>> { static constexpr long long value=0; };
}

#define vector __cc_vector
#define deque __cc_deque
#define map __cc_map
#define unordered_map __cc_unordered_map
#define set __cc_set
#define string __cc_string
#define queue __cc_queue
#define stack __cc_stack
#define priority_queue __cc_priority_queue
