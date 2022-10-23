Calling `liveplot myscript.py` with the code below will produce the same result
as `python myscript.py`, but the plot will update whenever `myscript.py`changes.

The result of `load_data` will be saved and re-used if the function does not change.

    import matplotlib.pyplot as plt 
    
    def load_data():
        return ([1, 2, 3], [1, 4, 9]}
        
    def make_figure(fig, data):
        x, y = data
        fig.add_subplot(111).plot(x, y, ".")
        
    if __name__ == "__main__":
        make_figure(plt.figure(), load_data())
        plt.show()

Other functions are supported.

      def load_data(): return None
      def postprocess(data): return data
      def settings(plt): pass 
      def make_figure(fig, data): pass

Find the documentation and examples at https://github.com/fkunstner/liveplot
