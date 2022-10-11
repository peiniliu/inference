import tensorflow as tf
import numpy
import json
from locust import HttpUser, task, constant, events
from PIL import Image
import io

class ImgClssificationUser(HttpUser):
    wait_time = constant(1)

    headers = {"content-type": "application/json"}

    # IMAGE_URL = 'https://tensorflow.org/images/blogs/serving/cat.jpg'
    # # Download the image since we weren't given one
    # dl_request = requests.get(IMAGE_URL, stream=True)
    # dl_request.raise_for_status()
    # data = dl_request.content
    # inputs = Image.open(io.BytesIO(dl_request.content))
    #with open('/mnt/locust/cat_224x224.jpeg', 'rb') as f:
    with open('locust/cat_224x224.jpeg', 'rb') as f:
           image = f.read()
    inputs = Image.open(io.BytesIO(image))
    inputs = numpy.array(inputs).tolist()
    # inputs = numpy.array(inputs)
    # inputs = numpy.expand_dims(inputs, 0)
    # data = json.dumps({"signature_name": "serving_default", "instances": inputs.tolist()})    
    
    @task
    def predict(self):
        # print(f"batchsize={self.environment.parsed_options.batchsize}")
        images = []
        for x in range(self.environment.parsed_options.batchsize):
            # print(x)
            images.append(self.inputs)
            # print(len(images))
        data = json.dumps({"signature_name": "serving_default", "instances": images})
        r = self.client.post("/v1/models/resnet:predict", data=data, headers=self.headers)


@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--batchsize", type=int, env_var="BATCH_SIZE", default="1", help="number of image/per request")