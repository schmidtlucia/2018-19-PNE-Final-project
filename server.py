# This is the server of the final practice

import http.server
import socketserver
import termcolor
import requests
import sys

socketserver.TCPServer.allow_reuse_address = True
PORT = 8000


# here we are creating a function for opening the information file and replacing the title and the information
def open_file(title, information):
    """This function opens our response HTML file, and takes the two given arguments and replaces the key signals,
    'TITLE' and '----', for them, returning the final response for the user."""

    file = open('form2.html', 'r')
    content = file.read()
    content = content.replace('TITLE', title)
    content = content.replace('----', information)
    return content


class TestHandler(http.server.BaseHTTPRequestHandler):

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

        #  we extract the endpoint from the request line
        req_line = self.requestline.split(" ")[1]

        # if the user only enters following endpoints, program must open the home menu
        if req_line == '/' or req_line == '/form1.html' or req_line == '/favicon.ico':
            file = open('form1.html', 'r')
            content = file.read()
            self.wfile.write(str.encode(content))

        # we will now analyze the endpoints
        else:

            # this endpoint is given if the user has requested some information about the species
            if 'listSpecies' in req_line:

                # this is the endpoint for retrieving species information from the API
                server = "http://rest.ensembl.org"
                ext = "/info/species?"
                r = requests.get(server + ext, headers={"Content-Type": "application/json"})
                if not r.ok:
                    r.raise_for_status()

                decoded = r.json()

                # we need to check if the optional variable limit is in the endpoint
                if 'limit' in req_line:
                    variables = req_line.partition('?')[2]

                    # if the user didn't specify a limit, we print all species in the ensembl data base
                    if variables == 'limit=':
                        title = 'List of all available species in the database:'
                        species = ''

                        # we iterate over each object (specie) stored in the API and extract the information 'name' and 'common_name'
                        for i in range(len(decoded['species'])):
                            specie = 'Common name: ' + decoded['species'][i]['common_name'] + '\n  Scientific name: ' + decoded['species'][i]['name'] + '\n\n'
                            species += specie

                    # if user enters a limit, we must only show that exact number of species
                    else:
                        # we do a partition to extract the given limit from the request line
                        limit = variables.partition('=')[2]
                        title = 'List of available species in the database (max ' + limit + '):'
                        species = ''
                        for i in range(int(limit)):
                            specie = 'Common name: ' + decoded['species'][i]['common_name'] + '\n  Scientific name: ' + decoded['species'][i]['name'] + '\n\n'
                            species += specie

                # we guarantee here that if the endpoint doesn't have the optional variable 'limit', we still print all species in the API
                else:
                    title = 'List of all available species in the database:'
                    species = ''
                    for i in range(len(decoded['species'])):
                        specie = 'Common name: ' + decoded['species'][i]['common_name'] + '\n  Scientific name: ' + decoded['species'][i]['name'] + '\n\n'
                        species += specie


                # here we open the HTML file and replace from it the word 'TITLE' for the variable 'title' shown above and '----' for the actual information extracted from Ensembl
                content = open_file(title, species)

            # we now check if the user has asked for information about the karyotype
            elif 'karyotype' in req_line:
                specie = req_line.partition('=')[2].lower()

                # we extract the information from the data base
                server = "http://rest.ensembl.org"
                ext = "/info/assembly/" + specie + "?"
                r = requests.get(server + ext, headers={"Content-Type": "application/json"})
                if not r.ok:
                    r.raise_for_status()
                    sys.exit()

                # in Ensembl, th information is stored in the object 'karyotype'
                decoded = r.json()
                kar = repr(decoded['karyotype'])

                # we replace key values in our HTML for the information extracted
                title = 'This is the Karyotype of th following specie: ' + specie
                content = open_file(title, kar)

            # here we will be giving information about the length of a chromosome of a given specie
            elif 'chromosomeLength' in req_line:

                # we extract the specie and the chromosome from the request line
                variables = req_line.partition('?')[2].partition('&')
                specie = variables[0].partition('=')[2]
                chromo = variables[2].partition('=')[2]

                # code for reaching the information in Ensembl
                server = "http://rest.ensembl.org"
                ext = "/info/assembly/" + specie + "/" + chromo + "?"
                r = requests.get(server + ext, headers={"Content-Type": "application/json"})
                if not r.ok:
                    r.raise_for_status()
                    sys.exit()

                # the information about the length of a chromosome is given by the following object in the Ensemble data base
                decoded = r.json()
                length = repr(decoded['length'])

                # we change the HTML file for printing the correct information
                title = 'The chromosome ' + chromo + ' of the ' + specie + ' species has the following length: '
                content = open_file(title, length)

            # here we will be giving the dna seq of a human gene and the information
            # as we need the gene's ID and sequence in all this endpoints, we are doing them in one single elif clause
            elif 'geneSeq' in req_line or 'geneInfo' in req_line or 'geneCalc' in req_line:

                # we need to extract the entered information by the the user: the gene
                gene = str(req_line.partition('=')[2])

                # this is the code given by the API REST for retrieving the information of the gene
                # we are searching now for the ID
                server = "http://rest.ensembl.org"
                ext = "/xrefs/symbol/homo_sapiens/" + gene + "?"
                r = requests.get(server + ext, headers={"Content-Type": "application/json"})
                if not r.ok:
                    r.raise_for_status()
                    sys.exit()

                # we need to get the ID of the gene stored in 'id' form the second index to the one before the last index
                decoded = r.json()
                ID = str(repr(decoded[0]['id'])[1:-1])

                # now that we have the ensemble ID of the given gene, we need to retrieve the DNA sequence of that gene
                # the API REST gives us following code for searching such information
                server = "http://rest.ensembl.org"
                ext = "/sequence/id/" + ID + "?"
                r = requests.get(server + ext, headers={"Content-Type": "text/plain"})
                if not r.ok:
                    r.raise_for_status()
                    sys.exit()
                sequence = r.text

                # we change the HTML file for printing the correct information
                title = 'The DNA sequence of the ' + gene + ' human gene is: '
                content = open_file(title, sequence)

                # we now want to know more information about a specific gene, therefore we use the variables described above 'gene' and 'sequence':
                if 'geneInfo' in req_line:

                    # this is the code given by the API REST for retrieving the info
                    server = "http://rest.ensembl.org"
                    ext = "/lookup/symbol/homo_sapiens/" + gene + "?expand=1"
                    r = requests.get(server + ext, headers={"Content-Type": "application/json"})
                    if not r.ok:
                        r.raise_for_status()
                        sys.exit()

                    # extract the information from the file given by the Ensembl data base
                    decoded = r.json()
                    start = repr(decoded['start'])
                    end = repr(decoded['end'])
                    chromo = repr(decoded['seq_region_name'])
                    length = len(sequence)

                    title = 'This is the required information of the ' + gene + ' human gene: '
                    info = 'ID: ' + ID + '\nThe gene\'s start is : ' + str(start) + '\nThe gene\'s end is: ' + str(end) + '\nIts length is: ' + str(length) + '\nAnd it is in the ' + str(chromo) + ' chromosome.'

                    content = open_file(title, info)

                elif 'geneCalc' in req_line:

                    length = len(sequence)

                    # we calculate the percentage of the bases
                    def perc(base, length):
                        num = sequence.count(base)
                        if num > 0:
                            perc = round(100.0 * num / length, 1)
                        else:
                            perc = 0
                        return perc

                    perca = str(perc('A', length))
                    percc = str(perc('C', length))
                    percg = str(perc('G', length))
                    perct = str(perc('T', length))

                    title = 'This are the asked calculations about the ' + gene + ' human gene: '
                    info = 'ID: ' + ID + '\nTotal length: ' + str(length) + '\nPercentage of A bases: ' + perca + '%\nPercentage of C bases: ' + percc + '%\nPercentage of G bases: ' + percg + '%\nPercentage of T bases: ' + perct + '%'

                    content = open_file(title, info)

                else:
                    pass

            # if the user wants to get a list of genes over a region, the program will enter this elif
            elif 'geneList' in req_line:

                # we are here extracting all the values of the variables entered by the user
                variables = req_line.partition('?')[2]
                chromo = variables.split('&')[0].partition('=')[2]
                start = variables.split('&')[1].partition('=')[2]
                end = variables.split('&')[2].partition('=')[2]

                # code given by the API rest for reaching the information
                server = "http://rest.ensembl.org"
                ext = "/overlap/region/human/" + chromo + ":" + start + "-" + end + "?feature=gene"
                r = requests.get(server + ext, headers={"Content-Type": "application/json"})
                if not r.ok:
                    r.raise_for_status()
                    sys.exit()
                content = r.json()

                # for every object in the list provided by the Api, we have a gene with  its respectively name and id
                # for printing them in our browser, we are creating an empty string and adding one by one iterating over the list
                genes = ''
                for i in range(len(content)):
                    gene = '\nGene: ' + str(content[i]['external_name']) + '\n    (Id: ' + str(content[i]['id']) + ')'
                    genes += gene

                title = 'This is the list of genes contained in the chromosome number ' + chromo + ' over the selected region ' + start + ' - ' + end + ':'
                content = open_file(title, genes)

            # if endpoints are wrongly entered, we show an error file
            else:
                file = open('error.html', 'r')
                content = file.read()

            # we encode our content for later printing it in the browser
            self.wfile.write(str.encode(content))


# -- MAIN PROGRAM

# connecting to server
with socketserver.TCPServer(("", PORT), TestHandler) as httpd:  # an empty IP aDdress means: 'use your own IP'

    print('Serving at PORT {}'.format(PORT))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("Stopped by the user")
        httpd.server_close()

print("")
print("Server Stopped")
