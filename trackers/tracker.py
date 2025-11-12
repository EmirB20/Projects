from ultralytics import YOLO
import supervision as sv
import pickle
import os
import numpy as np
import cv2
import sys
sys.path.append('../')
from video_helpers import get_center_of_bbox, get_bbox_width


class Tracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()


    def detect_frames(self, frames):
       batch_size = 20
       detections = []
       for i in range(0, len(frames), batch_size):
           detections_batch = self.model.predict(frames[i:i+batch_size], conf=0.1) # statistics are currently not being tracked for the goalkeeper
           # in the model the goalkeeper gets mostly read as a player which is fine. Can use .predict instead of .track to override goalkeeper tag as a player tag
           detections += detections_batch
           #break for testing
       return detections


    def get_object_tracks(self, frames, read_from_stub=False, stub_path = None):
        
         

        detections = self.detect_frames(frames)

        tracks={
            "players":[], # {0:{"bound_box":[0,0,0,0]} <--- one frame
            "referees":[],
            "ball":[]

        }

        for frame_num, detection in enumerate(detections): # loops over frame one by one # enumarate just puts the index of the list
            cls_names = detection.names
            cls_names_inv = {v:k for k,v in cls_names.items()} #k,v key,value
            # print(cls_names)
            # Convert the detections to supervision Detection format

            detection_supervision = sv.Detections.from_ultralytics(detection)

            # Convert Goalkeeper to player object
            for object_ind , class_id in enumerate(detection_supervision.class_id):
                if cls_names[class_id] == "goalkeeper":
                    detection_supervision.class_id[object_ind] = cls_names_inv["player"]

            # Track Objects
            detection_with_tracks = self.tracker.update_with_detections(detection_supervision)

            tracks["players"].append({})
            tracks["referees"].append({})
            tracks["ball"].append({})


            for frame_detection in detection_with_tracks:
                bound_box = frame_detection[0].tolist()
                cls_id = frame_detection[3]
                track_id = frame_detection[4]

                if cls_id == cls_names_inv['player']:
                    tracks["players"][frame_num][track_id] = {"bound_box":bound_box}

                if cls_id == cls_names_inv['referee']:
                    tracks["referees"][frame_num][track_id] = {"bound_box":bound_box}

            for frame_detection in detection_supervision:
                bound_box = frame_detection[0].tolist()
                cls_id = frame_detection[3]

                if cls_id == cls_names_inv['ball']:
                    tracks["ball"][frame_num][1] = {"bound_box":bound_box}

        if stub_path is not None:
            with open(stub_path, 'wb') as f:
                pickle.dump(tracks, f)

        return tracks       
            
            #print(detection_supervision)

            #break (just for testing)

    def draw_ellipse(self, frame, bound_box,color, track_id=None):
        y2 = int(bound_box[3])

        x_center, _ = get_center_of_bbox(bound_box)
        width = get_bbox_width(bound_box)

        cv2.ellipse(
            frame,
            center=(x_center, y2),
            axes=(int(width), int(0.35 * width)),
            angle=0.0,
            startAngle=-45,
            endAngle=255,
            color=color,
            thickness=2,
            lineType=cv2.LINE_4
        )
        
        rectangle_width = 40
        rectangle_height = 20
        x1_rect = x_center - rectangle_width // 2
        x2_rect = x_center + rectangle_width // 2
        y1_rect = (y2 - rectangle_height//2) + 15
        y2_rect = (y2 + rectangle_height//2) + 15

        if track_id is not None:

            cv2.rectangle(frame,
                (int(x1_rect), int(y1_rect)),
                (int(x2_rect), int(y2_rect)),
                color,
                cv2.FILLED)
            
            x1_text = x1_rect + 12
            if track_id > 99:
                x1_text -= 10

            cv2.putText(
                frame,
                f"{track_id}",
                (int(x1_text), int(y1_rect + 15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                2
                
            )


        return frame

    def draw_triangle(self, frame, bound_box, color)   :
        y = int(bound_box[1])
        x,_ = get_center_of_bbox(bound_box) 

        triangle_points = np.array([
            [x,y],
            [x-10,y-20],
            [x+10,y-20]
        ])
        cv2.drawContours(frame, [triangle_points],0,color, cv2.FILLED)
        cv2.drawContours(frame, [triangle_points],0,(0,0,0), 2)

        return frame

    def draw_annotations(self, video_frames, tracks):
        output_video_frames = []

        for frame_num, frame in enumerate(video_frames):
            frame = frame.copy() # so we do not pollute the video frames that are coming in (so the original list is not drawn on)

            player_dict = tracks["players"][frame_num]
            ball_dict = tracks["ball"][frame_num]
            referee_dict = tracks["referees"][frame_num]

            # Draw Players

            for track_id, player in player_dict.items():
                frame = self.draw_ellipse(frame, player["bound_box"], (0,0,255), track_id)

            
             # Draw Referees

            for _, referee in referee_dict.items():
                frame = self.draw_ellipse(frame, referee["bound_box"], (0,255,255), track_id = None)


            # Draw ball

            for track_id, ball in ball_dict.items():
                frame = self.draw_triangle(frame, ball["bound_box"], (0,255,0))

            output_video_frames.append(frame)

        return output_video_frames

