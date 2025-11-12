
from ultralytics import YOLO

model = YOLO('models/best.pt')

results = model.predict('input_videos/08fd33_4.mp4', save=True)
print(results[0])
print('============================================')
for box in results[0].boxes:
    print(box)



#from ultralytics import YOLO

#model = YOLO('yolov8x.pt')  # or 'yolov8n.pt' for faster testing

# Run prediction in streaming mode
#results_generator = model.predict(
   # source='input_videos\clfinaledit.mp4',
    #stream=True,  # stream mode lets you loop through frame results
    #save=True     # optionally save the output video
#)

# Limit to 600 frames
#for i, result in enumerate(results_generator):
  #  if i >= 600:
   #     break
   # print(f"Frame {i} - {len(result.boxes)} objects detected")
   # for box in result.boxes:
    #    print(box)
