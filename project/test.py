# import cv2
# import platform
#
# src = 0
# if platform.system() == 'Windows':
#     captrue = cv2.VideoCapture(src, cv2.CAP_DSHOW)
#
# else:
#     captrue = cv2.VideoCapture(src)
# captrue.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# captrue.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
# while captrue.isOpened():
#
#     (grabbed, frame) = captrue.read()
#
#     if grabbed:
#         cv2.imshow('Wandlab Camera Window', frame)
#
#         key = cv2.waitKey(1) & 0xFF
#         if (key == 27):
#             break
#
# captrue.release()
# cv2.destroyAllWindows()
import cv2

img = cv2.imread('static/mak_img/10.jpg', cv2.IMREAD_COLOR)
cv2.imshow('image', img)
cv2.waitKey(0)
cv2.destroyAllWindows


@app.route('/result')
def result():
	  # 모델은 불러와져 있으니, 사용자가 올린 데이터를 predict 함수에 넣어주면 됨
		# 이미지이기에, rescale 및 size 조정을 위해 ImageDataGenerator 활용
    test_datagen = ImageDataGenerator(rescale = 1./255)
    test_dir = 'static/'
    test_generator = test_datagen.flow_from_directory(
            test_dir,
            # target_size 는 학습할때 설정했던 사이즈와 일치해야 함
            target_size =(224, 224),
            color_mode ="rgb",
            shuffle = False,
            # test 셋의 경우, 굳이 클래스가 필요하지 않음
            # 학습할때는 꼭 binary 혹은 categorical 로 설정해줘야 함에 유의
            class_mode = None,
            batch_size = 1)
    pred = model.predict(test_generator)
    # 마지막으로 업로드한 사진에 대한 판별결과를 보여줌
    maks = ['albam', 'gyeongju', 'jangsu', 'jipyeong', 'sosungju']
    result = max(pred[-1]) # 최근 사진 중에 확률이 제일 높은 것
    mak_index = list(pred[-1]).index(result) # 최근 사진에서 확률이 제일 높은 것의 index
    mak = maks[mak_index]
    print(mak)
    return render_template('result.html', result=mak)



# from keras.models import load_model
# from PIL import Image, ImageOps
# import numpy as np
# import matplotlib.pyplot as plt
#
# # Load the model
# model = load_model('keras_model.h5')
# model.summary()
#
# # Create the array of the right shape to feed into the keras model
# # The 'length' or number of images you can put into the array is
# # determined by the first position in the shape tuple, in this case 1.
# data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
# # Replace this with the path to your image
# image = Image.open('test/p.jpg')
# #resize the image to a 224x224 with the same strategy as in TM2:
# #resizing the image to be at least 224x224 and then cropping from the center
# size = (224, 224)
# image = ImageOps.fit(image, size, Image.ANTIALIAS)
#
# #turn the image into a numpy array
# image_array = np.asarray(image)
# # Normalize the image
# normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
# # Load the image into the array
# data[0] = normalized_image_array
#
# # run the inference
# prediction = model.predict(data)
# print(prediction)
# plt.imshow(plt.imread('test/p.jpg'))
#
# label = np.array([['보','가위','주먹','없음']])
#
# # test = np.where(prediction[0]>0.8)
#
# print(label.shape)
# print(label[prediction[:]>0.8])
# print(prediction)