global plt
plt=None

def Plt(batch=False):
    import matplotlib
    global plt
    if plt is not None: return plt
    if batch:
        print('running in batch mode')
        matplotlib.use('Agg')
        #import matplotlib.pyplot as plt
        import pylab as plt
        pass
    else :
        import pylab as plt
    return plt


class Plotter():

    def __init__(self, name=None, batch=True, from_pickle=None,labels_renew=None,labels_cancel=None):
        if from_pickle is not None:
            f=open(from_pickle, 'rb')
            import pickle
            d=pickle.load(f)
            self.__dict__=d
            f.close()
            self.plt=Plt(batch)
            pass
        else :
            self.plt=Plt(batch)
            self.name=name
            fig,ax=self.plt.subplots()
            self.fig=fig
            self.ax=ax
            self.d={}
            self.ax_right=None
            self.labels_renew=labels_renew  ###Todo move
            self.labels_cancel=labels_cancel  ###Todo move
            pass
        pass

    # def __html__(self):
    #     return 

    def pickle(self, name=None):
        d={}
        d['name']=self.name
        d['fig']=self.fig
        d['ax']=self.ax
        d['d']=self.d
        d['ax_right']=self.ax_right
        d['labels_cancel']=self.labels_cancel
        d['labels_renew']=self.labels_renew
        import pickle
        if name is None: name=self.name+'.pickle'
        f=open(name,'wb')
        pickle.dump(d,f)
        f.close()
        return
    
    def text(self,x,y,text,color='black',verticalalignment='bottom',horizontalalignment='left',
             transform=None,fontsize=14):
        if transform is None: transform=self.ax.transAxes
        self.ax.text(x,y,text,color=color,verticalalignment=verticalalignment,horizontalalignment=horizontalalignment,
                     transform=transform,fontsize=fontsize)
        pass
    
    def close(self):
        self.plt.close(self.fig)
        pass

    def set_axis_labels(self,x=None,y=None,y2=None):
        if x is not None: self.ax.set_xlabel(x)
        if y is not None: self.ax.set_ylabel(y)
        if y2 is not None: self.ax_right.set_ylabel(y2)
    
    def plot(self, x, y, label="_", linestyle="-", color=None, yaxis_label=None, log=False, kwargs={}):
            
        if color is not None and color in self.d:
            color=self.d[color].get_color()
            pass
        fnc=self.ax.plot
        if log: fnc=self.ax.semilogy
        fnc(x,y,label=label,linestyle=linestyle, color=color, **kwargs)
        self.d[label]=self.ax.get_lines()[-1]
        if yaxis_label is not None:
            self.ax.set_ylabel(yaxis_label, color=color,fontsize='large')
            pass
        pass

    def normed_hist(self, x, bins=10, label='_', linestyle='-', color='b', yaxis_label=None,log=False):
        if color is not None and color in self.d:
            color=self.d[color].get_color()
            pass
        data,bin_edges=self.plt.histogram(x,bins)

        if log:
            print('log mode is not correct')
            data2=[]
            bin_edges2=[]
            last_edge=bin_edges[min(1,len(bin_edges)-1)]
            for i in range(len(data)):
                if data[i]>0:
                    data2.append(data[i])
                    bin_edges2.append(bin_edges[i])
                    last_edge=bin_edges[min(i,len(bin_edges)-1)]
                    pass
                continue
            import math
            import numpy as np
            data=np.log(data2)/math.log(10)
            bin_edges=np.array(bin_edges2+[last_edge])
            pass

        import numpy as np
        bin_centers=(bin_edges[:-1]+bin_edges[1:])/2
        data=data/data.sum()
        result=data.copy()
        data=np.append(np.append(data[0],data),data[-1])

        bin_centers=np.append(np.append(bin_edges[0],bin_centers),bin_edges[-1])
        self.ax.step(bin_centers,data,label=label,linestyle=linestyle,color=color)
        #self.ax.plot(bin_centers,data,label=label,linestyle=linestyle,color=color)
        
        if yaxis_label is not None: self.ax.set_ylabel(yaxis_label,color=color,fontsize='large')
        return result
    
    def plot_right(self, x, y, label="_", linestyle='-', color=None,yaxis_label=None,log=False, kwargs={}):
        if self.ax_right is None:
            self.ax_right=self.ax.twinx()
            pass
        for i,j in ({'label':label,'linestyle':linestyle,'color':color}).items():
            kwargs[i]=j
            continue
        if not log : self.ax_right.plot(x,y,**kwargs)
        else : self.ax_right.semilogy(x,y,**kwargs)
        if yaxis_label is not None:
            self.ax_right.set_ylabel(yaxis_label, color=color,fontsize='x-large')
            pass
        pass
    
    def xLabelDateFormat(self,DateFormatter=None):
        import datetime
        import numpy as np
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        import matplotlib.cbook as cbook

        years = mdates.YearLocator()   # every year
        months = mdates.MonthLocator()  # every month
        yearsFmt = mdates.AutoDateFormatter(mdates.AutoDateLocator())
        if DateFormatter is not None: yearsFmt = mdates.DateFormatter(DateFormatter)

        # format the ticks
        self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        self.ax.xaxis.set_major_formatter(yearsFmt)
        self.ax.xaxis.set_minor_locator(months)

        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        self.fig.autofmt_xdate()
        pass

    def add_legend(self,data,loc=None):
        legend=self.ax.legend()
        self.plt.gca().add_artist(legend)
        for n,s in data.items():
            l=self.ax.plot([],[],linestyle=s,label=n,color='black')
            continue
        legend2=self.ax.legend()
        self.plt.gca().add_artist(legend2)
        pass

    def set_limits(self, axis='y', minx=None, maxx=None, minr=None, maxr=None):
        """
        axis: 'x' or 'y'
        minx/maxx: min and max values
        minr/maxr: multiply min/max by some ratio
        """
        setter=getattr(self.ax, 'set_'+axis+'lim')
        getter=getattr(self.ax, 'get_'+axis+'lim')
        cmin,cmax=getter()
        if minx is not None: cmin=minx
        if maxx is not None: cmax=maxx
        if minr is not None: cmin*=minr
        if maxr is not None: cmax*=maxr
        setter(cmin,cmax)
        if (minr is not None or maxr is not None) and self.ax_right is not None:
            setter=getattr(self.ax_right, 'set_'+axis+'lim')
            getter=getattr(self.ax_right, 'get_'+axis+'lim')
            cmin,cmax=getter()
            if minr is not None: cmin*=minr
            if maxr is not None: cmax*=maxr
            setter(cmin,cmax)
            pass            
        pass

    def is_scatter(self):
        return len(self.ax.collections)>0

    def is_line(self):
        return not self.is_scatter() and len(self.ax.get_lines())

    def asbokeh_scatter(self,hover_names=None,tools="pan,box_zoom,wheel_zoom,reset,hover,save,zoom_in,zoom_out",colors=None):
        from bokeh.models import (
            ColumnDataSource,
            HoverTool,
            LogColorMapper
        )           
        from bokeh.io import show, save
        from bokeh.plotting import figure, output_file
        from bokeh.embed import components
        from bokeh.models import LinearAxis, Range1d, Span

        p=figure(title=self.name, tools=tools)
        if colors==None: colors=['red','blue','green','gray','orange']
        for i in range(len(self.ax.collections)):
            col=self.ax.collections[i]
            source=ColumnDataSource(data=dict(
                x=[x[0] for x in col.get_offsets()],
                y=[x[1] for x in col.get_offsets()],
            ))
            if len(hover_names)==len(self.ax.collections):
                #print(type(source.data))
                #source.data[hover_names[i][0]]=hover_names[i][1]
                source.add(hover_names[i][1], name=hover_names[i][0])
                pass
            p.circle('x','y',source=source,color=colors[i],legend=col.get_label())
            continue

        p.xaxis.axis_label=self.ax.get_xlabel()
        p.yaxis.axis_label=self.ax.get_ylabel()

        hover = p.select_one(HoverTool)
        hover.point_policy = "follow_mouse"
        hover.tooltips = [
            ('x','@x'),
            ('y','@y'),            
        ]
        if len(hover_names)==len(self.ax.collections):
            hover.tooltips.append( (hover_names[0][0],'@'+hover_names[0][0]) )
            pass
        
        return p

    def asbokeh_plot(self):
        from bokeh.models import (
            ColumnDataSource,
            HoverTool,
            LogColorMapper
        )           
        from bokeh.io import show, save
        from bokeh.plotting import figure, output_file
        from bokeh.embed import components
        from bokeh.models import LinearAxis, Range1d, Span

        pass
    
    def asbokeh(self,**kwargs):
        if self.is_scatter() : return self.asbokeh_scatter(**kwargs)
        elif self.is_line() : return self.asbokeh_plot(**kwargs)
        else : raise RuntimeError("Not sure how to convert this matplotlib object")
        
    
    def savefig(self, name=None, suf=[],legend=True,bbox_inches='tight',close=True,ftype=None, **kwargs):

        if ftype is not None and ftype=='bokeh':
            from bokeh.io import show, save
            from bokeh.plotting import figure, output_file
            p=self.asbokeh(**kwargs)
            output_file(self.name+'.html')
            save(p)
            return 
        
        if name is None: name=self.name

        if legend :
            if self.ax_right is not None:
                lines=self.ax.get_lines()
                lines+=self.ax_right.get_lines()
                lines_w_labels=[]
                for l in lines:
                    #if len(l.get_label()) and l.get_label()[0]!='_': lines_w_labels.append(l)
                    if len(l.get_label()) and l.get_label()[0]=='_': continue
                    else : lines_w_labels.append(l)
                    continue
                labels=[l.get_label() for l in lines_w_labels]
                self.ax.legend(lines_w_labels, labels, **kwargs)
                pass
            else : self.ax.legend()
            pass
        
        if len(suf)==0 :
            if not name.count('.'):name+='.png'
            import os
            #os.system('rm -f %s' %name)
            # print('saving ', name)
            # for l in self.ax.lines:
            #     print(l._x, l._y)
            self.fig.savefig(name,bbox_inches=bbox_inches)
            pass
        else:
            for suffix in suf:
                if not suffix.count('.'): suffix='.'+suffix
                self.fig.savefig(name+suffix,bbox_inches=bbox_inches)
                continue
            pass
        if close : self.close()
        return name
            

    pass

class StackPlotter(Plotter):
    global np
    import numpy as np
    def __init__(self, name, batch=True):
        super(StackPlotter,self).__init__(name, batch)
        self.total=None
        self._x=None
        pass

    def plot(self, x, y, label="_", color=None,fill=True,**kwargs):
        last=np.zeros(len(y))
        if self._x==None:
            self._x=x
            self.total=np.array(y)
        else:
            last=self.total.copy()
            if x!=self._x: raise ValueError( "inconsistent x-axes ", x, "was ", self._x)
            #print(self.total, "::\n", y)
            self.total+=np.array(y)
            pass

        # if color is not None:
        #     self.ax.plot(self._x,self.total,label=label,color=color)
        # else:
        #     self.ax.plot(self._x,self.total,label=label)
        #     pass
        step=None
        if 'drawstyle' in kwargs:
            step=kwargs['drawstyle'].replace('steps-','')
            pass
        print(step,kwargs)
        self.ax.plot(self._x,self.total,label=label,color=color,**kwargs)
        if fill : self.ax.fill_between(self._x,last,self.total,step=step,color=color)
        pass
    pass
                
            

# def plotMany( x, y, fig=None, ax=None, labels=None, colors=None):
#     if (fig is not None and ax is None) or (fig is None and ax is not None):
#         print('WARNING   keyword args, fig and ax should both be None or both non-None.  Not mixed:', fig, ax, 'will return new objects for each')
#         pass
#     if (fig is None) or (ax is None):
#         fig,ax=plt.subplots()
#         pass

#     if len(y)
#         print('ERROR  don\'t konw what you want, shape of x, y: ', len(x), len(y))
#         print('Expect len(x)==len(y) or len(x)==1')
#         import sys
#         sys.exit(0)
#         pass

#     for i in range(0, len(y)):
#         yi=y[i]
#         try: xi=x[i]
#         except: xi=x
