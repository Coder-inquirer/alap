####################################################################################################
#   PLAYER : A program that PLAYS NOTES WRITTEN IN .txt FILES
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
import music21

# list containing alaps
alap = defaultdict()
#alap_list = []

# length of alap (no. of beats)
length = 8

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
       
    
            
def play(mystr, mystream, myduration=0.75):
    for n in mystr:
        if n=='-':
            lastnote=mystream[len(mystream)-1]
            del mystream[len(mystream)-1]
            lastnote.duration.quarterLength+=myduration
            mystream.append(lastnote)
        elif n=='[':
            myduration/=2
        elif n==']':
            myduration*=2
        else:
            mystream.append(music21.note.Note(n,quarterLength=myduration))
    
    
def alap_main( myduration = 4):
    
    #read from file
    strs = []
    with open('bhairav_bandish.txt') as f:
        strs = f.read().splitlines()
    
    parsed_strs = []
    for mystr in strs:
        parsed_strs.append(parse(mystr)) 
    #print(*parsed_strs, sep="\n")
    
    #for mystr in parsed_strs:
    #    print(unparse(mystr))

    mystream = music21.stream.Stream()
    mystream.append(music21.instrument.Sitar())
    for mystr in parsed_strs[:10]:
        play(mystr, mystream)
        print(' '.join(map(str, mystr)) )
    #p=music21.graph.plot.HistogramPitchSpace(mystream)
    #p.run()
    mystream.show('midi')
    #for mystr in alap_list:
    #    print(' '.join(map(str, unparse(mystr))) )

#___calls________________________________________________________________________________________________

alap_main()


#___might_be_useful_______________________________________________________________________________________

#parsed_strs.append(''.join(map(str, parse(mystr)))) 
