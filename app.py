from flask import Flask,render_template,Response
import cv2
import numpy as np
import time
import module_pose as pm
import speak

app=Flask(__name__)
camera=cv2.VideoCapture(0)
detector =pm.poseDetector()
pTime = 0
count = 0
dir  = 0


def generate_frames():
    global count
    global dir 
    global pTime

    while True:
        
            
        ## read the camera frame
        success,frame=camera.read()
        if not success:
            break
        else:
            frame = detector.getPose(frame, False)
            pose_list = detector.getlandmark(frame , False)
            try :
                
                angle =  detector.find_angle( frame,  11 , 13 , 15)
                # print(angle)
                per = np.interp(angle, (30,150) , (0 , 100))
                # print(per)
                 # Right Arm
                detector.find_angle(frame ,  12 , 14 , 16)
                

                if per == 100:
                    if dir == 0 :
                        count +=0.5
                        dir = 1
                if per == 0 :
                    if dir == 1 :
                        count += 0.5
                        dir = 0
                print(count)      
                cv2.rectangle(frame ,  (0 , 500) , (200, 400) , (255,255 , 0) , cv2.FILLED)
                cv2.putText(frame  , str(int(count)) , (65, 480) , cv2.FONT_HERSHEY_PLAIN, 7,(255, 0,255 ) , 5 )
            except IndexError :
                print("Not found")  


            cTime = time.time()
            fps = 1/(cTime-pTime)
            pTime = cTime
            cv2.putText(frame, str(int(fps)) , (70, 50) , cv2.FONT_HERSHEY_PLAIN , 3 , (255, 0, 255) , 3)


            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    app.run(debug=True)