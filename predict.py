import os
import torch
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image

class FractureDetector:
    def __init__(self):
        self.model = None
        self.class_names = ['elbow positive', 'fingers positive', 'forearm fracture', 
                           'humerus fracture', 'humerus', 'shoulder fracture', 'wrist positive']
        self.initialize_model()

    def initialize_model(self):
        if os.path.exists('bonefracture_yolov8.pt'):
            self.model = YOLO('bonefracture_yolov8.pt')
        else:
            raise FileNotFoundError("Trained model 'bonefracture_yolov8.pt' not found. Please place it in the project root directory.")
        
    def enhance_image(self, image):
        # Convert to float32
        float_img = image.astype(np.float32) / 255.0
        
        # Apply CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply((float_img * 255).astype(np.uint8))
        
        return enhanced

    def detect_fracture(self, image_path):
        try:
            # Read image
            original_img = cv2.imread(image_path)
            if original_img is None:
                return None, None, None, None, None, "Error: Could not load image"

            # Convert to grayscale
            gray = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)

            # Save grayscale image
            grayscale_path = os.path.join('static', 'processed', 'grayscale_' + os.path.basename(image_path))
            cv2.imwrite(grayscale_path, gray)

            # Thresholded image (Otsu's threshold)
            _, thresh_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            thresholded_path = os.path.join('static', 'processed', 'thresholded_' + os.path.basename(image_path))
            cv2.imwrite(thresholded_path, thresh_img)

            # Binary image (simple binary threshold)
            _, binary_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            binary_path = os.path.join('static', 'processed', 'binary_' + os.path.basename(image_path))
            cv2.imwrite(binary_path, binary_img)

            # Enhance image
            enhanced = self.enhance_image(gray)
            # Create a 3-channel image for YOLO input
            enhanced_3ch = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
            # Run inference with higher confidence threshold
            results = self.model(enhanced_3ch, conf=0.25, iou=0.45)
            # Process results
            result_img = original_img.copy()
            detections = []
            # Get image dimensions
            height, width = result_img.shape[:2]
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    cls = int(box.cls[0].cpu().numpy())
                    conf = float(box.conf[0].cpu().numpy())
                    class_name = self.class_names[cls]
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    area = (x2 - x1) * (y2 - y1)
                    area_percentage = (area / (width * height)) * 100
                    if 0.1 <= area_percentage <= 30:
                        detections.append((x1, y1, x2, y2, conf, class_name))
                        color = (0, 0, 255)
                        if 'elbow' in class_name:
                            color = (255, 0, 0)
                        elif 'fingers' in class_name:
                            color = (0, 255, 0)
                        elif 'forearm' in class_name:
                            color = (255, 165, 0)
                        elif 'humerus' in class_name:
                            color = (128, 0, 128)
                        elif 'shoulder' in class_name:
                            color = (255, 255, 0)
                        elif 'wrist' in class_name:
                            color = (255, 192, 203)
                        cv2.rectangle(result_img, (x1, y1), (x2, y2), color, 2)
                        label = f'{class_name} {conf:.2f}'
                        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                        cv2.rectangle(result_img, (x1, y1-20), (x1+w, y1), color, -1)
                        cv2.putText(result_img, label, (x1, y1-5),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                        center_x = (x1 + x2) // 2
                        center_y = (y1 + y2) // 2
                        cross_size = 10
                        cv2.line(result_img, 
                               (center_x - cross_size, center_y),
                               (center_x + cross_size, center_y),
                               color, 2)
                        cv2.line(result_img,
                               (center_x, center_y - cross_size),
                               (center_x, center_y + cross_size),
                               color, 2)
            # Save the processed image
            output_path = os.path.join('static', 'processed', os.path.basename(image_path))
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cv2.imwrite(output_path, result_img)
            # Prepare result message
            if len(detections) > 0:
                detections.sort(key=lambda x: x[4], reverse=True)
                result = f"Found {len(detections)} detection(s)\n"
                result += "\nDetected fractures:"
                for i, (x1, y1, x2, y2, conf, class_name) in enumerate(detections, 1):
                    region = "upper" if y1 < height/2 else "lower"
                    side = "left" if x1 < width/2 else "right"
                    result += f"\n{i}. {class_name} ({region}-{side} region)"
                    result += f"\n   Confidence: {conf:.2f}"
                result += "\n\nColor Legend:"
                result += "\n- Blue: Elbow fracture"
                result += "\n- Green: Fingers fracture"
                result += "\n- Orange: Forearm fracture"
                result += "\n- Purple: Humerus fracture"
                result += "\n- Yellow: Shoulder fracture"
                result += "\n- Pink: Wrist fracture"
            else:
                result = "No fractures detected in the image"
            return output_path, grayscale_path, thresholded_path, binary_path, result
        except Exception as e:
            print(f"Error in detection: {str(e)}")
            return None, None, None, None, None, f"Error processing image: {str(e)}"

# Initialize the detector as a global variable
detector = None

def process_xray(image_path):
    global detector
    if detector is None:
        detector = FractureDetector()
    return detector.detect_fracture(image_path)