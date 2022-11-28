from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.http import require_POST
import cv2
import numpy as np
import json
import os
from rest_framework import status
from .models import Product
from .serializers import productSerializer
from django.core.files.storage import FileSystemStorage 


@require_POST
@api_view(["POST"]) 
def product(request):

    if request.method == 'POST':
        # request.header 
        # Content-Type: application/json
        # request.body 
        # {
        #     "name" : "<이름>.jpg",
        #     "data" : "<이름>.jpg"
        # } 
        
        # Image = request.FILES # multipart/formdata는 request.body 안됨 
        # img = Image.get('data') # 형식 어떻게 나오는지 확인 
        # cv2.imwrite("C:/Users/JYLEE/Desktop/gamul_jy/gamul/api/imgs/test_postman.jpg", img) # img를 해당 이름으로 해당 경로에 저장하고 그 경로를 쓰기
        # pInputImage = "api/imgs/<이름>.jpg"
        
        # img = request.FILES["file"]
        # img = np.array(img)
        # img_name = "dldk"
        # cv2.imwrite(img_name, img)
        
        ### 고정 ###
        pWeightpath = "C:/Users/JYLEE/Desktop/yolomodel/yolov3_custom_final.weights"
        pCfgpath = "C:/Users/JYLEE/Desktop/yolomodel/yolov3_custom (3).cfg"
        pClasspath = "C:/Users/JYLEE/Desktop/yolomodel/classes (1).names" 
        ############        
        print("여기 파일:",request.FILES)
        file = request.FILES["data[0][raw]"] # 포스트맨은 file, 리액트에서 받을 때는 data[0][raw]
        
        print(file)
        fs = FileSystemStorage("./imgs")
        filename = fs.save("object.jpg", file)
        pInputImage = "C:/Users/JYLEE/Desktop/gamul_Django/imgs/"+filename
        
        # pInputImage ="C:/Users/JYLEE/Desktop/gamul_Django/api/imgs/test22.jpg" # radish success testcase
        # pInputImage ="C:/Users/JYLEE/Desktop/gamul_Django/api/imgs/test26.jpg"  # pork success testcase
        
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
                
                if label == "radish":
                    label = "무"
                elif label == "pork":
                    label = "돼지고기"
                elif label == "egg":
                    label = "달걀"
                elif label == "onion":
                    label = "양파"
                elif label == "pear":
                    label = "배"
                elif label == "apple":
                    label = "사과"
                    
                Product.objects.create(
                    name = label,
                    confidence = int(100*confidences[i])
                )
        
        
        product = Product.objects.all()
        serializer = productSerializer(product, many=True)
        if len(product) != 0:
            context = {
                "status":"200", # 성공
                "success":"true",
                "message":"Successfully Detect Product",
                "data": serializer.data,
            }
        else:
            context = {
                "status":"400",
                "success":"false",
                "message":"Failed Detect Product",
            }  
        
        # 다시 db clear하기
        for i in range(len(product)):  
            product.delete()
            
        # 저장됐던 사진 다시 삭제
        os.remove(os.path.join("./imgs", pInputImage))
        
        
        # cors error
        # response = HttpResponse('success')
        # response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        # response["Access-Control-Allow-Origin"] = "*"
        # response["Acess-Control-Max-Age"] = "1000"
        # response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
        
        print(context)
        return Response(data=context)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    

            

    
    
