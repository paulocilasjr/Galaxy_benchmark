import sys

def readfq(p):
    r=[]
    with open(p) as h:
        while True:
            n=h.readline().rstrip('\n')
            if not n: break
            s=h.readline().rstrip('\n')
            h.readline()
            q=h.readline().rstrip('\n')
            r.append((n,s,q))
    return r
mix=readfq(sys.argv[1]); exo=readfq(sys.argv[2])
if len(mix) >= len(exo) and mix[:len(exo)] == exo:
    pct=round((len(exo)/len(mix))*100/10)*10
    ans=str(int(pct))
else:
    ans='NA'
open(sys.argv[3],'w').write(ans+'\n')
