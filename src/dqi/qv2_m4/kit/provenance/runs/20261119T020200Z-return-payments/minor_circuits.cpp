#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <vector>
using U=uint64_t;
struct Entry{U word;std::array<unsigned char,5> index;};
struct Search {
    std::vector<U> words, labels;std::vector<Entry> entries;
    std::vector<std::array<U,2>> good;std::array<unsigned char,5> temp{};
    int size,n,limit;long long collisions=0;
    void visit(int step,int from,U v){
        if(step==size){entries.push_back({v,temp});return;}
        for(int i=from;i<=n-size+step;i++){temp[step]=i;visit(step+1,i+1,v^words[i]);}
    }
    void test(const Entry&a,const Entry&b){
        std::array<U,2> mask{};for(int j=0;j<size;j++)for(int t:{a.index[j],b.index[j]})if(t<n-1)mask[t/64]^=1ULL<<(t%64);
        U base[64]={};int rank=0,k=0;
        for(int i=0;i<n;i++)if((mask[i/64]>>(i%64))&1){k++;U q=labels[i];while(q){int s=63-__builtin_clzll(q);if(!base[s]){base[s]=q;rank++;break;}q^=base[s];}}
        if(rank+1!=k || k<3)return;
        if(std::find(good.begin(),good.end(),mask)==good.end()&&int(good.size())<limit)good.push_back(mask);
    }
    void run(){
        visit(0,0,0);std::sort(entries.begin(),entries.end(),[](const Entry&a,const Entry&b){return a.word<b.word;});
        for(size_t i=0;i<entries.size();){
            size_t j=i+1;while(j<entries.size()&&entries[j].word==entries[i].word)j++;
            collisions+=1LL*(j-i)*(j-i-1)/2;
            if(int(good.size())<limit)for(size_t a=i;a<j;a++)for(size_t b=a+1;b<j;b++)test(entries[a],entries[b]);
            i=j;
        }
    }
};
int main(int argc,char**v){
    if(argc!=5)return 2;std::ifstream in(v[1]);Search s;s.size=atoi(v[3]);s.limit=atoi(v[4]);in>>s.n;
    if(s.n>128||s.size>5||s.size<2)return 3;
    for(int i=0;i<s.n;i++){U a,w;in>>a>>w;s.labels.push_back(a);s.words.push_back(w);}
    size_t count=1;for(int i=1;i<=s.size;i++)count=count*(s.n-i+1)/i;s.entries.reserve(count);
    s.run();std::ofstream out(v[2]);for(auto m:s.good)out<<m[0]<<" "<<m[1]<<"\n";
    std::cout<<count<<" subsets, "<<s.collisions<<" pairs, "<<s.good.size()<<" good circuits\n";
}
