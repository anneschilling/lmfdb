import sys
sys.path.append("../")

print "Importing sage in base"
import base
from math_classes import NumberFieldGaloisGroup as NF

base._init(37010,"")

base.getDBConnection()

for nf_dict in NF.collection().find():
   from copy import deepcopy
   nf_dict2 = deepcopy(nf_dict)
   nf = NF(data = nf_dict)
   print nf.polredabs()
   if nf.label():
      print nf.label()
      nf_dict2["label"] = nf.label()
      NF.collection().save(nf_dict2)
   
