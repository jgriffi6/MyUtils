global pd
import pandas as pd

def select(df, criteria, columns=None):
    df2=df[df.eval(criteria)]
    if columns is not None:
        return df2[columns]
    
    return df2

def convert_str_to_dates(df, columns):
    for col in columns:
        df[col]=df[col].map(lambda x: pd.Timestamp(x))
        continue
    pass

def robust_column_names(df):
    d={}
    import re
    reg_str='[-+ *&/\\@]'
    r=re.compile(reg_str)
    for col in df.columns:
        if col=='Unnamed: 0' : continue
        original_name=col
        result=r.search(col)
        while( result is not None):
            col=col.replace(result.group(),'_')
            result=r.search(col)
            continue
        if original_name != col : d[original_name]=col
        continue


    df.rename(index=str, columns=d, inplace=True)

    inverted_d={}
    for a,b in d.items():
        inverted_d[b]=a
        continue
    return inverted_d
                            

def read_excel(name, sheetname='Detail Data', date_cols=[], preselection=''):
    import RUtils,os
    Rcode="library(readxl)"
    Rcode+='\n'+"df=read_excel('%s', sheet='%s')"%(name, sheetname)
    Rcode+='\n'+"write.csv(df,'/tmp/%s/my_csv_from_excel.csv') "%os.getenv('USER')
    RUtils.Rscript(code=Rcode)
    df=pd.read_csv('/tmp/%s/my_csv_from_excel.csv' %os.getenv('USER'))
    try:
        robust_column_names(df)
        convert_str_to_dates(df, date_cols)
    except:
        convert_str_to_dates(df, date_cols)
        robust_column_names(df)
        pass
    if len(preselection): df=df[df.eval(preselection)]
    return df


def make_future(begin, end=None, freq='d', periods=100, col_name='date'):
    if end is not None:
        periods=(pd.Timestamp(end)-pd.Timestamp(begin)).days
        if freq=='h': periods*=24
        pass

    dates=[]
    begin=pd.Timestamp(begin, freq=freq)
    for i in range(0, periods):
        dates.append(begin)
        begin+=1
        continue

    return pd.DataFrame( {col_name: dates} )


def make_columns_with_simple_lambda(df, d={}, col=''):
    for name,method in sorted(d.items()):
        if type(method)==str :
            df[name]=df[col].map(lambda x: x.__getattribute__(method))
            pass
        else :
            df[name]=df[col].map(lambda x: method(x))
            pass
        continue
    return df

def drop_unnamed(df):
    cols=[]
    for col in df.columns:
        if col.count('Unnamed:'): cols.append(col)
        continue
    df.drop(cols, axis=1, inplace=True)

def read_csv(fname, parse_dates=True, ignore_date_cols=[], do_robust_column_names=True, encoding='utf-8', quiet=False, append_to=None):
    date_cols=[]
    import re
    reg=re.compile('[0-9]{2}:[0-9]{2}:[0-9]{2}')
    df=None
    files=[]
    if type(fname) != list: files=[fname]
    else: files=fname
    for fname in files:
        if parse_dates:
            df=pd.read_csv(fname,nrows=1,encoding=encoding)
            for col in df.columns:
                if col.lower().count('date') and not col in ignore_date_cols:
                    date_cols.append(col)
                    continue
                result=reg.search(str(df[0:1][col].tolist()[0]))
                if result is not None and not col in ignore_date_cols:
                    date_cols.append(col)
                    pass
                continue
            df=pd.read_csv(fname, parse_dates=date_cols, infer_datetime_format=True, encoding=encoding)
            pass
        else:
            df=pd.read_csv(fname,encoding=encoding)
            pass
        import resource
        if append_to is not None:
            append_to=append_to.append(df, ignore_index=True)
            df=append_to
            pass
        else: append_to=df
        mem=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if not quiet: print('read in:', fname, ' total used memory: ', mem/1000, 'MB; rows=', len(df))
        if do_robust_column_names: robust_column_names(df)
        continue
    drop_unnamed(df)        
    return df
        
def to_csv(df, fname):
    df.to_csv(fname, index=False)
    pass
