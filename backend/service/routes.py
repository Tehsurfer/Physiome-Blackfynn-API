from flask import jsonify
from flask import request
from blackfynn import Blackfynn
import urllib2

from service.app import app
from service.config import Config
import json
import csv
import numpy as np

bf = None
global user_ip
global data
storedData = {}
user_ip = None

# NOTE: connect_to_blackfynn() is a temporary workaround that can be used to login to Blackfynn without
# having to make a POST request

# @app.before_first_request
def connect_to_blackfynn():
    global bf
    bf = Blackfynn(
        api_token=Config.BLACKFYNN_API_TOKEN,
        api_secret=Config.BLACKFYNN_API_SECRET,
        env_override=False,
        host=Config.BLACKFYNN_API_HOST,
        concepts_api_host=Config.BLACKFYNN_CONCEPTS_API_HOST
    )


@app.route('/api/', methods=['GET'])
def home():
    return ('Welcome to a link to the Blackfynn API. Documentation coming soon but for now'
            + 'check out https://github.com/Tehsurfer/Physiome-Blackfynn-API')

@app.route('/', methods=['GET'])
def home2():
    return ('Welcome to a link to the Blackfynn API. Documentation coming soon but for now'
            + 'check out https://github.com/Tehsurfer/Physiome-Blackfynn-API')

@app.route('/dataset/<id>', methods=['GET'])
def dataset(id):
    if not ip_logged_in(request):
        return 'Not logged in'
    dataset = bf.get_dataset(id)
    return 'Dataset: {}'.format(dataset.name)


# This route logs in with a given api token and secret and returns the available 
@app.route('/get_timeseries_dataset_names', methods=['POST'])
def get_timeseries_dataset_names():
    data = json.loads(request.data.decode("utf-8"))

    global bf
    bf = Blackfynn(api_token=data['tokenId'], api_secret=data['secret'])
    data_sets = bf.datasets()

    global time_series_items
    time_series_items = []
    time_series_names = []
    for data_set in data_sets:
        for item in data_set.items:
            if item.type is 'TimeSeries':
                time_series_items.append(item)
                time_series_names.append(item.name)

    global user_ip
    user_ip = request.remote_addr
    return json.dumps({'names': time_series_names})

# /api/get_channel_data: Returns the data relating to the first channel of a given
#      dataset
@app.route('/get_channel_data', methods=['GET'])
def datasets():
    if not ip_logged_in(request):
        pass
        #return 'Not logged in'

    name = request.headers['Name']
    channel = request.headers['Channel']
    channel = channel.decode('utf-8')

    global bf
    global time_series_items
    data = []
    channel_array = []
    for item in time_series_items:
        print(item.name)
        if item.name == name:
            data = item.get_data(length='2s')
    for key in data:
        channel_array = data[key]
        break
    return json.dumps({'data': str(channel_array.tolist())})

# /api/get_channels: Returns channel names for a given dataset
@app.route('/get_channels', methods=['GET'])
def channels():
    if not ip_logged_in(request):
        pass
        #return 'Not logged in'

    name = request.headers['Name']
    global bf
    global time_series_items
    global storedData
    storedData = {}
    data = []
    channel_names = []
    for item in time_series_items:
        print(item.name)
        if item.name == name:
            data = item.get_data(length='1s')
    for key in data:
        channel_names.append(key)
    return json.dumps({'data': channel_names}) 

# /api/get_channel: Returns data for a single channel
@app.route('/get_channel', methods=['GET'])
def get_channel():
    if not ip_logged_in(request):
        pass
        #return 'Not logged in'

    name = request.headers['Name']
    requested_channel = request.headers['Channel']
    #requested_channel = requested_channel.decode("utf-8")
    print('request is:' + requested_channel)
    global bf
    global time_series_items
    global storedData
    data = []
    channel_names = []
    for item in time_series_items:
        if item.name == name:
            print 'found name'
            for channel in item.channels:
                print channel
                if channel.name == requested_channel:
                    data = channel.get_data(length='2s')
                    print 'data is: '
                    print data
                    storedData[requested_channel.decode('utf-8')] = data[requested_channel.decode('utf-8')].tolist()


    return json.dumps({'data': str(data[requested_channel.decode('utf-8')].tolist())})

# /api/get_file: Returns a file in blackfynn of a given name
@app.route('/get_file', methods=['GET'])
def get_file():
    if not ip_logged_in(request):
        pass
        #return 'Not logged in'

    file_name = request.headers['FileName']
    print('request is: ' + file_name)
    global bf
    try:
        dataset = bf.get_dataset('Zinc Exports')
        print dataset.name
    except:
        return 'Error: Cannot find the Zinc Exports dataset'
    try:
        File_DataPackage = dataset.get_items_by_name(file_name)
        print File_DataPackage
    except:
        return 'Error: Cannot find the requested File'

    return urllib2.urlopen(File_DataPackage[0].view[0].url).read()

@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200

@app.route("/create_openCOR_URL", methods=["GET"])
def createURL():
    baseURL = 'https://blackfynnpythonlink.ml/data/'
    baseFilePath = '/var/www/html/data/'
    randomURL = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
    write_opencor(baseFilePath+randomURL,storedData)
    return json.dumps({'url': baseURL+randomURL+'.csv'})

def ip_logged_in(request):
    global user_ip
    if user_ip is request.remote_addr:
        return True
    else:
        return False


def write_opencor(filename, data):
    f = csv.writer(open(filename, "w", newline=''))
    datakeys = ['environment | time (unknown unit)']
    for key in data:
        # note that we assume the keys here are in integers between 1-100. The %02d is to switch numbers such as '2' to '02'
        datakeys.append(' values | '+ key+ ' (unknown unit)')
    f.writerow(datakeys)
    size = len(data[next(iter(data))])

    # currently time is 1->len(data)
    time = np.linspace(0, size - 1, size)
    for i, unused in enumerate(data[next(iter(data))]):
        row = [time[i].tolist()]
        for key in data:
            row.append(data[key][i])
        f.writerow(row)

    f.close()
