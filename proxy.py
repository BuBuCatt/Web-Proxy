from socket import *
from urllib.parse import urlparse
import sys
from pathlib import Path



port = int(sys.argv[1]) 


#get http response store in socket
"""
    Sends an HTTP request to the specified host and returns the response.

    Arguments:
    host -- the hostname or IP address of the server
    method -- the HTTP method 
    path -- the path of the resource on the server 
    http_version -- the HTTP version

    Returns:
    bytes -- the response from the server
"""
def send_http_request(host, method, path, http_version):
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((host, 80))
        request = f"{method} {path} {http_version}\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        s.sendall(request.encode())
        response = b''
        while True:
            data = s.recv(1024)
            if not data:
                break
            response += data
    return response

"""
    Starts a proxy server that listens for incoming HTTP requests on the specified port and serves them to the client.
    Caches HTTP responses with status code for future requests.
    Arguments:
    port -- the port number on which to listen for incoming requests
"""
        

#create a socket as s
with socket(AF_INET , SOCK_STREAM) as s:
    s.bind(('',port))
    s.listen(1)
    cache_counter= 0    
    while True: #receiving data
        print("******************** Ready to serve ********************")
        
        #accept connetion
        clientSocket, addr = s.accept() # return socket obj and address        
        print("Received a client connection from ", addr)
        data = clientSocket.recv(1024) #receive data from celint
        decode_data = data.decode().split() 
        if not data:
            break    
        if len(decode_data) >= 3:
            method, url, http_version = decode_data[:3]#[0],[1],[2]
            #get piece of url [1]
            get_url=urlparse(url)
            #get path in url
            path = get_url.path
            host_url = f"{get_url.netloc}"
            file_path = "/home/st/chsu1/c5110" / Path(path).relative_to('/')

            print("Received a message from this client: ", data)
        
        #response  msg                           
        response = send_http_request(host_url, method, path, http_version)
                
                


        #check status is 200  or not 200
        
        #get Http/1.1 and 200
        get_http_part = response.decode().split()
        get_http_number = f"{get_http_part[1]}" #http number 
        if(int(get_http_number)==200):
            if Path(file_path).exists():
                cache_counter+=1
                with open(file_path,'rb')as file:
                    file_text = file.read()
                print("Yay! The requested file is in the cache...")
                cache_msg = f"{http_version} 200 OK\r\nContent-Length: {len(file_text.decode())}\r\nConnection: close\r\nCache-Hit: {cache_counter}\r\n\r\n{file_text.decode()}" 

                clientSocket.sendall(cache_msg.encode())
                clientSocket.close()
                cache_counter= 0

                
        
            else:
                            #cache 
                print("Oops! No cache hit! Requesting origin server for the file...")
                
                #msg details
                print("Sending the following message to proxy to server: ")
                #decode and split data by space
                
                print(method, path, http_version)
                print("host: ", host_url)
                print("Connection: ","close")
                
                
                
                response_msg = response.decode().split("\r\n\r\n")
                file_content = response_msg[1].encode()
                file_path = Path("/home/st/chsu1/c5110") / Path(path).relative_to('/')   
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path,'wb') as file:
                    file.write(file_content)
                print("/r/n/r/nResponse received from server, and status code is 200! Write to cache, save time next time...")
                msg=f"{response_msg[0]} \r\nCache-Hit: {cache_counter} \r\n\r\n{response_msg[1]} "
                clientSocket.sendall(msg.encode())
                clientSocket.close()

            
        else: #404 or 500
            response_msg = response.decode().split("\r\n")
            msg=f"{response_msg[0]} \r\nCache-Hit: {cache_counter}\r\n{response_msg[1]}\r\n{response_msg[2]}\r\n{response_msg[3]}\r\n{response_msg[4]}\r\n{response_msg[5]}\r\n{response_msg[6]}\r\n{response_msg[7]}\r\n"   
                            #msg details
            print("Oops! No cache hit! Requesting origin server for the file...")
            print("Sending the following message to proxy to server: ")
            #decode and split data by space

            print(method, path, http_version)
            print("host: ", host_url)
            print("Connection: ","close")
            
            
            print("Response received from server, and status code is not 200! No cache writing...")            
            clientSocket.sendall(msg.encode())
            clientSocket.close()
        print("Now responding to the client...")
        print("All done! Closing socket...\r\n\r\n")
                
                
            
        
            
            
 
            
    
    