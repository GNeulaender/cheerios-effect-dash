import math
#
# Funções auxiliares
#
utriangular = lambda d: d/(2*math.sqrt(6)) #incerteza triangular
uretangular = lambda d: d/(2*math.sqrt(3)) #incerteza retangular
# função para calcular incerteza combinada de uma lista de incertezas
def ucomb(*ulist):
  sum = 0.0
  for var in ulist:
    sum += var**2
  return math.sqrt(sum)
#função média
def media(vlist):
  sum = 0.0
  for var in vlist:
    sum += var
  return sum/len(vlist)
#incerteza gaussiana
def ugaus(vlist):
  sum = 0.0
  m = media(vlist)
  for var in vlist:
    sum += (var-m)**2
  return math.sqrt(sum/len(vlist))
