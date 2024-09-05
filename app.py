from flask import Flask, request, jsonify
import os
import pandas as pd
from werkzeug.utils import secure_filename
from plot import *
app = Flask(__name__)
from flask_cors import CORS
CORS(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/process-file', methods=['POST'])
def process_file():
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    plot_type = request.form.get('plotType')
    timeInterval = request.form.get('timeInterval')
    startdate = request.form.get('startDate')
    endDate = request.form.get('endDate')
    predict_date = request.form.get('predict_date')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    df = pd.read_excel(file_path)
    if plot_type != 'asaoka':
        graph = Graph(df,startdate, endDate,predict_date)    
    graph = Graph(df,startdate, endDate,predict_date,timeInterval)
    basic_x,basic_y = graph.basic_plot()

    if plot_type == 'hyperbolic':
        ori_x,ori_y,ori_y2, reg_x, reg_y,reg_y2,t_pred,so,a,b,sf,sl =graph.hyperbolic_plot()
        response_data = {
            'basic_x': basic_x.tolist(), 
            'basic_y': basic_y.tolist(),
            'ori_x': ori_x, 
            'ori_y': ori_y,
            'ori_y2': ori_y2,
            'reg_x': reg_x.tolist(),
            'reg_y': reg_y.tolist(),
            'reg_y2': reg_y2.tolist(),
            'plottype': plot_type,
            't_pred': t_pred.to_list(),
            'so': so,
            'a': a,
            'b': b,
            'sf': sf,
            'sl': sl
        }

    elif plot_type == 'hosino':
        ori_x,ori_y,ori_y2, reg_x, reg_y,reg_y2,t_pred,so,a,b,sf,sl =graph.hosino_plot()
        response_data = {
            'basic_x': basic_x.tolist(), 
            'basic_y': basic_y.tolist(),
            'ori_x': ori_x, 
            'ori_y': ori_y,
            'ori_y2': ori_y2,
            'reg_x': reg_x.tolist(),
            'reg_y': reg_y.tolist(),
            'reg_y2': reg_y2.tolist(),
            'plottype': plot_type,
            't_pred': t_pred.to_list(),
            'so': so,
            'a': a,
            'b': b,
            'sf': sf,
            'sl': sl
        }

    elif plot_type == 'asaoka':
        ori_x,ori_y, ori_y2,so,a,b,sf,timeInterval,x_cross, y_cross, x_range, x_min,x_max,t_pred,s1,sl,real_dates,real_values = graph.asaoka_plot()
        response_data = {
            'basic_x': basic_x.tolist(), 
            'basic_y': basic_y.tolist(),
            'ori_x': ori_x, 
            'ori_y': ori_y,
            'ori_y2': ori_y2,
            'plottype': plot_type,
            'so': so,
            'a': a,
            'b': b,
            'sf': sf,
            'timeInterval': timeInterval,
            'x_cross' : x_cross, 'y_cross':y_cross, 'x_range':x_range, 'x_min':x_min,'x_max':x_max,
            't_pred': t_pred.to_list(),'s1':s1.to_list(),'sl':sl,'real_dates': real_dates,'real_values': real_values
        }
    else:
        return jsonify({'error': 'Invalid plot type'}), 400
    os.remove(file_path)

    return jsonify(response_data), 200

if __name__ == '__main__':
    app.run(port=5000)
