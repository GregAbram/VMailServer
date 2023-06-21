This contains the source for the straw-man VMail server.  The server is a Django app that presents an API that allows clients to create vmails and add snapshots to vmails.   Both vmails and their snapshots contain arbitrary data, represented as Json documents, plus a very few pre-defined fields: in addition to the arbitrary json content, vmails contain a 'name' field, while snapshots contain a text and media URL.

The server also implements a very simple web app to view pre-defined vmails that have been uploaded.

The server is implemented in a Docker container.  To build the container, enter the **docker** directory and run the ***build*** script.   This will create a container named *vmail*.  

To run the server initially, create two empty directories **db** and **media** in the root of this project *with full read/write/execute permissions* and run the ***run*** script.   This will launch the container and link **bb** and **media** directories.  The initial run will create the Mongo database.   Subsequently, *vmails* and *snapshots* will be inserted into the Mongo database, and any media attached to snapshots will be placed in the media directory.   NOTE: as its currently set up, the container will run detached.   You ca change it to run interactively by editting the **run** script.   Then, the choice of CMD in the Dockerfile determines whether it gives you a prompt in the container or simply spews the apache error log.

There is a CSharp progam, *Program.cs* in the examples directory.   This code demonstrates the API through which a CSharp program can upload vmails and associated snapshots to the server.   There is a line in there that specifies the IP address of the server.  The server must be running for this to work.  You will also need to modify that code soi that it can find a set of image files to install in the snapshots.

Given that the server container is running, it is accessible on port 8080 of the host.   Any system with access to the host can then utilize the API by referring to *hostname:8080*.

To access the web application, browse to *hostname:8080/vmail/vmail/*.   You will see a list of vmails on the server.   Click on one and you willbe presented with the first snapshot of that vmail; from there the buttons are self-explainatory.


