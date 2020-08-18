####################################################################################################
#   ALAP : A program that generates alap from an example set of alaps
#
#
# functions:
#
#  structure(list of char)
#       identifies patterns in the examples , for example, "SRG-GRS-" has the structure "ABC-BCA-"
#
#  score(list of char)
#       gives a score to the inputted string
#____________________________________________________________________________________________________


from collections import *

# list containing alaps
alap = defaultdict()
#alap_list = []

# length of alap (no. of beats)
length = 8

# dictionary mapping swaras to codes
swar_code = {'S':61, 'r':62, 'R':63, 'g':64,'G':65,'m':66,'M':67,'P':68,'d':69,'D':70,'n':71,'N':72,'-':'-'}
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

def unparse(mystr):
    retstr = []
    for i in mystr:
        if i =='-':
            retstr.append(swar[i])
        elif int(i)<61:
            retstr.append(str(swar[i+12])+".")
        elif int(i)>72:
            retstr.append(str(swar[i-12])+"'")
        else:
            retstr.append(str(swar[i]))
    return retstr
    
#def score(mystr):

def compose(parsed_strs, length=4):
    alap_list = []
    # do a DFS to populate the alap_list with all possible combinations
    compose_dfs(alap_list, parsed_strs, length)

    #remove duplicates
    res = [] 
    [res.append(x) for x in alap_list if x not in res] 

    return res
    #print(*alap_list, sep="\n")


def compose_dfs(alap_list, parsed_strs, length, seq=[]):
    for mystr in parsed_strs:
        if len(mystr)<length:
            compose_dfs(alap_list, parsed_strs, length-len(mystr), seq+mystr)
        elif len(mystr)>length:
            continue
        else:
            alap_list.append(seq+mystr)
        
    
            
        
        
    
    
def alap_main():
    
    #read from file
    strs = []
    with open('bhairav.txt') as f:
        strs = f.read().splitlines()
    
    for l in range(1,length):
        strs.append(['-']*l)
        
    parsed_strs = []
    for mystr in strs:
        parsed_strs.append(parse(mystr)) 
    #print(*parsed_strs, sep="\n")
    
    #for mystr in parsed_strs:
    #    print(unparse(mystr))

    alap_list=[]
    alap_list = compose(parsed_strs, 8)
    #for mystr in alap_list:
    #    print(' '.join(map(str, mystr)) )
    for mystr in alap_list:
        print(' '.join(map(str, unparse(mystr))) )

#___calls________________________________________________________________________________________________

alap_main()


#___might_be_useful_______________________________________________________________________________________

#parsed_strs.append(''.join(map(str, parse(mystr)))) 
