from rest_framework.response import Response
from rest_framework.decorators import api_view
import cv2
import numpy as np
import json
from .models import Product
from .serializers import productSerializer


@api_view(["POST"]) 
def product(request):
    # 만약에 request바디를 받고 제대로 작동안하면 imgs파일에 저장하고 그 path를 사용해서 넣기
    # Image = request.FILES # multipart/formdata는 request.body 안됨 
    # img = Image.get('name')
    # cv2.imwrite("C:/Users/JYLEE/Desktop/gamul_jy/gamul/api/imgs/<>.jpg", img) # img를 해당 이름으로 해당 경로에 저장하고 그 경로를 쓰기
    # pInputImage = "api/imgs/<>.jpg"
    
    ### 고정 ###
    pWeightpath = "C:/Users/JYLEE/Desktop/yolomodel/yolov3_custom_final.weights"
    pCfgpath = "C:/Users/JYLEE/Desktop/yolomodel/yolov3_custom (3).cfg"
    pClasspath = "C:/Users/JYLEE/Desktop/yolomodel/classes (1).names" 
    ############
    

    ## 리액트에서 받을 것 : test
    # pInputImage ="C:/Users/JYLEE/Desktop/gamul_Django/api/imgs/test22.jpg" # radish success testcase
    pInputImage ="C:/Users/JYLEE/Desktop/gamul_Django/api/imgs/test26.jpg"  # pork success testcase
    # Load Yolo
    net = cv2.dnn.readNet(pWeightpath, pCfgpath) 
    classes = []
    with open(pClasspath, "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()

    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    
    # Loading image
    img = cv2.imread(pInputImage) 
    img = cv2.resize(img, None, fx=0.9, fy=0.9)

    height, width, channels = img.shape
    

    # Detecting objects
    blob = cv2.dnn.blobFromImage(
        img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers) 
    
    # 탐지한 객체의 클래스 예측 
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out: 
            scores = detection[5:]
            class_id = np.argmax(scores) # score중에 가장 큰 값을 가지는 index를 반환 
            confidence = scores[class_id]

            if confidence > 0.5: # names파일에서 원하는 객체 id에서 -1하기(선택사항)
                # 탐지한 객체 박싱
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                
                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
            
            
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    font = cv2.FONT_HERSHEY_PLAIN
    
    for i in range(len(boxes)):
        if i in indexes:
            colors = np.random.uniform(0, 255, size=(len(classes), len(boxes)))
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            color = 255
            cv2.rectangle(img, (x, y), (x + w, y + h), 255, 2)
            cv2.putText(
                img, label + str(int(100*confidences[i])), (x, y + 30), font, 1, color, 3)
            
            Product.objects.create(
                name = label,
                confidence = int(100*confidences[i])
            )
    
    
    product = Product.objects.all()
    serializer = productSerializer(product, many=True)
    if len(product) != 0:
        context = {
            "status":"200",
            "success":"true",
            "message":"Successfully Detect Product",
            'data': serializer.data,
        }
    else:
        context = {
            "status":"400",
            "success":"false",
            "message":"Failed Detect Product",
        }
    print(serializer.data)    
    
    # 다시 db clear하기
    for i in range(len(product)):  
        product.delete()
    
    return Response(data=context)
    
    

            

    
    
