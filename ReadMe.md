# AWS Setup
After starting and logging into AWS these are the steps to setup the services for the program.
1. Search API Gateway
1.1 Create API
1.2 Choose HTTP API, build
1.3 API name: ProcessCropEvent| API Address Type: IPv4, next
1.4 Configure routes just click next
1.5 Define stages | Stage name: $default auto deploy on
1.6 Just click create all the way, then you are transfered to a UI with Routes and Routes for "ProcessCropEvent" with a create button. Click Create
1.7 Set ANY -> POST and /cloud/update
1.8 You can open this then and on the right it says ARN copy that address, and paste that address into ```CloudRoute.scala```

2. Search Lambda
2.1 Create Lambda
2.2 Name: ProcessCropEvent / Runtime: Python 3.12
2.3 Source code can be found in the root directory called ```lambda_function.py```. Upload/Copy the code into the auto generated lambda_function.py

3. Search S3 buckets
3.1 Create bucket
3.2 General purpose | Bucket name: crop-surveillance-logs-balazs (or anything but it has to be the same as in the lambda code {Original idea was to have stored different log for each teammember but then decided that it's unnecessary, and was just too lazy to change the name at that point}) Leave everything else as it is and create bucket

4. Search DynamoDB
4.1 Create table
4.2 Name: CropEvent | Partition Key: event_id
4.3 leave everything else as default
4.3 Create table

# Start up
## 1. IoT Layer
To start the IoT Layer, start it using the Docker file in ```MS2_IoT_Implementation```. This will start sending the input data from the sensors via MQTT.

## 2. Edge Layer
To start the Edge Layer, start it using the DOcker file in ```MS3_Edge_Layer_Implementation```. It starts the edge layer, handling the JSON as well as stores them in the Redis DB.

## 3.1 Clould Layer Node A
To run Cloud Layer Node A, run the Docker file in MS4_Cloud_Layer/cloud_node_a. This will start Node A, that handles anomaly detection and forwards the data to Cloud Node B.

## 3.2 Cloud Layer Node B
To run Cloud Layer Node B, run the Docker file in MS4_Cloud_Layer/cloud_node_b. This will start Node B, receiving the data from Node A, handles crop recommendation based on 2 method and forwards and stores data/logs in DynamoDB/S3 AWS services.