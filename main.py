import random
def puint(io):
    ijm=input(io)
    ipp=int(ijm)
    return ipp
muma=puint(":") 
mums=puint(":")
kl=0
mumd=1
opi=0
keypoa=0
keypos=0
keypod=0
keypof=0
keypog=0
while opi<=mums:
    kl=0
    mumd=1    
    opi+=1
    print("<================================>")
    print(opi)
    while kl<muma:
        print("--------------------------------------------------------")
        kli=random.randint(0,1)        
        mumd+=kli
        if mumd==0:
            mumd=1        
        kl+=1
        print(kl)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(mumd)
    if mumd==1:
        keypoa+=1
    if mumd==2:
        keypos+=1
    if mumd==3:
        keypod+=1
    if mumd==4:
        keypof+=1
    if mumd==5:
        keypog+=1
print("+++++++++++++++++++++++++++++++++++")
print(mums)
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print(keypoa)
print(keypos)
print(keypod)
print(keypof)
print(keypog)

        
    
    
    
