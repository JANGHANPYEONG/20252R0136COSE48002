import json
import logging
import os
import pprint

from dotenv import load_dotenv

from kafka import KafkaConsumer

from opencv_utils import *


load_dotenv()


# Create a KafkaConsumer instance
def process_messages(s3_conn, consumer):
    print("Success to Connect KafkaConsumer!")
    try:
        for message in consumer:

            print(f"Received message: {message.value.decode('utf-8')}")
            try:
                # 메시지의 value 부분을 JSON으로 디코딩
                json_message = message.value.decode('utf-8')
                data = json.loads(json_message)
                
                # JSON 데이터에서 필요한 정보 추출
                image_url = data.get("image_url")
                meat_id = data.get("meat_id")
                seqno = data.get("seqno")
                
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
                
                # Manually commit the offset after successful processing
                consumer.commit()
                print(f"Success to create OpenCV Info")
            except Exception as e:
                print(f"Error processing message: {e}")
    finally:
        consumer.close()


def create_consumer():
    return KafkaConsumer(
        os.getenv("KAFKA_TOPIC"),
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        group_id=os.getenv("KAFKA_CONSUMER_GROUP"),
    )


def async_process_image(consumer):
    texture = process_messages(consumer)
    pprint.pprint(texture)
