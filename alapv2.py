####################################################################################################
#   ALAP 2.0 : A program that generates alap from an example set of alaps
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
import difflib

# list containing alaps
#alap_list = []

filename = 'raga_data/malhar.txt'

myduration = 0.75
transpose = 4


char_list = ['-','[',']']
v_aaroh=[]
v_avroh=[]
mukhda=[]
max_gap = 4

score_max_gap = -1
score_v_aaroh = -10
score_v_avroh = -10
score_end_SP  = -1
score_dash    = -1
pass_score = 0
similarity_sort = True

# length of alap (no. of beats)
length = 16
number_of_alaps = 8

chosen_instrument = music21.instrument.Piano()


# dictionary mapping swaras to codes
swar_code = {'S':61, 'r':62, 'R':63, 'g':64,'G':65,'m':66,'M':67,'P':68,'d':69,'D':70,'n':71,'N':72,'-':'-','[':'[',']':']'}
# inverse mapping using map and reversed 
swar = dict(map(reversed, swar_code.items()))

pattern_cnt = Counter()
temp_list=[]
played_list=[]

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

def similarity(s1,s2):
    sm=difflib.SequenceMatcher(None,s1,s2)
    return sm.ratio()

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
        
    j=len(mylist)-1
    while j>0 and  mylist[j] in char_list:
        if mylist[j]=='-':
            count_beg_dash+=1
        j-=1
    if count_beg_dash%2!=1:
        ret+=score_dash
    for i in range(1,length):
        if mylist[i]=='-':
            count+=1
            
        if (mylist[i]=='-' or i==length-1) and mylist[i-1]!='-':
            j=i
            while j>0 and  mylist[j] in char_list:
                j=j-1
            n2=mylist[j]
            j=j-1
            while j>0 and  mylist[j] in char_list:
                j=j-1
            n1=mylist[j]
            if n1 not in char_list:
                if n1<=n2 and n2 not in v_aaroh:
                    ret=ret+score_v_aaroh
                if n1>=n2 and n2 not in v_avroh:
                    ret=ret+score_v_avroh
        if i==length-1:
            j=i
            while j>0 and  mylist[j] in char_list:
                j=j-1
            n2=mylist[j]
            if n2 not in char_list:
                if n2%12 != 68%12 and n2%12 != 61%12:
                    ret += score_end_SP
        if score_max_gap!=0:
            if mylist[i] not in char_list:
                j=i-1
                while j>0 and  mylist[j] in char_list:
                    j=j-1
                if mylist[j] not in char_list:
                    if abs(mylist[i]-mylist[j]) > max_gap:
                        ret = ret + score_max_gap
    for i in range(length-1):
         if mylist[i]=='-' and mylist[i+1]!='-':
            if i%2==0:
                j=i+1
                while j<length and mylist[j]!='-':
                    j+=1
                if j%2!=0:
                    ret+=score_dash
    if count>length/4:
        ret+=score_dash        
    return ret

def pass_list(mylist):
    global pass_score
    if score(mylist)<pass_score:
        return False
    return True

def key_similarity(mylist):
    global temp_list
    return similarity(temp_list,mylist)

def random_alap(parsed_strs, length):
    mylist=parsed_strs[random.randrange(0,len(parsed_strs))]
    if len(mylist)==length:
        return mylist
    elif len(mylist)<length:
        return mylist+random_alap(parsed_strs, length-len(mylist))
    else:
        return random_alap(parsed_strs, length)

def random_alap_2(parsed_strs,length):
    if ['-'] not in parsed_strs:
        parsed_strs.append(['-'])
    while True:
        mylist=parsed_strs[random.randrange(0,len(parsed_strs))]
        if len(mylist)<length:
            r=random_alap_2(parsed_strs,length-len(mylist))
            return random.choice([r+mylist, mylist+r])
        elif len(mylist)==length:
            return mylist
        else:
            continue

def calc_len(string):
    length=0
    level_cnt=0
    for i in range(len(string)):
        if level_cnt==0:
            length+=1
        if string[i]=='[':
            level_cnt+=1
        elif string[i]==']':
            level_cnt-=1
    return length
        
            
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
            mystream.append(music21.note.Note(n+transpose,quarterLength=myduration))

    #mystream.show('midi')    

def play_taan():
    mystream = music21.stream.Stream()
    mystream.append(chosen_instrument)
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
    global similarity_sort
    global number_of_alaps
    global temp_list
    global played_list
    global filename
    global length
    
    #read from file
    strs = []
    with open(filename) as f:
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
    if mukhda!=[]:
        mukhda=parse(mukhda[1])
        print(mukhda)
    print(v_aaroh)
    print(v_avroh)
    length = calc_len(mukhda)
    print("length :",length)

    #remove duplicate chalans
    res = [] 
    [res.append(x) for x in strs if x not in res]
    strs = res
    
    strs.append(['-'])
    
    parsed_strs = []
    for mystr in strs:
        parsed_strs.append(parse(mystr))
    print(parsed_strs)

    #______________________________________________________________play
    mystream = music21.stream.Stream()
    #instrument
    mystream.append(chosen_instrument)
    played_list=[]
    for i in range(number_of_alaps):
        count=0
        while count<length**3:
            mylist = random_alap_2(parsed_strs,length)
            if mylist not in played_list and pass_list(mylist)==True:
                played_list.append(mylist)
                break
            count+=1
    played_list=played_list[:number_of_alaps]
    if similarity_sort==True:
        #temp_list=played_list[0]
        #temp_list = ["-"]*len(played_list[0])
        temp_list=mukhda
        played_list.sort(key=key_similarity, reverse=True)
        
    print("Alap : ")
    play(mukhda, mystream)
    for mylist in played_list:#[min(number_of_alaps,length_alap_list):]:
        play(mukhda[:length//2], mystream)
        play(mylist, mystream,myduration/2)
        print(' '.join(map(str,unparse(mylist))) )
    play(mukhda, mystream)
    
    played_list_random=[]
    
    print("Random Alap : ")
    for i in range(number_of_alaps):
        count=0
        while count<length**2:
            mylist = random_alap_2(parsed_strs,length)
            if mylist not in played_list_random:
                played_list_random.append(mylist)
                break
            count+=1
    if similarity_sort==True:
        temp_list=mukhda
        played_list_random.sort(key=key_similarity, reverse=True)
    for mylist in played_list_random:
        play(mukhda[:length//2], mystream)
        play(mylist, mystream,myduration/2)
        print(' '.join(map(str,unparse(mylist))) )
    play(mukhda, mystream)
    
    mystream.show('midi')


#___calls________________________________________________________________________________________________

alap_main()


#___might_be_useful_______________________________________________________________________________________

    #parsed_strs.append(''.join(map(str, parse(mystr))))

    #for mystr in alap_list[:20]:
    #    print(' '.join(map(str, unparse(mystr))) )
        
    #print(*parsed_strs, sep="\n")
    #for mystr in parsed_strs:
    #    print(unparse(mystr))
