# PyXFOIL

Basic Python wrapper for XFOIL.

- [x] MIT License
- [x] Python 3.8+

**Example Usage:**

```python
from pyxfoil.xfmanager import XFManager

cmds = [
    'PLOP', 'G', '',               # set no display
    'naca 2412',                   # set aerofoil
    'oper',                        # set OPER mode 
    'pacc', 'naca2412.out', '',    # set output file
    'aseq', -5, 10, 0.5,           # set a.o.a sweep
    '', 'QUIT'                     # quit xfoil
]

xf = XFManager()
xf.config_cmd(cmds)

xf.run()
```

###### Made by Daniel Kelshaw
