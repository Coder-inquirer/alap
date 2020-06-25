import math
import wave
import struct
from scipy.signal import chirp
import numpy as np
import matplotlib.pyplot as plt
#_________________________________________________________CONSTANTS_____________
freq = 440.0
data_size = 40000
fname = "WaveTest.wav"
frate = 11025.0  # framerate as a float
amp = 64000.0     # multiplier for amplitude

nchannels = 1
sampwidth = 2
framerate = int(frate)
nframes = data_size
comptype = "NONE"
compname = "not compressed"

#__________________________________________________________GLOBALS_______________

meend=False

phase = 0
prev_ampl=1
duration = 0.5

dampening = False
half_time = duration
half_length = framerate*half_time
half_length_factor = 1

harmonics = []
phases = [0]*len(harmonics)

meend_method = 'linear'

wav_file = wave.open(fname, "w")
wav_file.setparams((nchannels, sampwidth, framerate, nframes,
    comptype, compname))

# dictionary mapping swaras to codes
swar_code = {'S':61, 'r':62, 'R':63, 'g':64,'G':65,'m':66,'M':67,'P':68,'d':69,'D':70,'n':71,'N':72,'-':'-','[':'[',']':']', '(':'(',')':')'}
# inverse mapping using map and reversed 
swar = dict(map(reversed, swar_code.items()))

bhup_pitches=[168.1, 178.6, 173, 192.3, 172.4, 180.2, 200, 181.8, 183.8, 178.6, 192.3, 175.4, 163.9, 156.2, 188.8, 208.3, 215.1, 217.4, 232.6, 227.3, 235.3, 212.8, 208.3, 215.1, 222.2, 206.2, 183.3, 190.5, 188.7, 185.2, 178.6, 188.7, 192.3, 180.2, 185.2, 190.5, 180.2, 188.8, 161.3, 156.2]
#________________________________________________________________________________
#__________________________________________________________CLASSES_______________
    
class Stream:
    def __init__(self):
        self.stream = []    # creates a new empty list for each stream object

    def append(self, note):
        self.stream.append(note)

    def write(self, wavfile = wav_file):
        for entity in self.stream:
            entity.write(wavfile)
            
    def add_duration(self, duration=0):
        self.stream[-1].add_duration(duration)
        
    
#________________________________________________________________________________
class Note:
    def __init__(self, freq, duration=duration):
        self.freq = freq            # an int or char
        self.duration = duration

    def write(self, wavfile = wav_file):
        write_to_wav(wavfile = wav_file, fbeg=self.freq, fend=self.freq, duration=self.duration, pluck=True)

    def add_duration(self, duration=0):
        self.duration+=duration
#________________________________________________________________________________
class Meend:
    def __init__(self, beg, end, duration, pluck=True):
        self.beg = beg              # an int 
        self.end = end              # an int 
        self.duration = duration
        self.pluck = pluck

    def write(self, wavfile = wav_file):
        if self.pluck==True:
            write_to_wav(wavfile = wav_file, fbeg=self.beg, fend=self.end, duration=self.duration, method = meend_method, pluck=True)
        else:
            write_to_wav(wavfile = wav_file, fbeg=self.beg, fend=self.end, duration=self.duration, method = meend_method, pluck=False)
        
    def add_duration(self, duration=0):
        self.duration+=duration

#________________________________________________________________________________
#_____________________________________________________________FUNCTIONS__________


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
                
def play(mystr, mystream, myduration=duration):
    global meend
    meend_count=0
    pluck=True
    for n in mystr:
        if n=='-':
            mystream.add_duration(myduration)
        elif n=='[':
            myduration/=2
        elif n==']':
            myduration*=2
        elif n==')':
            meend=False
            pluck=True
        elif n=='(':
            meend=True
            meend_count=0
        elif meend==True:
            if meend_count!=0:
                mystream.append(Meend(freq(prev),freq(n),duration=myduration, pluck=pluck))
                pluck=False
            prev=n
            meend_count+=1
        else:
            mystream.append(Note(freq(n),duration=myduration))
            prev=n

def freq(note):       #takes int, returns freq
    a = 440                 #frequency of A (common value is 440Hz)
    return (a / 32) * (2 ** ((note - 9) / 12))

def endphase(p1,p2,half_ampl=1):
    theta = math.degrees(math.acos(p2/half_ampl))
    if p2>p1:
        theta = 360 - theta
    return theta

def smoothen_end(sine_arr_x,fraction=0.01):
    beg = int((1-fraction)*len(sine_arr_x))
    end = len(sine_arr_x)
    for i in range(beg,end):
        sine_arr_x[i]*=(end-i)/(end-beg)
def smoothen_beg(sine_arr_x,fraction=0.01):
    beg = 0
    end = int(fraction*len(sine_arr_x))
    for i in range(beg,end):
        sine_arr_x[i]*=(i)/(end-beg)

def damper(x):
    return math.exp(-x/half_length)
def dampen(sine_arr_x, half_length=half_length):
    global prev_ampl
    for i in range(len(sine_arr_x)):
        sine_arr_x[i]*=math.exp(-i/half_length)
    
def write_to_wav(fbeg=freq, fend=freq, wavfile=wav_file, duration=duration, frate=frate, method='linear', pluck=True):
    global phase
    global dampen
    global harmonics
    global prev_ampl
    global half_length
    global half_length_factor
    
    phase+=360*fbeg/frate
    t = np.linspace(0, duration, int((duration)*frate))
    sine_arr_x = chirp(t, f0=fbeg, f1=fend, t1=duration, method=method, vertex_zero=False, phi=phase)
    phase = endphase(sine_arr_x[-2], sine_arr_x[-1])
    
    
    for i in range(len(harmonics)):
        factor = i+2
        ch = chirp(t, f0=factor*fbeg, f1=factor*fend, t1=duration, method=method, vertex_zero=False, phi=phases[i])
        sine_arr_x += harmonics[i]*ch
    
    if pluck==False and dampening==True:
        sine_arr_x*=prev_ampl
    else:
        prev_ampl = 1
    #if pluck ==True:
        #smoothen_beg(sine_arr_x,fraction=0.01)
        #smoothen_end(sine_arr_x,fraction=0.01)

    if dampening==True:
        dampen(sine_arr_x)
        prev_ampl*=math.exp(-(len(sine_arr_x)-1)/half_length)
    
    

    sine_arr_x/=1+sum(map(float,harmonics))
    print(sine_arr_x[0],sine_arr_x[1],sine_arr_x[2],sine_arr_x[3],sine_arr_x[-2],sine_arr_x[-1])
    for s in sine_arr_x:
        # write the audio frames to file
        wav_file.writeframes(struct.pack('h', int(s*amp/2)))
    



#________________________________________________________________________________
#______________________________________________________________MAIN______________    

mystream = Stream()
for i in range(1,len(bhup_pitches)):
    print(i)
    mystream.append(Meend(2*bhup_pitches[i-1],2*bhup_pitches[i],duration=0.1, pluck=True))
"""
#read from file
strs = []
with open('bhairav_bandish_copy.txt') as f:
    strs = f.read().splitlines()

parsed_strs = []
for mystr in strs:
    parsed_strs.append(parse(mystr)) 
#print(*parsed_strs, sep="\n")
for mystr in parsed_strs[:10]:
    play(mystr, mystream)
    print(' '.join(map(str, mystr)) )
"""
mystream.write()
wav_file.close()


#________________________________________________________________________________
#________________________________________________________________________________



"""
phase = 0    
#write_to_wav(freq(71),freq(71))
#write_to_wav(freq(69),freq(68), duration = 1, method="quadratic")
write_to_wav(freq(68),freq(68), duration = 1)
#write_to_wav(freq(69),freq(68), duration = 1, method="quadratic")
write_to_wav(freq(68),freq(68), duration = 1)
write_to_wav(freq(67),freq(67))
wav_file.close()    
"""



"""
t_beg=0.0
t_end=1.0
fa=277.18
fb=415.3047
#sine_list_x = []
#for x in range(data_size):
#    sine_list_x.append(math.sin(2*math.pi*freq*(x/frate)))

t = np.linspace(t_beg, t_end, int((t_end-t_beg)*frate))
sine_list_x = chirp(t, f0=fa, f1=fb, t1=t_end, method='quadratic', phi=-90)
sine_list_x2 = chirp(t, f0=fb, f1=fa, t1=t_end, method='linear')
#np.append(sine_list_x,sine_list_x2)

plt.plot(sine_list_x[:100])
plt.show()


"""
"""
for s in sine_list_x:
    # write the audio frames to file
    wav_file.writeframes(struct.pack('h', int(s*amp/2)))
for s in sine_list_x2:
    # write the audio frames to file
    wav_file.writeframes(struct.pack('h', int(s*amp/2)))
"""




