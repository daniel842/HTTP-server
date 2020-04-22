# HTTP Server Shell
# Author: Barak Gonen
# Purpose: Provide a basis for Ex. 4.4
# Note: The code is written in a simple way, without classes, log files or other utilities, for educational purpose
# Usage: Fill the missing functions and constants

# Import modules
import socket
import os.path
import glob

Dictionary_of_Forbidden = ['sodi.py']
Default_url = '/index.html'
Default_dir = '/Users/danielvazana/Downloads/webroot'
Optional_File_Dictionary = {'/cat_glass': '/imgs/abstract.jpg', '/gvahim': '/imgs/favicon.ico',
                            '/toen': '/imgs/loading.gif'}
Image_404 = '/uploads/404.jpg'
Image_403 = '/uploads/403-forbidden-error.png'


def get_file_data(filename):
    """ Get data from file """
    with open(filename, 'rb') as file1:
        data = file1.read()
    length = str(len(data))
    return "Content-Length: " + length, " \r\n\r\n" + data


def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client"""
    # Sets the url by resource
    ex4 = True
    ex6 = True
    ex9 = True
    ex11 = True
    if resource == '/':
        url = Default_url
        ex4 = True
        ex6 = False
        ex9 = False
        ex11 = False
    elif '/favicon.ico' == resource:
        url = '/imgs' + resource
        ex4 = True
        ex6 = False
        ex9 = False
        ex11 = False
    elif '/calculate-next?num=' in resource:
        ex4 = False
        ex6 = True
        ex9 = False
        ex11 = False
    elif '/calculate-area?' in resource:
        ex4 = False
        ex6 = False
        ex9 = True
        ex11 = False
    elif '/image?' in resource:
        ex4 = False
        ex6 = False
        ex9 = False
        ex11 = True
    else:
        url = resource

    # Prepares the header and defines the file name for sending to the client if necessary
    # If there is a 302 error then immediately send the code 302 to the client
    # extract requested file type from URL (html, jpg etc)
    if ex4:
        file_name = ''
        if os.path.isfile(Default_dir + url):
            if url in Dictionary_of_Forbidden:
                http_header = "HTTP/1.0 403 Forbidden \n"
                file_name = Default_dir + Image_403
            else:
                http_header = "HTTP/1.0 200 ok \n"
                filetype = str(url.split('.')[- 1])
                if filetype == "html" or filetype == "txt":
                    http_header += "Content-Type: text/" + filetype + "; charset=utf-8 \r\n"
                elif filetype == "css":
                    http_header += "Content-Type: text/" + filetype + " \r\n"
                elif filetype == 'jpg':
                    http_header += "Content-Type: image/jpeg \r\n"
                file_name = Default_dir + url
        elif url in Optional_File_Dictionary:
            http_header = "HTTP/1.1 302 Found\r\nContent-Type: text/html; charset=utf-8 \r\nLocation: " + \
                          Optional_File_Dictionary[url] + "\r\n\r\n"
            client_socket.send(http_header)
        else:
            http_header = "HTTP/1.0 404 Not Found \n"
            file_name = Default_dir + Image_404

        # Read the data from the file and send it to the client
        if '302 Found' not in http_header:
            length, data = get_file_data(file_name)
            http_response = http_header + length + data
            client_socket.send(http_response)
    elif ex6:
        # Ex 4.6
        http_header = "HTTP/1.0 200 ok \nContent-Type: text/text; charset=utf-8 \r\n"
        num = str(int(resource.replace('/calculate-next?num=', '')) + 1)
        length = str(len(num))
        http_response = http_header + "Content-Length: " + length, " \r\n\r\n" + num
        http_response = http_response[0] + http_response[1]
        client_socket.send(http_response)
    elif ex9:
        http_header = "HTTP/1.0 200 ok \nContent-Type: text/text; charset=utf-8 \r\n"
        nums = resource.replace('/calculate-area?', '')
        num1 = nums.replace('height=', '')
        num1 = num1[:num1.find('&')]
        num2 = resource[resource.find('&') + 1:]
        num2 = num2.replace('width=', '')
        num3 = float(num1) * float(num2)
        num3 = num3 / 2
        data = str(num3)
        length = str(len(data))
        http_response = http_header + "Content-Length: " + length, " \r\n\r\n" + data
        http_response = http_response[0] + http_response[1]
        client_socket.send(http_response)
    elif ex11:
        list_of_files = glob.glob(Default_dir + '/uploads' + "/*.*")
        name_of_file = resource[resource.find('image-name=') + len('image-name='):]
        file_path = ''
        for file in list_of_files:
            if name_of_file in file:
                file_path = file
        http_header = "HTTP/1.0 200 ok \nContent-Type: text/text; charset=utf-8 \r\n"
        if not os.path.exists(file_path):
            file_path = Default_dir + Image_404
        if '/'+name_of_file in Optional_File_Dictionary:
            file_path = Default_dir + Optional_File_Dictionary['/'+name_of_file]
        length, data = get_file_data(file_path)
        http_response = http_header + length + data
        client_socket.send(http_response)


def handle_client_post(client_request, client_socket):
    length = client_request[client_request.find('Content-Length:') + len('Content-Length: '):]
    length = int(length[:length.find('\r\n')])
    data = ''
    rest = length % 1024
    for i in xrange(length / 1024):
        data += client_socket.recv(1024)
    if rest != 0:
        data += client_socket.recv(rest)
    name_of_file = client_request[client_request.find('file-name=') + len('file-name='):]
    name_of_file = name_of_file[:name_of_file.find(' HTTP/1.1')]
    with open(Default_dir + '/uploads/' + name_of_file, 'wb') as file_to_wirte:
        file_to_wirte.write(data)
    http_header = "HTTP/1.0 200 ok \nContent-Type: text/text; charset=utf-8 \r\n"
    message = 'File received and saved'
    length_message = str(len(message))
    http_response = http_header + "Content-Length: " + length_message, " \r\n\r\n" + message
    http_response = http_response[0] + http_response[1]
    client_socket.send(http_response)


def validate_http_request(request):
    """ Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL """
    # TO DO: write function
    list1 = request.split()
    # Strats the checkings
    flag = False
    if list1[0] == 'GET':
        if list1[1][0] == '/':
            if list1[2] == 'HTTP/1.1':
                flag = True
    elif list1[0] == 'POST':
        if list1[1][0] == '/':
            if list1[2] == 'HTTP/1.1':
                flag = True
    return flag, list1[1]


def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print 'Client connected'
    while True:
        # TO DO: insert code that receives client request
        try:
            client_request = client_socket.recv(1024)
            if 'POST' in client_request:
                handle_client_post(client_request, client_socket)
        except:
            break
        if client_request == '':
            break
        # ...
        valid_http, resource = validate_http_request(client_request)
        if valid_http:
            print 'Got a valid HTTP request'
            handle_client_request(resource, client_socket)
        else:
            print 'Error: Not a valid HTTP request'
            break
    print 'Closing connection'
    client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    port = 8001
    ip = '0.0.0.0'
    server_socket = socket.socket()
    server_socket.bind((ip, port))
    server_socket.listen(10)
    print "Listening for connections on port %d" % port
    ok = True
    while ok:
        client_socket, client_address = server_socket.accept()
        print 'New connection received'
        client_socket.settimeout(1)
        handle_client(client_socket)
    server_socket.close()


if __name__ == '__main__':
    main()
