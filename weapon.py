import cv2
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import winsound


def send_email(subject, body, to_email, app_password, frame):
    email = 'sankarchandrahasini@gmail.com'  # Your email address
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Convert frame to JPEG format for email attachment
    _, frame_encoded = cv2.imencode('.jpg', frame)
    frame_as_bytes = frame_encoded.tobytes()
    image = MIMEImage(frame_as_bytes)
    msg.attach(image)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()

        try:
            server.login(email, app_password)
            server.sendmail(email, to_email, msg.as_string())
            print(f"Email sent to {to_email} successfully.")
            return True
        
        except smtplib.SMTPException as e:
            print(f"SMTP Exception: {e}")
            return False

def weapon_detection():
    # Load Yolo
    net = cv2.dnn.readNet("yolov3_training_2000.weights", "yolov3_testing.cfg")
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    classes = ["Gun", "Knife"]  # Update with your specific classes

    cap = cv2.VideoCapture(0)  # Using default webcam (index 0)

    Email_Status = False

    while True:
        ret, img = cap.read()
        if not ret:
            break
        height, width, channels = img.shape

        # Detecting objects
        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
        colors = np.random.uniform(0, 255, size=(len(classes), 3))
        outs = net.forward(output_layers)

        # Showing information on the screen
        class_ids = []
        confidences = []
        boxes = []
        weapon_counts = {}  # Dictionary to store counts of each detected weapon type
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    # Object detected
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
                    
                    # Increment count for this class
                    class_name = classes[class_id]
                    weapon_counts[class_name] = weapon_counts.get(class_name, 0) + 1

        if weapon_counts:
            print("Weapons detected:")
            for weapon, count in weapon_counts.items():
                print(f"{weapon}: {count}")

        font = cv2.FONT_HERSHEY_SIMPLEX
        for i in range(len(boxes)):
            x, y, w, h = boxes[i]
            class_id = class_ids[i]
            color = colors[class_id]
            label = classes[class_id]  # Get class name associated with class ID
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, label, (x, y - 5), font, 0.5, color, 2)

        cv2.imshow("Webcam", img)
        
        if weapon_counts and not Email_Status:
            # Email details
            subject = "Weapon Detected!"
            body = "A weapon has been detected. Please take necessary action."
            recipient_email = 'chandrahasinis.csbs2022@citchennai.net'
            app_password = "iyyz zjym xvib cygy"  # App-specific password for your email account
            
            # Send email with frame as attachment
            success = send_email(subject, body, recipient_email, app_password, img)
            if success:
                Email_Status = True
                frequency = 2500
                duration = 1000
                winsound.Beep(frequency, duration)


        key = cv2.waitKey(1)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

# Call the function to run weapon detection
weapon_detection()
