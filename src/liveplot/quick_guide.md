Calling `liveplot` on the code below will produce the same result as `python`, but the plot will
update when the file changes. The data is saved and re-used if `load_data` does not change.

    import matplotlib.pyplot as plt 
    
    def load_data(): 
        return ([1, 2, 3], [1, 4, 9])
        
    def make_figure(fig, data): 
        fig.add_subplot(111).plot(*data, ".")
        
    if __name__ == "__main__":
        make_figure(plt.figure(), load_data())
        plt.show()

Functions supported:

    def load_data(): return None
    def postprocess(data): return data
    def settings(plt): pass
    def make_figure(fig, data): pass

Find the documentation and examples at https://github.com/fkunstner/liveplot
