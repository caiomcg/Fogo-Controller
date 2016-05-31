# Fogo-Controller
A simple Python HTTP Restful server for the Fogo Controller Android and iOS APP.

The script uses Flask Restful to build a simple HTTP server on Python 2, in a
future release the code will be revised to comply with Python 3 standards. 

### Requirements ###

* **[Python 2.3.1 or above](https://www.python.org/)** :white_check_mark:
* **[Flask Restful 0.3.4 or above](http://flask-restful-cn.readthedocs.io/en/0.3.4/)** :white_check_mark:

### Installation ###

**Implementation notes: The Following methods were tested under Ubuntu 14.04 LTS.**

##### Script #####

To make the user experience even better we provide a shell script to install the Fogo-Controller Python server.
In order to run the script move to the folder where the project is located and run the following command: `./install_controler.sh`.

##### Manually #####

To manually install the dependencies you will have to:

1. Check if Python is installed and update the build.
2. Install python-pip.
3. Install Requests.
4. Install Flask.
5. Install Flask Restful.

## Executing

To run the script you will have to:

1. Move to the folder containing the script.
2. Run the Python Script: `./Fogo-Controller.py`.

**The script requires two arguments to start: [The Machine Name] [The Manager IP Address].**

```
./Fogo-Controller.py Fogo-PC-1 192.168.0.22
```

## Program Behaviour

Once the script starts an HTTP server will be executed at `http://localhost:5000` and your machine will communicate with the HTTP manager server. At this point the application will wait for requests that will activate the Fogo Player modules. These requests will be controlled by your Android or iOS device.
