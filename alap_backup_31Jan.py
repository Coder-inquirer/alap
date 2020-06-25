####################################################################################################
#   ALAP : A program that generates alap from an example set of alaps
#
#   works effortlessly even for 16 beat length
# functions:
#
#  structure(list of char)
#       identifies patterns in the examples , for example, "SRG-GRS-" has the structure "ABC-BCA-"
#
#  score(list of char)
#       gives a score to the inputted string
#____________________________________________________________________________________________________


from collections import *
import music21
import random

# list containing alaps
#alap_list = []

myduration = 0.8

char_list = ['-','[',']']
v_aaroh=[]
v_avroh=[]
mukhda=[]
max_gap = 4

score_max_gap = 0
score_v_aaroh = -10
score_v_avroh = -10
score_end_SP  = -1
score_dash    = -2
pass_score = -1

# length of alap (no. of beats)
length = 16

# dictionary mapping swaras to codes
swar_code = {'S':61, 'r':62, 'R':63, 'g':64,'G':65,'m':66,'M':67,'P':68,'d':69,'D':70,'n':71,'N':72,'-':'-','[':'[',']':']'}
# inverse mapping using map and reversed 
swar = dict(map(reversed, swar_code.items()))

pattern_cnt = Counter()

def parse(mystr):
    retstr = []
    for s in mystr:
        if s == '.':
            popped=retstr.pop()
            retstr.append(popped-12)
        elif s == "'":
            popped=retstr.pop()
            retstr.append(popped+12)
        elif s==' ' or s==';':
            continue
            #retstr.append(swar_code['-']) 
        else:
            retstr.append(swar_code[s])  
    return retstr

def unparse(mylist):
    retstr = []
    for i in mylist:
        if i =='-':
            retstr.append(swar[i])
        elif int(i)<61:
            retstr.append(str(swar[i+12])+".")
        elif int(i)>72:
            retstr.append(str(swar[i-12])+"'")
        else:
            retstr.append(str(swar[i]))
    return retstr
    
def score(mylist):
    ret = 0
    #v_aaroh/v_avroh
    global v_aaroh
    global v_avroh
    global char_list
    global max_gap
    global score_v_aaroh
    global score_v_avroh
    global score_max_gap
    global score_end_SP
    global score_dash
    
    length = len(mylist)
    count  = 0
    count_beg_dash=0
    j=0
    while j<length and  mylist[j] in char_list:
        if mylist[j]=='-':
            count_beg_dash+=1
        j+=1
    if count_beg_dash%2==1:
        ret+=score_dash
    for i in range(1,length):
        if mylist[i]=='-':
            count+=1
        if (mylist[i]=='-' or i==length-1) and mylist[i-1]!='-':
            j=i
            while j>0 and  mylist[j] in char_list:
                j=j-1
            n2=mylist[j]
            n2_j=j #hack: works only when there are no [ or ]
            j=j-1
            while j>0 and  mylist[j] in char_list:
                j=j-1
            n1=mylist[j]
            if n1 not in char_list:
                if n1<=n2 and n2 not in v_aaroh:
                    ret=ret+score_v_aaroh
                if n1>=n2 and n2 not in v_avroh:
                    ret=ret+score_v_avroh
            if (n2%12 != 68%12 and n2%12 != 61%12):
                ret += score_end_SP
            if (length-1-n2_j)%2==0:
                ret +=score_dash
      
     #   if mylist[i] not in char_list:
     #       j=i-1
     #       while j>0 and  mylist[j] in char_list:
     #           j=j-1
     #       if mylist[j] not in char_list:
     #           if abs(mylist[i]-mylist[j]) > max_gap:
     #               ret = ret + score_max_gap
     
    if count>length/3:
        ret+=score_dash        
    return ret

def pass_list(mylist):
    global pass_score
    if score(mylist)<pass_score:
        return False
    return True
    

def compose(parsed_strs, length=4):
    alap_list_ret = []
    # do a DFS to populate the alap_list with all possible combinations
    compose_dfs(alap_list_ret, parsed_strs, length)
    print("Initial noo. of alaps : ",len(alap_list_ret))
    #remove duplicates
    return alap_list_ret

def compose_dfs(alap_list, parsed_strs, length, seq=[]):
    for mystr in parsed_strs:
        if len(mystr)<length:
            compose_dfs(alap_list, parsed_strs, length-len(mystr), seq+mystr)
        elif len(mystr)>length:
            continue
        else:
            alap_list.append(seq+mystr)

            
def compose2(parsed_strs, length=8):
    dfs_list = []
    for i in range(length):
        dfs_list.append([])
    print(dfs_list)
    # do a DFS to populate the dfs_list with all possible combinations
    compose_dfs2(dfs_list, parsed_strs, length)
    
    alap_list_ret = dfs_list[length-1]
    
    print("Initial noo. of alaps : ",len(alap_list_ret))
    return alap_list_ret


def compose_dfs2(dfs_list, parsed_strs, length):
    for mystr in parsed_strs:
        if len(mystr)<length:
            if len(dfs_list[length-len(mystr)-1])==0:
                compose_dfs2(dfs_list, parsed_strs, length-len(mystr))
            for subseq in dfs_list[length-len(mystr)-1]:
                dfs_list[length-1].append(subseq+mystr)
        elif len(mystr)>length:
            continue
        else:
            dfs_list[length-1].append(mystr)
            
def play(mylist, mystream, myduration = myduration):
    for n in mylist:
        if n=='-':
            lastnote=mystream[len(mystream)-1]
            del mystream[len(mystream)-1]
            lastnote.duration.quarterLength+=myduration
            mystream.append(lastnote)
            #mystream.append(music21.note.Rest(quarterLength=myduration))
        elif n=='[':
            myduration/=2
        elif n==']':
            myduration*=2
        else:
            mystream.append(music21.note.Note(n,quarterLength=myduration))

    #mystream.show('midi')    

def play_taan():
    mystream = music21.stream.Stream()
    mystream.append(music21.instrument.Lute())
    for i in range(16):
        #append_mukhda(mystream)
        mylist = alap_list[random.randrange(0,length_alap_list,1)]
        play(mukhda[:length//2], mystream)
        play(mylist, mystream,myduration/2)
        print(' '.join(map(str, mylist)) )
    mystream.show('midi')
    
def alap_main():
    global length
    global v_aaroh
    global v_avroh
    global mukhda
    global myduration
    
    #read from file
    strs = []
    with open('bhairav.txt') as f:
        strs = f.read().splitlines()

    to_delete=[]
    for s in strs:
        if s[0]=='%':
            to_delete.append(s)
            if "%v_aaroh" in s:
                v_aaroh=s.split(":")
                continue
            elif "%v_avroh" in s:
                v_avroh=s.split(":")
            elif "%mukhda" in s:
                mukhda=s.split(":")
                    
    while len(to_delete)!=0:
        strs.remove(to_delete.pop())

    v_aaroh=parse(v_aaroh[1])
    v_avroh=parse(v_avroh[1])
    mukhda=parse(mukhda[1])
    print(v_aaroh)
    print(v_avroh)
    print(mukhda)

    res = [] 
    [res.append(x) for x in strs if x not in res]
    strs = res    
    strs.append(['-'])         
    #p=0
    #while 2**p<=length:
    #    strs.append(['-']*2**p)
    #    p+=1
    parsed_strs = []
    for mystr in strs:
        parsed_strs.append(parse(mystr))

    #compose
    alap_list=[]
    alap_list = compose(parsed_strs, length)
      
    #alap_list.sort(key=score, reverse=True)
    #alap_list=list(filter(pass_list,alap_list))
    #res = [] 
    #[res.append(x) for x in alap_list if x not in res]
    #alap_list = res
    length_alap_list=len(alap_list)
    print("No.of alaps : ",length_alap_list)
    
    mystream = music21.stream.Stream()
    mystream.append(music21.instrument.Lute())
    played_list=[]
    for i in range(16):
        count=0
        while count<length:
            mylist = alap_list[random.randrange(0,length_alap_list,1)]
            if mylist not in played_list:
                played_list.append(mylist)
                if pass_list(mylist)==True:
                    break
            count+=1
        play(mukhda[:length//2], mystream)
        play(mylist, mystream,myduration/2)
        print(' '.join(map(str,unparse(mylist))) )
    mystream.show('midi')

    #for mystr in alap_list[:20]:
    #    print(' '.join(map(str, unparse(mystr))) )

#___calls________________________________________________________________________________________________

alap_main()


#___might_be_useful_______________________________________________________________________________________

#parsed_strs.append(''.join(map(str, parse(mystr)))) 
        
    #print(*parsed_strs, sep="\n")
    #for mystr in parsed_strs:
    #    print(unparse(mystr))
