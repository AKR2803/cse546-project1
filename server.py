import boto3
from flask import Flask, request, jsonify

s3_client = boto3.client('s3', region_name='us-east-1')
simpledb_client = boto3.client('sdb', region_name='us-east-1')

simpledb_domain = '1232886878-simpleDB'
s3_bucket = '1232886878-in-bucket'

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def handle_upload():
    # post request
    if request.method == 'POST':
        print("Inside POST method...")

        input_files = request.files.getlist('inputFile')
        response = {}

        for f1 in input_files:
            file_name = str(f1.filename).split('.')[0]
            
            # upload file to s3 bucket "1232886878-in-bucket"
            s3_client.upload_fileobj(f1, s3_bucket, f1.filename)

            # fetch result from simpledb
            db_response = simpledb_client.get_attributes(
                DomainName=simpledb_domain,
                ItemName=file_name,
                AttributeNames=['prediction']
            )

            prediction = db_response['Attributes'][0]['Value'] if 'Attributes' in db_response else 'None'
            response[file_name] = prediction

        response_text = "\n".join([f"{key}: {value}" for key, value in response.items()])
        return response_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    else:
        # get request form
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>CSE546 - Project1</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                body {
                    display: flex;
                    font-family: system-ui, sans-serif;
                    justify-content: center;
                    align-items: center;
                    color: #333;
                }
                h1 {
                    color: #4CAF50;
                    margin-bottom: 1rem;
                }
                form {
                    padding: 2rem;
                    border-radius: 8px;
                    border: 1px solid #000;
                    text-align: center;
                }
                input[type="file"] {
                    margin-bottom: 1rem;
                    padding: 10px;
                    border-radius: 4px;
                    background-color: #d4ffcd;
                }
                button {
                    background-color: #4CAF50;
                    color: #fff;
                    padding: 1rem;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                    transition: all 0.2s ease-in-out;
                }
                button:hover {
                    background-color: #145017;
                }
            </style>
        </head>
        <body>
            <div>
                <h1>Project 1 - Face Recognition</h1>
                <p>Please choose an image for Face Recognition</p>
                <form action="/" method="POST" enctype="multipart/form-data">
                    <input type="file" multiple name="inputFile">
                    <br>
                    <button type="submit">Submit Image</button>
                </form>
            </div>
        </body>
        </html>
        '''

if __name__ == '__main__':
    # listen on "/" 8000
    app.run(host='0.0.0.0', port=8000)