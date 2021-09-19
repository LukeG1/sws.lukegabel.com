
import scipy.interpolate
from pprint import pprint 

pprint(scipy.interpolate.PchipInterpolator([1,2,3], [1,2,3], axis=0, extrapolate=None).x)