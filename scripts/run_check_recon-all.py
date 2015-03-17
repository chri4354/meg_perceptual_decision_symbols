import os
def tail(f, n, offset=0):
  stdin,stdout = os.popen2("tail -n "+n+offset+" "+f)
  stdin.close()
  lines = stdout.readlines(); stdout.close()
  return lines[:,-offset]
