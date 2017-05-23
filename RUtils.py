import os

user=os.getenv('USER')

def check_tmp_dir():
    if not os.path.isdir('/tmp/'+user): os.system('mkdir -p /tmp/'+user)
    return
        

def write_to_csv(df, name='/tmp/'+user+'/tmp.csv'):
    check_tmp_dir()
    df.to_csv(name)
    return

def Rscript(fname='/tmp/'+user+'/tmp.R', code="", ):
    check_tmp_dir()
    buf="""#!/usr/bin/env Rscript
    """
    
    f=open(fname,'w')
    f.write(buf+code)
    f.close()
    os.system('chmod +x '+fname)
    os.system(fname)
    return
    

def Run(code="print('never again')"):
    check_tmp_dir()
    Rscript(code=code)
    pass

def Smooth(df, col):
    check_tmp_dir()

    write_to_csv(df)

    """
    library(wavethresh)
    """
