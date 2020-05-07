import logging,sys,getopt,time
logging.getLogger("scapy.runtime").setLevel(logging.ERROR) 
 
from scapy.all import *
from scapy.all import RandMAC


def sending_probe(frame, inter=0, count=None, verbose=None, *args, **kargs):
    __gen_sending_probe(conf.L2socket(*args, **kargs), frame, inter=inter, count=count, verbose=verbose)


def __gen_sending_probe(s, frame, inter=0, count=None, verbose=None, *args, **kargs):
    """Send probe requests. 

    Args:
        s: Input args.
        frame: Formatted frame content. 
        inter: Interval. 
        count: Package number expected to send. 
        verbose: Determain wheter display result. 
    """
    if type(frame) is str:
        frame = conf.raw_layer(load=frame)
    if not isinstance(frame, Gen):
        frame = SetGen(frame)
    if verbose is None:
        verbose = conf.verb
    n = 0
    if count is None:
        count = 1
    try:
        while count:
            last_time = 0
            for p in frame:
                now_time = time.clock()
                while (now_time - last_time < inter):
                    now_time = time.clock()
                last_time = now_time
                s.send(p)
                n += 1
                print("Packet No.%s sent." %(n))
                count -= 1
    except KeyboardInterrupt:
        pass
    s.close()
    if verbose:
        print ("\nSent %i packets." % n)


def main():
    iface = 'wlp3s0'
    interval = 1000
    count = 100
    # mac = 'f8:62:14' # Allocated to Apple
    machead = 'da:a1:19' # Allocated to  Google
    mac = 'de:fa:lt:ad:dr:es'
    help_msg = '''-i <interface>
    -n <packs> Package number expected to send.
    -r Use random MAC address, default is random MAC. 
    -h <machead> format: ??:??:??, this option only works in random mode, default is Google's code(da:a1:19). 
    -m <mac> Use assigned MAC address. format: ??:??:??:??:??:??, this option will override -r and -mh. 
    -t <interval>
    '''
    #opts
    try:
        opts,args = getopt.getopt(sys.argv[1:],"i:n:t:rh:m:")
    except getopt.GetoptError as e:
        print ("ERR:"+e.msg+"\n"+help_msg)
        sys.exit(-1)
    
    mac_flag = 1
    for opt, arg in opts:
        if opt == '-i':
            iface = arg
        elif opt == '-n':
            count = int(arg)
        elif opt == '-t':
            interval = float(arg)
        elif opt == '-r':
            machead = 'da:a1:19'
        elif opt == '-h':
            machead = arg
        elif opt == '-m':
            mac = arg
            mac_flag = 0
    if mac_flag:
        print ("iface=%s, packs=%d, machead=%s, interval=%f" %(iface,count,machead,interval))
    else:
        print ("iface=%s, packs=%d, mac=%s, interval=%f" %(iface,count,mac,interval))
    
    s_time = time.time()
    print ("start time:%f" % s_time)
    print( "Press CTRL+C to Abort")
    
    if mac_flag:
        sending_probe(RadioTap()/
            Dot11(type=0,subtype=4,
            addr1="ff:ff:ff:ff:ff:ff",
            addr2=RandMAC(machead),
            addr3="ff:ff:ff:ff:ff:ff")/
            Dot11Elt(ID='DSset',info='\x01')/
            Dot11Elt(ID='Rates',info='\x02\x04\x0b'),
            iface=iface,count=count,inter=interval,verbose=1)
        e_time = time.time()
        print ("end time=%f, spend time=%f" %(e_time, e_time - s_time))
    else: 
        sending_probe(RadioTap()/
            Dot11(type=0,subtype=4,
            addr1="ff:ff:ff:ff:ff:ff",
            addr2=mac,
            addr3="ff:ff:ff:ff:ff:ff")/
            Dot11Elt(ID='DSset',info='\x01')/
            Dot11Elt(ID='Rates',info='\x02\x04\x0b'),
            iface=iface,count=count,inter=interval,verbose=1)
        e_time = time.time()
        print ("end time=%f, spend time=%f" %(e_time, e_time - s_time))
    
if __name__ == "__main__":
    main()