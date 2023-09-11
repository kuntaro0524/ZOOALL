                        #score_array.append((gxyz,total_score))


xyz1=[0,1,0]
xyz2=[1,1,2]
xyz3=[1,1,1.5]
xyz4=[1,1,1]

score1=3
score2=4
score3=5
score4=1


lll=[]

lll.append((xyz1,score1))
lll.append((xyz2,score2))
lll.append((xyz3,score3))
lll.append((xyz4,score4))

#>>> persons = [('Yoshida', 30), ('Suzuki', 100), ('Tanaka', 15)]
for l in lll:
	print(l[1])
print(lll)
l2=sorted(lll, key=lambda x: x[1])
l3=sorted(lll, key=lambda x: x[1],reverse=True)
print(l2)
print(l3)

"""
def compCryScore(x,y):
        a=x.score_total
        b=y.score_total
        if a==b: return 0
        if a<b: return 1
        return -1
"""

"""
                def compCryScore(x,y):
                        a=x.score_total
                        b=y.score_total
                        #print "SCORE COMPARE",a,b
                        if a==b: return 0
                        if a<b: return 1
                        return -1
                        #print thresh_nspots,crysize
"""
