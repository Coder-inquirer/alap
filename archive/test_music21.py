from music21 import *

n = note.Note(61)
n.offset
#n.duration.type = 'half'
#n.show('midi')
print(n.duration)
mystream = stream.Stream()
mystream.append(note.Note(61))
mystream.append(note.Rest())
mystream.append(note.Note(61))
mystream.append(note.Note(61))
mystream.show('midi')
