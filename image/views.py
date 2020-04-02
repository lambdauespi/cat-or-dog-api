from django.shortcuts import render
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Image
from rest_framework.response import Response
from .serializers import ImageSerializer
from rest_framework import status
from rest_framework.views import APIView
from cloudinary.templatetags import cloudinary
from random import randint
from django.conf import settings
import copy
import cloudinary.uploader
from keras.preprocessing import image
import tensorflow as tf
import numpy as np


# Create your views here.

# cnn_model = copy.copy(settings.CNN_MODEL)
cnn_model = tf.lite.Interpreter(model_path='api/cnn/gato_cachorro.tflite')
cnn_model.allocate_tensors()
img_width = 128
img_height = 128
file_types = ['png','jpg','jpeg']

class ImageList(APIView):
    serializer_class = ImageSerializer
    def get(self, request, format=None):
        images = Image.objects.all()
        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
class ImagePredict(APIView):
    parser_classes = (MultiPartParser, FormParser,)
    serializer_class = ImageSerializer
    
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                ## modelo novo
                in_index = cnn_model.get_input_details()[0]["index"]
                out_index = cnn_model.get_output_details()[0]["index"]
                ## ..
                
                img_req = request.FILES['imageFile']
                if(img_req.name.split(".")[-1].lower() not in file_types):
                    return Response({'message': 'Certifique-se que sua imagem está entre os formatos de PNG, JPG ou JPEG'}, status.HTTP_400_BAD_REQUEST)
                
                img = image.load_img(img_req, target_size = (img_width, img_height))
                img = image.img_to_array(img)
                img = np.expand_dims(img, axis = 0)
                
                ## modelo novo
                img = img.astype('float32')

                img = img/255
                
                cnn_model.set_tensor(in_index, img)
                cnn_model.invoke()
                x = cnn_model.get_tensor(out_index)[0]
                limite = 0.96
                ## ..
                
                ## modelo velho
                # x = cnn_model.predict_classes(img)
                # if(x[0][0] == 0):
                #     ans = "Gato"
                # elif(x[0][0] == 1):
                #     ans = "Cachorro"
                # else:
                #     ans = "Não foi possível reconhecer"
                # return Response({"prediction":ans}, status.HTTP_200_OK)
                ## ..
                if x[0] > limite and x[0] > x[1]:
                    ans = "Gato"
                    percent = x[0]
                elif x[1] > limite and x[1] > x[0]:
                    ans = "Cachorro"
                    percent = x[1]
                else:
                    ans = "Não foi possível reconhcer"
                    percent = 0
                
                return Response({"prediction":ans, "percent_cat":x[0], "percent_dog":x[1]}, status.HTTP_200_OK)
                
            except Exception as message:
                return Response({'message': 'Certifique-se que enviou uam imagem'}, status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class ImageSave(APIView):
    parser_classes = (MultiPartParser, FormParser,)
    serializer_class = ImageSerializer
    
    def upload_image_cloudinary(self, request, image_name):
        cloudinary.uploader.upload(
            request.FILES['imageFile'],
            public_id=image_name
        )
        
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                imageName = "path/images/"+request.FILES['imageFile'].name.split('.')[0]+str(randint(0, 1000))
                self.upload_image_cloudinary(request, imageName)
                print(imageName)
                serializer.save(image=imageName)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as message:
                return Response({'message': 'Certifique-se que enviou uam imagem'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ImageDetail(APIView):
    serializer_class = ImageSerializer
    
    def get(self, request, id, format=None):
        images = [Image.objects.get(id=id)]
        serializer = self.serializer_class(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, id, format=None):
        try:
            image = Image.objects.get(id=id)
            image.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as message:
            return Response(status=status.HTTP_404_NOT_FOUND)

