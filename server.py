import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import base64
import io
#from flask import Flask
#from main_loop import gravity_step
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_daq as daq
from input_loop import data_divide
from adjust_calc import km_to_au, au_to_km
from math import sqrt,pow
from copy import deepcopy

standard_columns=['Name',"x",'y','z','vx','vy','vz','GM']
def gravity_step(obj_a,obj_b, time_step=1):
    #Newtonian approximation, accurate to within 1.112*10^-17 of the final value
    diffx=obj_a[0][0]-obj_b[0][0]
    diffy=obj_a[0][1]-obj_b[0][1]
    diffz=obj_a[0][2]-obj_b[0][2]
    dist2=pow(diffx,2)+pow(diffy,2)+pow(diffz,2)
    dv=time_step*obj_b[2]/dist2
    dist=sqrt(dist2)
    obj_a[1][0]-=dv*diffx/dist
    obj_a[1][1]-=dv*diffy/dist
    obj_a[1][2]-=dv*diffz/dist
    return obj_a

def process_loop(timestep,simulate_until,indata):
    print("process_loop")
    time=0
    output=[]
    data=deepcopy(indata)
    while time<simulate_until:
        for a in data:
            for b in data:
                if a != b:
                    a = gravity_step(a, b, timestep)
        for a in data:
            a[0][0] += a[1][0] * timestep
            a[0][1] += a[1][1] * timestep
            a[0][2] += a[1][2] * timestep
        #if time==5:
        #    data[1][0][0] = 2
        time += timestep
        ts=[time]
        ts.extend([[co for co in a[0]] for a in data])
        output.append(ts)
    #print(output)
    print("Fin")
    return output
app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.H1(children='Online Orbital Gravity Simulator'),
    dcc.Upload(id='input_data',children=html.Div(['Drag and Drop or ',html.A('Select Files')]),style={'width': '50%','height': '60px','lineHeight': '60px','borderWidth': '1px','borderStyle': 'dashed','borderRadius': '5px','textAlign': 'center','margin': '10px'},),
    dash_table.DataTable(id="input_table",columns=[{'name':standard_columns[n],'id':n} for n in range(len(standard_columns))],data=[{"Name":"bleh","x":"splango"},{"Name":"foo","y":"bar"}],editable=True),
    #html.Button('Add Object',id='add_rows_button',n_clicks=0),
    #html.Div(id='data_container'),
    html.Div(children='Select Units'),
    dcc.RadioItems(options=[{'label': 'Kilometers','value':'KM'},{'label': 'Astronomical Units','value':'AU'}],value='AU',id="unit_radio"),
    #html.Span(children=[
    html.Span('Time Step (Days)'),
    daq.NumericInput(id="timestep",min=1,value=1),
    #html.Span('Days')]),
    #html.Span(children=[
    html.Span('Duration (Days)'),
    daq.NumericInput(id="duration",min=1,value=1,max=100000000),
    #html.Span('Days')]),
    html.Button('Start',id="run_button",n_clicks=0),
    dcc.Store(id="orbit_data"),

    #dcc.Graph(figure=go.Figure(data=[],layout=),id='graph')
    dcc.Graph(figure=go.Figure(),id='graph')
])


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if 'csv' in filename:
        df= pd.read_csv(io.StringIO(decoded.decode('utf-8')),header=None)
    elif 'xls' in filename:
        df= pd.read_excel(io.BytesIO(decoded))
    return df
    #return html.Div([html.H5(filename),dash_table.DataTable(id=input_table,data=df.to_dict('rows'),columns=[{'name': i, 'id': i} for i in df.columns]),html.Hr()])

def read_table(data,columns):
    print("read_table")
    out_list=[]
    lookup_dict={col['name']:col['id'] for col in columns}
    for row in data:
        print(len(row))
        lup=[lookup_dict[v] for v in standard_columns]
        print(str(lup))
        print(str(row))
        in_list=[[row[str(lookup_dict['x'])],row[str(lookup_dict['y'])],row[str(lookup_dict['z'])]],[row[str(lookup_dict['vx'])],row[str(lookup_dict['vy'])],row[str(lookup_dict['vz'])]],row[str(lookup_dict['GM'])]]
        #for val in row.values():
        #    in_list.append(val)
        out_list.append(in_list)
    return out_list

def generate_colorscale(num,tot):
    scale=[]
    for n in range(1,10):
        scale.append([(n-1)/10,'rgb('+str(255*n/10)+","+str(255*(1-(num/tot)))+",0)"])
        scale.append([n/10,'rgb('+str(255*n/10)+","+str(255*(1-(num/tot)))+",0)"]) #str(255*num/tot)
    return scale

def generate_colorway(tot):
    way=[]
    for n in range(tot):
        #col='rgb('+str(int(255*n/tot))+","+str(int(255*(1-(n/tot))))+",255)"
        col='#'+format(int(16777215*n/tot))[-6:].zfill(6)
        way.extend([col,col])
    print(way)
    return way
def output_to_graph(data):
    print("output_to_graph")
    '''objects=[[[],[],[]] for o in range(1,len(data[0]))]
    for t in range(len(data)):
        for o in range(1,len(data[t])-1):
            try:
                objects[o-1][0].append(data[t][o][0][0])
                objects[o-1][1].append(data[t][o][0][1])
                objects[o-1][2].append(data[t][o][0][2])
            except IndexError:
                print(str(data[t]))
                raise IndexError("IndexError at o="+str(o)+" and t="+str(t))
    print(len(data))
    print(len(objects[0][0]))'''
    trace=[]
    for o in range(1,len(data[0])):
        xs=[]
        ys=[]
        zs=[]
        for t in range(len(data)):
            xs.append(data[t][o][0])
            ys.append(data[t][o][1])
            zs.append(data[t][o][2])
        #trace.append(go.Scatter3d(x=xs,y=ys,z=zs,line=dict(cmax=len(data),cmin=0,color=[n for n in range(len(data))],colorscale=generate_colorscale(o,len(data[0])),width=5),mode='lines'))
        trace.append(go.Scatter3d(x=xs, y=ys, z=zs, line=dict(width=5),mode='lines'))
        trace.append(go.Scatter3d(x=[xs[-1]],y=[ys[-1]],z=[zs[-1]],mode='markers+text'))
    #x=[a[1][0] for a in data]
    #y=[a[1][1] for a in data]
    #z=[a[1][2] for a in data]
    #trace=[go.Scatter3d(x=x,y=y,z=z)]

    #trace=[go.Scatter3d(x=a[0],y=a[1],z=a[2],line=dict(color='#1f77b4',width=2)) for a in objects]
    return trace
@app.callback(dash.dependencies.Output('input_table', 'data'),[dash.dependencies.Input('input_data', 'contents')],[dash.dependencies.State('input_data', 'filename')])
def update_table(contents, filename): # THIS IS THE PROBLEM--- THE TABLE IS NOT BEING UPDATED AT ALL
    #ctx = dash.callback_context
    if contents is None:
        return [{}]
    df = parse_contents(contents, filename)
    dct=df.to_dict('rows')
    return dct

'''@app.callback(dash.dependencies.Output('data_container', 'children'),[dash.dependencies.Input('input_data', 'contents')],[dash.dependencies.State('input_data', 'filename')])
def update_output(contents,filename):
   if contents==None:
       return
   df=parse_contents(contents,filename)
   return html.Div([html.H5(filename), dash_table.DataTable(id='input_table', data=df.to_dict('rows'),columns=[{'name': standard_columns[i], 'id': df.columns[i]} for i in range(len(df.columns))]),html.Button('Add Object',id='add_rows_button',n_clicks=0),html.Hr()])'''
@app.callback(dash.dependencies.Output('orbit_data', 'data'),[dash.dependencies.Input('run_button','n_clicks')],[dash.dependencies.State('input_table','data'),dash.dependencies.State('unit_radio',"value"),dash.dependencies.State('timestep',"value"),dash.dependencies.State('duration','value'),dash.dependencies.State('input_table','columns')])
def grav_funct(n_clicks,input1,input2,input3,input4,input5):
    print("grav_funct")
    if n_clicks>0 and input5 != None:
        dat=process_loop(input3,input4,read_table(input1,input5))
        return dat
app.config['suppress_callback_exceptions']=True
'''@app.callback(dash.dependencies.Output('input_table','data'),[dash.dependencies.Input('add_rows_button','n_clicks')],[dash.dependencies.State('input_table','rows'),dash.dependencies.State('input_table','rows')])          #Editable table
def add_row(n_clicks,rows,columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows'''
@app.callback(dash.dependencies.Output('graph', 'figure'),[dash.dependencies.Input('orbit_data','data')])       #Make the graph
def graph_funct(data):
    print("graph_funct")
    if data==None:
        return go.Figure()
    trace=output_to_graph(data)
    lay=dict(width=800,height=800,autosize=False,colorway=generate_colorway(len(data[0])),scene=dict( xaxis=dict(
            gridcolor='rgb(255, 255, 255)',
            zerolinecolor='rgb(255, 255, 255)',
            showbackground=True,
            backgroundcolor='rgb(230, 230,230)'
        ),
        yaxis=dict(
            gridcolor='rgb(255, 255, 255)',
            zerolinecolor='rgb(255, 255, 255)',
            showbackground=True,
            backgroundcolor='rgb(230, 230,230)'
        ),
        zaxis=dict(
            gridcolor='rgb(255, 255, 255)',
            zerolinecolor='rgb(255, 255, 255)',
            showbackground=True,
            backgroundcolor='rgb(230, 230,230)'
        ),
        camera=dict(
            up=dict(
                x=0,
                y=0,
                z=1
            ),
            eye=dict(
                x=-5,
                y=5,
                z=5,
            )
        ),
        aspectratio = dict( x=4, y=4, z=4 ),
        aspectmode = 'manual'))
    return go.Figure(data=trace,layout=lay)
if __name__ == '__main__':
    app.run_server(debug=True)