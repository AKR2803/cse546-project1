from flask import Flask, request, jsonify

import boto3

REGION = 'us-east-1'  # Replace with your region if different

s3_client = boto3.client('s3', region_name=REGION)
simpledb_client = boto3.client('sdb', region_name=REGION)
SIMPLEDB_DOMAIN = '1232886878-simpleDB'  # Replace with your ASU ID
S3_INPUT_BUCKET = '1232886878-in-bucket'  # Replace with your S3 bucket name

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def handle_upload():
    if request.method == 'POST':
        print("Inside POST")
        if 'inputFile' not in request.files:
            return jsonify({"error": "No inputFile provided"}), 400
        
        input_files = request.files.getlist('inputFile')
        response = {}

        for f1 in input_files:
            file_name = str(f1.filename).split('.')[0]
            
            # Upload the file to S3
            s3_client.upload_fileobj(f1, S3_INPUT_BUCKET, f1.filename)

            # Query SimpleDB for the recognition result
            db_response = simpledb_client.get_attributes(
                DomainName=SIMPLEDB_DOMAIN,
                ItemName=file_name,
                AttributeNames=['prediction']
            )

            prediction = db_response['Attributes'][0]['Value'] if 'Attributes' in db_response else 'Unknown'
            response[file_name] = prediction

        # Return the result in the required format
        # return f"{file_name}:{prediction}", 200     

        response_text = "\n".join([f"{key}: {value}" for key, value in response.items()])
        return response_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    else:
        # Render the HTML form for GET requests
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>File Upload</title>
        </head>
        <body>
            <h1>Upload a File</h1>
            <form action="/" method="post" enctype="multipart/form-data">
                <input type="file" name="inputFile" multiple>
                <button type="submit">Upload</button>
            </form>
        </body>
        </html>
        '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
