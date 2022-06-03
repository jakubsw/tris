import csv
import json

class ArticleRank:
    """Calculates ArticleRank"""
    def get_mean_ref_count(self):
        """Calculates mean number of references"""
        cnt_refs = 0
        for w in self.dataset:
            cnt_refs += len(w[2])            
        return cnt_refs / len(self.dataset)

    def calc_ar1(self):
        """Calculates one iteration of ArticleRank data"""
        ar = self.ar1.copy()
        for v in self.dataset:
            d = 1 / (len(v[2]) + self.mr)
            for w in v[2]:
                ar[str(w)] += self.ar[v[0]] * d 
        return ar

    def calc_ar(self, dataset, iteration = 40, df = 0.85):
        """Initializes and calculates ArticleRank data"""
        self.dataset = dataset
        self.ar = {}
        for w in dataset:
            self.ar[w[0]] = 1.0 - df
        self.ar1 = self.ar.copy()
        self.mr = self.get_mean_ref_count()
        for i in range(iteration - 1):
            self.ar = self.calc_ar1()
        return self.ar

class TRIS:
    def load_data(self, fn):
        """Loads citation network data"""
        with open(fn, encoding="utf8") as json_file:
            self.data = json.load(json_file)
            
    def sort_works(self):
        """Sorts works by: year DESC, same-year citations ASC, citations ASC"""
        self.works.sort(key = lambda x: (-x[1], x[4], x[3]))
                
    def init_counters(self):
        """Zeroes the counters to calculate TRIS"""
        self.works = []
        self.cnt_refs = 0
        for w in self.data["works"]:    
            wv = self.data["works"][w]
            wv["ft"] = 0.0
            wv["tt"] = 0.0
            wv["cn"] = 0
            wv["sycn"] = 0
            if wv['w_year']:
                self.works.append( [w, int(wv['w_year']), wv['w_refs'], 0, 0] )
                
    def calc_citations(self):
        """Calculates the fixed part of TRIS"""
        for p in self.works:
            td = len(p[2])
            self.cnt_refs += td
            td += max(9, td) 
            td = 1 / td
            self.data["works"][p[0]]["td"] = td
            y = self.data["works"][p[0]]["w_year"]
            for r in p[2]:              
                rw = self.data["works"][str(r)]
                rw["cn"] += 1
                rw["ft"] += td
                if y == rw["w_year"]:
                    rw["sycn"] += 1
        for p in self.works:
            wv = self.data["works"][p[0]]
            p[3] = wv["cn"]
            p[4] = wv["sycn"]

    def calc_transitive(self):
        """Calculates the transitive part of TRIS"""
        for p in self.works:            
            ft = self.data["works"][p[0]]["ft"]
            tt = self.data["works"][p[0]]["tt"]  
            td = ft + tt  * self.data["works"][p[0]]["td"]  
            for r in p[2]:              
                rw = self.data["works"][str(r)]
                rw["tt"] += td          
                 
    def tris(self, paper):
        """Returns TRIS of a given paper"""
        p = self.data["works"][str(paper)]
        return p["ft"] + p["tt"]

    def cit_no(self, paper):
        """Returns citation number of a given paper"""
        return self.data["works"][str(paper)]["cn"]

    def same_year_cit_no(self, paper):
        """Returns same-year citation number of a given paper"""
        return self.data["works"][str(paper)]["sycn"]

    def article_rank(self, paper):
        """Returns ArticleRank of a given paper"""
        if 'ar' not in self.__dict__:
            self.ar = ArticleRank()
            self.ar.calc_ar(self.works)
        return self.ar.ar[paper]

    def save_to_csv(self, fn):
        with open(fn, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Id','Year','CitNum','SameYearCitNum',
                             'ArticleRank', 'TRIS'])
            for p in self.works:
                r = [p[0], p[1], p[3], p[4], self.article_rank(p[0]),
                     self.tris(p[0])]
                writer.writerow(r)    
        
    def __init__(self, fn):
        """Loads, initializes and calculates TRIS data"""
        self.load_data(fn)
        self.init_counters()
        self.calc_citations()       
        self.sort_works()
        self.calc_transitive()
        
# example of use:
t = TRIS("graph (5).json")
print('Works:',len(t.data["works"]),'Connected:',len(t.works),
      'Connections:',t.cnt_refs,
      'Mean Citation Number:', t.cnt_refs/len(t.data["works"]))
t.save_to_csv("test1.csv")


