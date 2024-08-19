import json
import pprint
from app import celery
from flask import current_app
from threading import Thread
import os

from opencv_utils import *

# Celery 설정


@celery.task(name="process_image")
def async_process_image(s3_conn, image_url, meat_id, seqno):
    try:        
        object_key = '/'.join(image_url.split('/')[-2:])
        image = s3_conn.download_image(object_key)

        print("Start to create Section Image")
        s3_bucket = "section_images"
        section_object_key = extract_section_image(s3_conn, image, s3_bucket, meat_id, seqno)
                
        if section_object_key:
            section_image = s3_conn.download_image(section_object_key)
            print(f"Success to create Section Image: {section_image}")
                
            print("Start to create Color Palette From Section Image")
            color_palette = final_color_palette_proportion(section_image)
            pprint.pprint(f"Success to create Color Palette: {color_palette}")
                
            print("Start to create Texture Info")
            texture = create_texture_info(section_image)
            pprint.pprint(f"Processed texture: {texture}")
                    
            print("Start to create LBP images")
            lbp_result = lbp_calculate(s3_conn, section_image, meat_id, seqno)
            pprint.pprint(f"Processed LBP Images: {lbp_result}")
                    
            print("Start to create Gabor Filter images")
            gabor_result = gabor_texture_analysis(s3_conn, section_image, meat_id, seqno)
            pprint.pprint(f"Processed Gabor Images: {gabor_result}")
        else:
            raise Exception("Fail to create section image")
        # Here you can save the texture info to a database or send it to another service
    except Exception as e:
        print(f"Fail to Process OpenCV Info")
        raise str(e)