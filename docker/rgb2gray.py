from is_wire.core import Channel, Subscription, Message, Tracer, AsyncTransport
from opencensus.ext.zipkin.trace_exporter import ZipkinExporter
from is_msgs.image_pb2 import Image
import numpy as np
import cv2
import time
from streamChannel import StreamChannel

def to_np(input_image):
    if isinstance(input_image, np.ndarray):
        return input_image
    if isinstance(input_image, Image):
        buffer = np.frombuffer(input_image.data, dtype=np.uint8)
        return cv2.imdecode(buffer, flags=cv2.IMREAD_COLOR)
    return np.array([], dtype=np.uint8)

def to_image(input_image, encode_format='.jpeg', compression_level=0.8):
    if isinstance(input_image, np.ndarray):
        params = [
            cv2.IMWRITE_JPEG_QUALITY, int(compression_level * 100)
        ] if encode_format == '.jpeg' else [
            cv2.IMWRITE_PNG_COMPRESSION, int(compression_level * 9)
        ]
        cimage = cv2.imencode(ext=encode_format, img=input_image, params=params)
        return Image(data=cimage[1].tobytes())
    if isinstance(input_image, Image):
        return input_image
    return Image()

exporters = [
    ZipkinExporter(
        service_name=f"Cam{i} to Gray",
        host_name="10.10.0.68",
        port=30200,
        transport=AsyncTransport,
    ) for i in range(1, 5)
]

def process_image(channel, exporter, cam_id, qtd, start_time):
    msg = channel.consume_last()
    if isinstance(msg, bool):
        return qtd, start_time
    tracer = Tracer(exporter, span_context=msg.extract_tracing())
    with tracer.span(name="GrayProcess") as span:
        gray_start = time.time()
        im = msg.unpack(Image)
        frame = to_np(im)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img_gray = to_image(gray)
        qtd += 1
        elapsed_time = time.time() - gray_start
        total_time = time.time() - start_time
        span.add_attribute("Tempo de Processamento (ms)", elapsed_time)
        if total_time >= 1:
            span.add_attribute("FPS", qtd)
            start_time = time.time()
            qtd = 0
        message = Message()
        message.pack(img_gray)
        message.inject_tracing(span)
        channel.publish(message, topic=f"GrayCam.{cam_id}")
    return qtd, start_time

if __name__ == '__main__':
    print('---RUNNING EXAMPLE DEMO OF THE CAMERA CLIENT---')

    broker_uri = "amqp://10.10.0.68:30000"
    channels = [StreamChannel(broker_uri) for _ in range(4)]
    subscriptions = [
        Subscription(channel=channels[i]).subscribe(topic=f'CameraGateway.{i+1}.Frame')
        for i in range(4)
    ]

    qtds = [0] * 4
    start_time = time.time()

    while True:
        for i in range(4):
            qtds[i], start_time = process_image(channels[i], exporters[i], i+1, qtds[i], start_time)