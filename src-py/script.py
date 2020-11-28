for i in range(4000, 24900, 4000):
    print('1'*4000, end='\\')
print('1'*1000 , end='\\')
for i in range(4000, 24900, 4000):
       print('-1|'*4000, end='\\')
print('-1|'*999, end='')
print("-1\\", end='')

for i in range(24900):
    print('\\', end='')
