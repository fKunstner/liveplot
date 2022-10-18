# Liveplot 

`liveplot` updates a Matplotlib `pyplot` figure on save,
without having to re-run a script and reloading data.






How to: `python -m liveplot myplot.py` where `myplot.py` contains 
a plotting function `make_figure(fig, data)`
 where `data` is the return value of `load_data`
- A data loading function `load_data` if you need one

Edit `myplot.py` and save to see the results. 

