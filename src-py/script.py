
for i in range(4000, 24900, 4000):
  if i == 4000:
    print('0' + '1'*3999, end='\\')
  else :
    print('1'*4000, end='\\')
print('1'*900 , end='\\')
for i in range(4000, 24900, 4000):
  print('-1|'*4000, end='\\')
print('-1|'*899, end='')
print("-1\\", end='')

for i in range(24900):
  print('\\', end='')
