global pd
import pandas as pd

def Pd():
    import pandas as pd
    import os
    columns=100
    try:
        rows,columns=os.popen('stty size', 'r').read().split()
    except: pass
    pd.options.display.width=int(columns)
    return pd

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
    new_cols=[]
    for col in df.columns:
        new_cols.append(col)
        if col=='Unnamed: 0' : continue
        original_name=col
        result=r.search(col)
        while( result is not None):
            col=col.replace(result.group(),'_')
            result=r.search(col)
            continue
        if original_name != col : d[original_name]=col
        new_cols[-1]=col
        continue

    #for some reason this first method takes a long time...
    #df.rename(index=str, columns=d, inplace=True, copy=False)
    df.columns=new_cols
    
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

def read_csv(fname, parse_dates=True, ignore_date_cols=[], do_robust_column_names=True, encoding='utf-8', quiet=False, append_to=None, selection=None, sep=',',usecols=None,strip_blank_space=None, kwargs=None):
    """
    return a dataframe

    fname: file name, or list of file names
    
    parse_dates: attempt to parse dates, look for 'date' in column name (case-insensitive), or for data in first row of column
    resembling: xx:yy:zz

    ignore_date_cols: in parsing of dates, ignore specific columns.  e.g. dates is a fruit ...

    do_robust_column_names: convert spaces, and unfriendly symbols to '_'
    
    encoding: default 'utf-8'

    append_to: provide a df that should be appended to output

    selection: function or tuple(function, arg1, arg2, etc.)  df is always passed as first argument to function.
    called for each df

    strip_blank_space: default None, if list, do df[col]=df[col].map(lambda x: x.strip()) for all col in list, else if not None, strip all leading,trailing
    white space for all columns with 'dtype=='O''

    kwargs: dictionary passed to pd.read_csv, default None
    """
    if kwargs is None: kwargs={}
    date_cols=[]
    import re
    reg=re.compile('[0-9]{2}:[0-9]{2}:[0-9]{2}')
    df=None
    files=[]
    if type(fname) != list: files=[fname]
    else: files=fname
    for fname in files:
        if parse_dates:
            df=pd.read_csv(fname,nrows=1,encoding=encoding,sep=sep,usecols=usecols)
            for col in df.columns:
                if col.lower().count('date') and not col in ignore_date_cols:
                    date_cols.append(col)
                    continue
                result=reg.search(str(df[0:1][col].tolist()[0]))
                if result is not None and not col in ignore_date_cols:
                    date_cols.append(col)
                    pass
                continue
            df=pd.read_csv(fname, parse_dates=date_cols, infer_datetime_format=True, encoding=encoding,sep=sep,usecols=usecols,**kwargs)
            pass
        else:
            df=pd.read_csv(fname,encoding=encoding,sep=sep,usecols=usecols,**kwargs)
            pass
        import resource
        if selection is not None:
            if type(selection)==tuple:
                df=selection[0](df, *(selection[1:]))
            else :
                df=selection(df)
                pass
            pass
            
        if append_to is not None:
            append_to=append_to.append(df, ignore_index=True)
            df=append_to
            pass
        else: append_to=df
        mem=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if not quiet: print('read in:', fname, ' total used memory: ', mem/1000, 'MB; rows=', len(df))
        continue
    if do_robust_column_names: robust_column_names(df)
    drop_unnamed(df)
    if strip_blank_space is not None:
        cols=df.columns
        if type(strip_blank_space)==list: cols=strip_blank_space
        elif type(strip_blank_space)==bool and strip_blank_space==False: cols=[]
        for c in cols:
            if df[c].dtype != 'O': continue
            df[c]=df[c].map(lambda x: x.strip())
            continue
        pass
    return df
        
def to_csv(df, fname):
    df.to_csv(fname, index=False)
    pass

def general_dict(df, key=None, cols=None):
    """
    Note, probably could do some sort of join operation...
    return dict[key] = df[df.key==value][cols].values
    so a dict[key] = np.array(cols)
    
    key: str
    cols: [str,str,...]

    """
    import numpy as np
    d={}
    #i=0
    the_cols=[key]
    the_cols+=cols
    df_view=df[the_cols]
    
    for t in df_view.itertuples():
        k=t[1]
        if k in d:
            d[k]=np.vstack((d[k], np.array(t[2:])))
        else:
            d[k]=np.array(t[2:])
            pass
        continue
    return d

def pairwise_dict(df, selection=None, cols=None, key=None, value=None):
    if selection is not None: df=select(df,criteria=selection,columns=cols)
    elif cols is not None: df=df[cols]

    if len(df.columns)!=2 and (key is None or value is None):
        raise RuntimeError('pairwise dict expects two columns!, dataframe has', len(df.columns), 'columns')

    if key is None: key=df.columns[0]
    if value is None: value=df.columns[1]

    keys=df[key].tolist()
    values=df[value].tolist()
    d={}
    for k,v in zip(keys,values): d[k]=v
    return d

def append_var(df, selection=None, groupby=None, new_var='', var='', transform='sum', transform2='max', default_val=-1):
    """
df: dataframe
selection: string, pd.core.series.Series().  If string, df[df.eval(selection)], else, df[selection]... default: None
transform2: 'max', 'min', None. What to do for non-matching rows after initial transform.  i.e. df.loc[ all, 'new_var']=df.groupby(groupby)[new_var].transform('transform2')
you are selecting the 'transform2'
default_val: default value
groupby: list. List of items to group by
var: name of var we are transforming
transform: how to transform var
new_var: name of new var
    """
    dummy=[True for i in range(len(df))]
    if selection is None: selection=dummy
    elif type(selection)==str:
        if len(selection):selection=df.eval(selection)
        else:selection=dummy
        pass

    if groupby is None or len(groupby)==0: raise ValueError('groupby must be a non-empty list')
    if var is None or len(var)==0: raise ValueError('var must be a non-empty string')
    if new_var is None or len(new_var)==0: raise ValueError('new_var must be a non-empty string')

    if default_val is not None:df[new_var]=default_val

    df.loc[selection, new_var]=df[selection].groupby(groupby)[var].transform(transform)
    if transform2 is not None and len(transform2):
        df.loc[ dummy, new_var]=df.groupby(groupby)[new_var].transform(transform2)
        pass
    
    pass    

def change_col_name(df, old_names, new_names):
    """
    old_names: str or list
    new_names: str or list--must match old_names
    """
    #print("changing col name", old_names, new_names)
    if type(old_names) != type(new_names):
        raise ValueError('type of old_names and new_names do not match')
    if type(old_names)==list:
        if len(old_names) != len(new_names):
            raise ValueError('len of old_names and new_names do not match', len(old_names), len(new_names))
        for o,n in zip(old_names,new_names):
            change_col_name(df,o,n)
            continue
        pass
    else :
        df.columns=[ new_names if col==old_names else col for col in df.columns ]
        pass
    return


import time

def parse_date(df, date_col, form=None, new_name=None):
    if form is not None:
        import timeit
        def _temp_func_(x,form=form):
            #if x!=x: return pd.Timestamp('2000-01-01')
            if type(x)==float : return pd.Timestamp('2000-01-01')
            a=time.strptime(x,form)
            result=pd.Timestamp( a.tm_year, a.tm_mon, a.tm_mday )
            return result
        if type(form)==type(_temp_func_): _temp_func_=form
        df[date_col]=df[date_col].map(lambda x: _temp_func_(x))
    else:
        df[date_col]=df[date_col].map(lambda x: pd.Timestamp(x))        
        pass

    if new_name is not None:
        change_col_name(df, date_col, new_name)
        pass
    pass


def denan_cols(df, cols, value=0):
    for col in cols:
        df[col]=df[col].map(lambda x: x if x==x else value)
        pass
    return
