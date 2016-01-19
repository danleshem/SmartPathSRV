import json
from flask import Flask, jsonify, Response, make_response, request
from flask.ext.cors import CORS
import googlemaps
import datetime

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route('/api/v1.0/query', methods=['POST'])
def query():

    post = request.get_json()

    print(post)

    origins      = post.get('origins')
    destinations = post.get('destinations')
    hour         = float(post.get('hour'))

    gmaps = googlemaps.Client(key='AIzaSyBVRtAf-hg-YYA4RynxjwKWMC8PB8-WFDc')

    #results
    gmaps_result = {}
    data = [0,1,2, 3]

    modes = ('walking', 'driving', 'transit', 'taxi')

    global time_is_money
    time_is_money = hour

    for i in range(len(modes)):

        if modes[i] == 'taxi':
            mode = 'driving'
        else:
            mode = modes[i]

        gmaps_result[mode] = gmaps.distance_matrix(origins = origins, destinations = destinations, mode=mode)
        distance = gmaps_result[mode]['rows'][0]['elements'][0]['distance']
        duration = gmaps_result[mode]['rows'][0]['elements'][0]['duration']

        data[i] = {
            'distance': distance,
            'duration': duration,
            'cost': cost_determniator(modes[i], distance['value'], duration['value'] ),
            'mode': modes[i]
        }


    data = sorted(data, key=lambda k: k['cost']['total_cost'])
    newdata = {'data': data}

    return make_response(jsonify(newdata))

def cost_determniator(mode = None, distance = None, duration = None):

    #CONSTANTS
    BUS_TICKET_COST = 6.9
    #TIME_IS_MONEY   = 100
    GASOLINE_LITER_COST   = 5.9
    GASOLINE_CONSSUMING   = 10 #1:10

    if mode == 'driving':
        cost = round( (distance/1000/GASOLINE_CONSSUMING)*GASOLINE_LITER_COST, 2 )

    if mode == 'walking':
        cost = 0

    if mode == 'transit':
        cost = BUS_TICKET_COST

    if mode == 'taxi':
        #RATE 1
        if datetime.time(5, 30, 0) <= datetime.time(21, 30, 0):
            grace_time = 80
            pulse      = 11
        else:
            grace_time = 35
            pulse      = 9

        cost = 12.3 + (duration-grace_time)/(pulse)*0.3

    total_cost = round(cost + (duration/60)*(time_is_money/60), 2)

    return {'cost': round(cost, 2), 'total_cost': total_cost}

if __name__ == '__main__':
    app.debug = True
    app.run()

    #changes