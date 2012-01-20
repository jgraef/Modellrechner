FILTER = ''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])

def hexdump(src, offset = 0, length=16):
    N=0; result=''
    while src:
        s = "".join(map(chr, src[:length]))
        src = src[length:]
        hexa = ' '.join(["%02X"%ord(x) for x in s])
        s = s.translate(FILTER)
        result += "%04X   %-*s   %s\n" % (N+offset, length*3, hexa, s)
        N+=length
    return result
 
if (__name__=="__main__"):
    text = "This 10 line function is just a sample of pyhton power " +\
           "for string manipulations.\n" +\
           "The code is \x07even\x08 quite readable!"
    test = [ord(c) for c in text]

    print(hexdump(test))
