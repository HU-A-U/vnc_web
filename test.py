import requests
s=requests.session()
print s.cookies


a=['1','2']
a[0]='pause'
print a
# import shlex
# args=[]
# cmd=r'C:\Users\xh\vnc_web\user\lufei\move_login.vdo'
# print 'i am cmds', cmd
# x=open(cmd)
# print x
# lex = shlex.split(open(cmd), posix=True)
# print lex
# args = list(lex) + args
# print list(lex), 'i am lex'

response=s.get(url='http://127.0.0.1:5000/api/index?username=lufei&ip=127.0.0.1&port=5905')
# print response.cookies
params={'data':"['pause 0.1 move 100 200','pause 0.1 type 100200']"}
s.post(url='http://127.0.0.1:5000/api/target/chongbo',data=params)
print response.cookies
print response.text

# x='pause 0.1 move 100 200'
# strs=x.split(' ')[0]
# print strs
