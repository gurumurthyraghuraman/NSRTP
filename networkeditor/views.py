import json
import uuid
from networkeditor import genricfault, specifiedfault
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render
from networkeditor.models import nsrpt, networkconnection, graphdata, networkconn
from django.contrib.gis.geos import Point, GEOSGeometry
from shapely.geometry import MultiPoint

def index(request):
    print("Hello")
    data = {'mydata' : "Network Science Research Tool Project"}
    return render(request, 'networkeditor/main.html', data)

def faultAnalyzer(request):
    data = {'mydata': "Network Science Research Tool Project"}
    return render(request, 'networkeditor/Fault_analyzer.html', data)

def savedata(request):
    if request.method == 'POST':
        lat = request.POST['lat']
        long = request.POST['long']

        nsrpt.objects.create(
            latitude=lat,
            longitude=long
        )
    response_data = {"lat": lat, "long": long}
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def fetchdata(request):
    data1 = nsrpt.objects.all();
    data = serializers.serialize('json', data1)
    print(data)
    return HttpResponse(data, content_type="application/json")

def savenetwork(request):
    uid = uuid.uuid4();
    graphname = request.GET.get('name', '')
    print(graphname)
    if request.method == 'POST':
        #name = request.POST.get('name', False)
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        print(len(data))
        print(data)
        print(data[0]['latitude'])
        print(data[0]['connectednodes'][0])
        Lat = data[0]['latitude']
        Long = data[0]['longitude']

        graphdata.objects.create(
            graphname=graphname,
            graphid=uid
        )

        networkconnection.objects.create(
            networkid = uid,
            LatLong = GEOSGeometry('POINT(34.223 -110.423)'),
            ConnectedPoints = data[0]['connectednodes']
        )

        for i in range(0, len(data)):
            networkconn.objects.create(
            networkid = uid,
            Lat = data[i]['latitude'],
            Long = data[i]['longitude'],
            ConnectedPoints = data[i]['connectednodes'],
            LatLongId = data[i]['uid'],
            #LatLonx = data[i]['latlonx'],
            #LatLongy = data[i]['latlony']
            )

    response_data = {"data" : data}
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def fetchnetwork(request):
    network = networkconnection.objects.all();
    data = serializers.serialize('json', network)
    print(data)
    return HttpResponse(data, content_type="application/json")

def loadnetwork(request):
    graphname = request.GET.get('name', '')
    network = networkconn.objects.raw("select * from public.networkeditor_networkconn n, public.networkeditor_graphdata g where g.graphname = '"+graphname+"' and g.graphid=n.networkid")
    data = serializers.serialize('json', network)
    #print(data)
    return HttpResponse(data, content_type="application/json")

def fetchGraphName(request):
    network = graphdata.objects.raw("select * from public.networkeditor_graphdata")
    data = serializers.serialize('json', network)
    #print(data)
    return HttpResponse(data, content_type="application/json")

def genfault(request):
    radius = request.GET.get('radius', '')
    #print(radius)
    graphname = request.GET.get('network','')
    #print(graphname)
    network = networkconn.objects.raw("select * from public.networkeditor_networkconn n, public.networkeditor_graphdata g where g.graphname = '"+graphname+"' and g.graphid=n.networkid")
    data = serializers.serialize('json', network)
    genNetwork = dict()
    for obj in network:
        genNetwork[obj.LatLongId] = Point(obj.Lat, obj.Long)
        #print(genNetwork)
        #print(obj.Lat)
    graph = dict()
    for obj in network:
        aa = genNetwork[obj.LatLongId]
        ll = list()
        for i in range(0, len(obj.ConnectedPoints)):
            #print(obj.ConnectedPoints[i])
            ll.append(genNetwork[obj.ConnectedPoints[i]])
        graph[(aa.x, aa.y)] = ll
    #print(graph)
    #print(genricfault.r)
    graph = genricfault.convert_graph_to_reqd_format(graph)
    #print(graph)
    genricfault.r = int(radius)
    graphmerc = genricfault.convert_input_graph_to_mercator(graph)
    #print("Graph from Views.py")
    #print(genricfault.str_of_graph(graph))
    a, b, c, d, e = genricfault.compute_generic_fault(graphmerc)
    #print(a)
    #print(b)
    #print(c)
    #print(d)
    #print(e)
    data1 = {"a" : a, "b" : b, "c" : c, "d" : d, "e" : e}
    #data2 = {"a" : a}
    return HttpResponse(json.dumps(data1), content_type="application/json")

def specificfault(request):
    graphname = request.POST.get('name', '')
    #print(graphname)
    markerarr = request.POST.getlist('markerarr[]')
    #print(markerarr)
    #print(markerarr[0])
    network = networkconn.objects.raw("select * from public.networkeditor_networkconn n, public.networkeditor_graphdata g where g.graphname = '" + graphname + "' and g.graphid=n.networkid")
    data = serializers.serialize('json', network)
    genNetwork = dict()
    for obj in network:
        genNetwork[obj.LatLongId] = Point(obj.Lat, obj.Long)
        #print(genNetwork)
        #print(obj.Lat)
    graph = dict()
    for obj in network:
        aa = genNetwork[obj.LatLongId]
        ll = list()
        for i in range(0, len(obj.ConnectedPoints)):
            #print(obj.ConnectedPoints[i])
            ll.append(genNetwork[obj.ConnectedPoints[i]])
        graph[(aa.x, aa.y)] = ll
    #print(graph)
    #print(genricfault.r)
    graph = genricfault.convert_graph_to_reqd_format(graph)
    input_graph = genricfault.convert_input_graph_to_mercator(graph)
    lspec = list()
    for eachPolygonPoint in markerarr:
        y = ((eachPolygonPoint.strip("()")).replace(" ", "")).split(",")
        #print(y[0])
        #print(y[1])
        lspec.append((genricfault.merc_x(float(y[1])), genricfault.merc_y(float(y[0]))))

    #print(lspec)
    mul_l_spec = MultiPoint(lspec)
    #print(mul_l_spec)
    f, g, h,i, j = specifiedfault.specified_fault(input_graph, mul_l_spec)
    #print(f)
    #print(g)
    #print(h)
    #print(i)
    #print(j)
    #print(json.dumps(markerarr))
    data1 = {"a": f, "b": g, "c": h, "d": i, "e": j}
    return HttpResponse(json.dumps(data1), content_type="application/json")