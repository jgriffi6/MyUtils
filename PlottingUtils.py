global plt

def Plt(batch=False):
    import matplotlib
    if batch:
        matplotlib.use('Agg')
        pass
    global plt
    import matplotlib.pyplot as plt
    return plt


class Plotter():

    def __init__(self, name, batch=True):
        self.plt=Plt(batch)
        self.name=name
        fig,ax=plt.subplots()
        self.fig=fig
        self.ax=ax
        self.d={}
        pass

    def close(self):
        self.plt.close(self.fig)
        pass

    def plot(self, x, y, label="_", linestyle="-", color=None):
        if color is not None and color in self.d:
            color=self.d[color].get_color()
            pass
        self.ax.plot(x,y,label=label,linestyle=linestyle, color=color)
        self.d[label]=self.ax.get_lines()[-1]
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
    
    def savefig(self, name=None, suf=[],legend=True):
        if name is None: name=self.name

        if legend : self.ax.legend()
        
        if len(suf)==0 :
            if not name.count('.'):name+='.png'
            self.fig.savefig(name)
            pass
        else:
            for suffix in suf:
                self.fig.savefig(name+suf)
                continue
            pass
        self.close()
        return
            

    pass

class StackPlotter(Plotter):
    global np
    import numpy as np
    def __init__(self, name, batch=True):
        super(StackPlotter,self).__init__(name, batch)
        self.total=None
        self._x=None
        pass

    def plot(self, x, y, label="_", color=None,fill=True):
        last=np.zeros(len(y))
        if self._x==None:
            self._x=x
            self.total=np.array(y)
        else:
            last=self.total.copy()
            if x!=self._x: raise ValueError( "inconsistent x-axes ", x, "was ", self._x)
            self.total+=np.array(y)
            pass

        # if color is not None:
        #     self.ax.plot(self._x,self.total,label=label,color=color)
        # else:
        #     self.ax.plot(self._x,self.total,label=label)
        #     pass
        self.ax.plot(self._x,self.total,label=label,color=color)
        if fill : self.ax.fill_between(self._x,last,self.total)
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
