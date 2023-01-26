#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        #structure :method path
        decode_data=self.data.decode().split() #this splits the data into parts
        
        #check empty requests
        if len(decode_data)<=0:
            self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n\r\n",'utf-8'))
            return
        #print ("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK",'utf-8'))

        #check request, should only accept get. return 405 if not get
        get_request=self.check_get(decode_data)
        print(decode_data)
        if get_request==False:
            print(get_request)
            return
        else:
            #if anyone tries to access root, return 404
            root_access=self.check_path(decode_data)
            if root_access:
                return
            #check the file types
            if decode_data[1][-1]=='/' or decode_data[1].split('.')[-1]=='css' or decode_data[1].split('.')[-1]=='html':
                self.get_file(decode_data)
            else:
                self.redirection(decode_data)
            
            
            
#check method
    def check_get(self, decoded):
        if decoded[0]!='GET':
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\nAllow: GET\r\n\r\nContent-length:0",'utf-8'))
            return False
        return True
#check the path
    def check_path(self,decoded):
        if '../' in decoded[1]:
            self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n\r\nContent-length:0",'utf-8'))
            return True
        return False

    def get_file(self,decoded):
        data_path=decoded[1].split('.')
        
        #open files
        file_name='www'+decoded[1]
        print('\n'+data_path[-1])
        print(file_name)
        #for redirection
        if decoded[1][-1]=='/':
            file_name+='/index.html'
            data_path[-1]='html'
        try:
            print("This is the file name:"+file_name)
            file=open(file_name)
            content=file.read()
            file.close()
            if decoded[1][-1]=='/' or data_path[-1]=='html' or data_path[-1]=='css':
                print('yes\n')
                self.request.sendall(bytearray("HTTP/1.1 200 OK\r\nContent-Length:" + str(len(content)) + "\r\nContent-Type: text/"+data_path[-1]+"\r\n\r\n" + content,'utf-8'))
            else:
                print('no\n')
                print("http://127.0.0.1:8080" + decoded[1] + '/')
                self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\nLocation: " + "http://127.0.0.1:8080" + decoded[1] + '/' + "\r\n\r\n",'utf-8'))
            #any wrong directory goes to 404
        except:   
            print('what\n')   
            self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n\r\n",'utf-8'))
            return
        return
    #for 301 status code
    def redirection(self,decoded):
        path='www'+decoded[1]+'/index.html'
        try:
            file=open(path)
            file.close()
            self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\nLocation: " + "http://127.0.0.1:8080" + decoded[1] + '/' + "\r\n\r\n",'utf-8'))
        except:
            self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n\r\n",'utf-8'))
            return
        return
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
