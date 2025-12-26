import logging
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class ImageAnalyzer:
    def extract_exif_data(self, image_path: str) -> Dict[str, Any]:
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS
            
            with Image.open(image_path) as image:
                exif_data = {}
                gps_data = {}
                
                if hasattr(image, '_getexif') and image._getexif():
                    exif = image._getexif()
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        
                        if tag == 'GPSInfo':
                            for gps_tag_id, gps_value in value.items():
                                gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                                gps_data[gps_tag] = str(gps_value)
                        else:
                            try:
                                exif_data[tag] = str(value)
                            except:
                                exif_data[tag] = "Unable to decode"
                
                with open(image_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                
                result = {
                    'filename': os.path.basename(image_path),
                    'format': image.format,
                    'mode': image.mode,
                    'size': image.size,
                    'width': image.width,
                    'height': image.height,
                    'file_size': os.path.getsize(image_path),
                    'sha256': file_hash,
                    'exif': exif_data,
                    'gps': gps_data if gps_data else None,
                    'timestamp': datetime.now().isoformat()
                }
                
                if gps_data:
                    coords = self._parse_gps_coordinates(gps_data)
                    if coords:
                        result['coordinates'] = coords
                
                return result
                
        except ImportError:
            return {'error': 'Pillow not installed'}
        except Exception as e:
            logger.error(f"EXIF extraction error: {e}")
            return {'error': str(e)}
    
    def _parse_gps_coordinates(self, gps_data: Dict) -> Optional[Dict[str, float]]:
        try:
            def convert_to_degrees(value):
                d, m, s = value
                return float(d) + float(m)/60 + float(s)/3600
            
            lat = gps_data.get('GPSLatitude')
            lat_ref = gps_data.get('GPSLatitudeRef')
            lon = gps_data.get('GPSLongitude')
            lon_ref = gps_data.get('GPSLongitudeRef')
            
            if lat and lon and lat_ref and lon_ref:
                latitude = convert_to_degrees(eval(lat))
                longitude = convert_to_degrees(eval(lon))
                
                if lat_ref == 'S':
                    latitude = -latitude
                if lon_ref == 'W':
                    longitude = -longitude
                
                return {
                    'latitude': latitude,
                    'longitude': longitude
                }
        except:
            pass
        return None
    
    def calculate_hash(self, image_path: str) -> Dict[str, str]:
        try:
            import hashlib
            
            with open(image_path, 'rb') as f:
                content = f.read()
                
            return {
                'md5': hashlib.md5(content).hexdigest(),
                'sha1': hashlib.sha1(content).hexdigest(),
                'sha256': hashlib.sha256(content).hexdigest(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_image_content(self, image_path: str) -> Dict[str, Any]:
        try:
            from PIL import Image
            import colorsys
            from collections import Counter
            
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                small_img = img.resize((100, 100))
                pixels = list(small_img.getdata())
                
                color_counts = Counter(pixels)
                dominant_colors = color_counts.most_common(5)
                
                r_avg = sum(p[0] for p in pixels) / len(pixels)
                g_avg = sum(p[1] for p in pixels) / len(pixels)
                b_avg = sum(p[2] for p in pixels) / len(pixels)
                
                brightness = (r_avg + g_avg + b_avg) / 3 / 255
                
                return {
                    'dimensions': img.size,
                    'aspect_ratio': round(img.width / img.height, 2),
                    'dominant_colors': [
                        {'color': f'#{c[0]:02x}{c[1]:02x}{c[2]:02x}', 'count': cnt}
                        for c, cnt in dominant_colors
                    ],
                    'average_color': f'#{int(r_avg):02x}{int(g_avg):02x}{int(b_avg):02x}',
                    'brightness': round(brightness, 2),
                    'is_dark': brightness < 0.5,
                    'timestamp': datetime.now().isoformat()
                }
        except ImportError:
            return {'error': 'Pillow not installed'}
        except Exception as e:
            return {'error': str(e)}
    
    def detect_faces(self, image_path: str) -> Dict[str, Any]:
        try:
            import cv2
            
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)
            
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            face_data = []
            for (x, y, w, h) in faces:
                face_data.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h)
                })
            
            return {
                'faces_detected': len(faces),
                'faces': face_data,
                'timestamp': datetime.now().isoformat()
            }
        except ImportError:
            return {'error': 'OpenCV not installed', 'faces_detected': 0}
        except Exception as e:
            return {'error': str(e), 'faces_detected': 0}

image_analyzer = ImageAnalyzer()
