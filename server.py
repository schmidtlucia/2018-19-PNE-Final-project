# This is the server o the final practice

import http.server
import socketserver
import termcolor
import requests
import sys

socketserver.TCPServer.allow_reuse_address = True
PORT = 8000


class TestHandler(http.server.BaseHTTPRequestHandler):  # We are creating objects that heritates the properties of the http.server library

    def do_GET(self):

        # -- printing the request line
        termcolor.cprint(self.requestline, 'green')

        f = open('form1.html', 'r')
        contents = f.read()

        # -- creating a happy server response
        self.send_response(200)

        self.send_header('Content-Type', 'text/html')
        self.send_header('  Content-Length', len(str.encode(contents)))
        self.end_headers()

        #  create a response different from happy server
        req_line = self.requestline.split(" ")[1]
        if req_line == '/' or req_line == '/form1.html' or req_line == '/favicon.ico':
            file = open('form1.html', 'r')
            content = file.read()
            self.wfile.write(str.encode(content))

        else:
            if 'listSpecies' in req_line:

                server = "http://rest.ensembl.org"
                ext = "/info/species?"

                r = requests.get(server + ext, headers={"Content-Type": "application/json"})

                if not r.ok:
                    r.raise_for_status()
                    sys.exit()

                decoded = r.json()


                if 'limit' in req_line:
                    variables = req_line.partition('?')[2]

                    if variables == 'limit=':
                        title = 'List of available species in the database:'
                        species = ''
                        for i in range(len(decoded['species'])):
                            specie = 'Common name: ' + decoded['species'][i]['common_name'] + '\n  Scientific name: ' + decoded['species'][i]['name'] + '\n\n'

                            if specie in species:
                                pass
                            else:                                                                                                                                                                           
                                species += specie
                    else:
                        limit = variables.partition('=')[2]
                        title = 'List of available species in the database (max '+ limit + '):'
                        species = ''
                        for i in range(int(limit)):
                            specie = 'Common name: ' + decoded['species'][i]['common_name'] + '\n  Scientific name: ' + decoded['species'][i]['name'] + '\n\n'

                            if specie in species:
                                pass
                            else:
                                species += specie

                else:
                    title = 'List of available species in the database:'
                    species = ''
                    for i in range(len(decoded['species'])):
                        specie = 'Common name: ' + decoded['species'][i]['common_name'] + '\n  Scientific name: ' + decoded['species'][i]['name'] + '\n\n'

                        if specie in species:
                            pass
                        else:
                            species += specie


                file = open('form2.html', 'r')
                content = file.read()
                content = content.replace('TITLE', title)
                content = content.replace('----', species)
                self.wfile.write(str.encode(content))



            else:
                file = open('error.html', 'r')
                content = file.read()

                self.wfile.write(str.encode(content))

# -- MAIN PROGRAM


with socketserver.TCPServer(("", PORT), TestHandler) as httpd:  # an empty IP adress means: 'use your own IP'
    print('Serving at PORT {}'.format(PORT))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("Stopped by the user")
        httpd.server_close()

print("")
print("Server Stopped")