import os

from dotenv import load_dotenv
from kafka import KafkaProducer


load_dotenv()


def create_producer():
    return KafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    )


def send_image(producer, s3_image):
    producer.send(os.getenv("KAFKA_TOPIC"), value=s3_image.encode("utf-8"))
    producer.flush()
    producer.close()
    return {"msg": f"Success to Send S3 image URL {s3_image.encode('utf-8')}"}
