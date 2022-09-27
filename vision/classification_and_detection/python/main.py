"""
mlperf inference benchmarking tool
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import array
import collections
import json
import logging
import os
import sys
import threading
import time
from queue import Queue

import mlperf_loadgen as lg
import numpy as np

import dataset
import imagenet
import imagenetPicture
import coco

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")

NANO_SEC = 1e9
MILLI_SEC = 1000

# pylint: disable=missing-docstring

# the datasets we support
SUPPORTED_DATASETS = {
    "imagenet":
        (imagenet.Imagenet, dataset.pre_process_vgg, dataset.PostProcessCommon(offset=-1),
         {"image_size": [224, 224, 3]}),
    "imagenet_tfserving":
        (imagenetPicture.Imagenet, dataset.pre_process_tfserving, dataset.PostProcessRestful(offset=-1),
         {"image_size": [224, 224, 3]}),
    "imagenet_seldon":
        (imagenet.Imagenet, dataset.pre_process_no, dataset.PostProcessSeldon(offset=-1),
         {"image_size": [224, 224, 3]}),
    "imagenet_seldon_preprocessed":
        (imagenet.Imagenet, dataset.pre_process_resnet, dataset.PostProcessSeldon(offset=-1),
         {"image_size": [224, 224, 3]}),
    "imagenet_tflocal":
        (imagenet.Imagenet, dataset.pre_process_resnet, dataset.PostProcessSeldon(offset=-1),
         {"image_size": [224, 224, 3]}),
    "imagenet_mobilenet":
        (imagenet.Imagenet, dataset.pre_process_mobilenet, dataset.PostProcessArgMax(offset=-1),
         {"image_size": [224, 224, 3]}),
    "coco-300":
        (coco.Coco, dataset.pre_process_coco_mobilenet, coco.PostProcessCoco(),
         {"image_size": [300, 300, 3]}),
    "coco-300-pt":
        (coco.Coco, dataset.pre_process_coco_pt_mobilenet, coco.PostProcessCocoPt(False,0.3),
         {"image_size": [300, 300, 3]}),         
    "coco-1200":
        (coco.Coco, dataset.pre_process_coco_resnet34, coco.PostProcessCoco(),
         {"image_size": [1200, 1200, 3]}),
    "coco-1200-onnx":
        (coco.Coco, dataset.pre_process_coco_resnet34, coco.PostProcessCocoOnnx(),
         {"image_size": [1200, 1200, 3]}),
    "coco-1200-pt":
        (coco.Coco, dataset.pre_process_coco_resnet34, coco.PostProcessCocoPt(True,0.05),
         {"image_size": [1200, 1200, 3],"use_label_map": True}),
    "coco-1200-tf":
        (coco.Coco, dataset.pre_process_coco_resnet34, coco.PostProcessCocoTf(),
         {"image_size": [1200, 1200, 3],"use_label_map": False}),
}

# pre-defined command line options so simplify things. They are used as defaults and can be
# overwritten from command line

SUPPORTED_PROFILES = {
    "defaults": {
        "dataset": "imagenet",
        "backend": "tensorflow",
        "cache": 0,
        "max-batchsize": 32,
    },

    # resnet
    "resnet50-tf": {
        "inputs": "input_tensor:0",
        "outputs": "ArgMax:0",
        "dataset": "imagenet",
        "backend": "tensorflow",
        "model-name": "resnet50",
    },
    "resnet50-onnxruntime": {
        "dataset": "imagenet",
        "outputs": "ArgMax:0",
        "backend": "onnxruntime",
        "model-name": "resnet50",
    },
    "resnet50-tfserving": {
        "dataset": "imagenet_tfserving",
        "backend": "tfserving",
#        "server": "localhost:8500",
        "server": "172.30.0.50:31930",
        "model-name": "resnet50",
    },
    "resnet50-seldon": {
        "dataset": "imagenet_seldon",
        "backend": "seldon",
        "server": "10.108.184.226:15101",
        "namespace": "resnet-tf-single",
        "deployment_name": "image",
        "model-name": "resnet50",
    },
    "resnet50-tflocal": {
        "inputs": "input_tensor:0",
        "outputs": "predictions/Softmax:0",
        "dataset": "imagenet_tflocal",
        "backend": "tflocal",
        "model-name": "resnet50",
    },

    # mobilenet
    "mobilenet-tf": {
        "inputs": "input:0",
        "outputs": "MobilenetV1/Predictions/Reshape_1:0",
        "dataset": "imagenet_mobilenet",
        "backend": "tensorflow",
        "model-name": "mobilenet",
    },
    "mobilenet-onnxruntime": {
        "dataset": "imagenet_mobilenet",
        "outputs": "MobilenetV1/Predictions/Reshape_1:0",
        "backend": "onnxruntime",
        "model-name": "mobilenet",
    },

    # ssd-mobilenet
    "ssd-mobilenet-tf": {
        "inputs": "image_tensor:0",
        "outputs": "num_detections:0,detection_boxes:0,detection_scores:0,detection_classes:0",
        "dataset": "coco-300",
        "backend": "tensorflow",
        "model-name": "ssd-mobilenet",
    },
    "ssd-mobilenet-pytorch": {
        "inputs": "image",
        "outputs": "bboxes,labels,scores",
        "dataset": "coco-300-pt",
        "backend": "pytorch-native",
        "model-name": "ssd-mobilenet",
    },
    "ssd-mobilenet-onnxruntime": {
        "dataset": "coco-300",
        "outputs": "num_detections:0,detection_boxes:0,detection_scores:0,detection_classes:0",
        "backend": "onnxruntime",
        "data-format": "NHWC",
        "model-name": "ssd-mobilenet",
    },

    # ssd-resnet34
    "ssd-resnet34-tf": {
        "inputs": "image:0",
        "outputs": "detection_bboxes:0,detection_classes:0,detection_scores:0",
        "dataset": "coco-1200-tf",
        "backend": "tensorflow",
        "data-format": "NCHW",
        "model-name": "ssd-resnet34",
    },
    "ssd-resnet34-pytorch": {
        "inputs": "image",
        "outputs": "bboxes,labels,scores",
        "dataset": "coco-1200-pt",
        "backend": "pytorch-native",
        "model-name": "ssd-resnet34",
    },
    "ssd-resnet34-onnxruntime": {
        "dataset": "coco-1200-onnx",
        "inputs": "image",
        "outputs": "bboxes,labels,scores",
        "backend": "onnxruntime",
        "data-format": "NCHW",
        "max-batchsize": 1,
        "model-name": "ssd-resnet34",
    },
    "ssd-resnet34-onnxruntime-tf": {
        "dataset": "coco-1200-tf",
        "inputs": "image:0",
        "outputs": "detection_bboxes:0,detection_classes:0,detection_scores:0",
        "backend": "onnxruntime",
        "data-format": "NHWC",
        "model-name": "ssd-resnet34",
    },

}

SCENARIO_MAP = {
    "SingleStream": lg.TestScenario.SingleStream,
    "MultiStream": lg.TestScenario.MultiStream,
    "Server": lg.TestScenario.Server,
    "Offline": lg.TestScenario.Offline,
}

last_timeing = []


def get_args():
    """Parse commandline."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=SUPPORTED_DATASETS.keys(), help="dataset")
    parser.add_argument("--dataset-path", required=True, help="path to the dataset")
    parser.add_argument("--dataset-list", help="path to the dataset list")
    parser.add_argument("--data-format", choices=["NCHW", "NHWC"], help="data format")
    parser.add_argument("--profile", choices=SUPPORTED_PROFILES.keys(), help="standard profiles")
    parser.add_argument("--scenario", default="SingleStream",
                        help="mlperf benchmark scenario, one of " + str(list(SCENARIO_MAP.keys())))
    parser.add_argument("--max-batchsize", type=int, help="max batch size in a single inference")
    parser.add_argument("--model", help="model file")
    parser.add_argument("--output", help="test results")
    parser.add_argument("--inputs", help="model inputs")
    parser.add_argument("--outputs", help="model outputs")
    parser.add_argument("--preprocess", type=int, default=0, help="preprocess step , 0 normal, 1 only preprocess, 2 predict with preprocess")
    parser.add_argument("--backend", help="runtime to use")
    # server for tfserving service
    parser.add_argument("--server", default="localhost:8500",help="serving service- host:port")
    # server for seldon deployment
    parser.add_argument("--namespace", default="resnet-tf-single",help="seldon deployment model namespace")
    parser.add_argument("--deployment_name", default="image",help="seldon deployment name")
    parser.add_argument("--model-name", help="name of the mlperf model, ie. resnet50")
    parser.add_argument("--threads", default=os.cpu_count(), type=int, help="threads")
    parser.add_argument("--qps", type=int, help="target qps")
    parser.add_argument("--cache", type=int, default=0, help="use cache")
    parser.add_argument("--cache_dir", type=str, default=None, help="preprocessed cache dir")
    parser.add_argument("--accuracy", action="store_true", help="enable accuracy pass")
    parser.add_argument("--find-peak-performance", action="store_true", help="enable finding peak performance pass")

    # file to use mlperf rules compliant parameters
    parser.add_argument("--mlperf_conf", default="../../mlperf.conf", help="mlperf rules config")
    # file for user LoadGen settings such as target QPS
    parser.add_argument("--user_conf", default="user.conf", help="user config for user LoadGen settings such as target QPS")

    # below will override mlperf rules compliant settings - don't use for official submission
    parser.add_argument("--time", type=int, help="time to scan in seconds")
    parser.add_argument("--count", type=int, help="dataset items to use")
    parser.add_argument("--max-latency", type=float, help="mlperf max latency in pct tile")
    parser.add_argument("--samples-per-query", type=int, help="mlperf multi-stream sample per query")
    args = parser.parse_args()

    # don't use defaults in argparser. Instead we default to a dict, override that with a profile
    # and take this as default unless command line give
    defaults = SUPPORTED_PROFILES["defaults"]

    if args.profile:
        profile = SUPPORTED_PROFILES[args.profile]
        defaults.update(profile)
    for k, v in defaults.items():
        kc = k.replace("-", "_")
        if getattr(args, kc) is None:
            setattr(args, kc, v)
    if args.inputs:
        args.inputs = args.inputs.split(",")
    if args.outputs:
        args.outputs = args.outputs.split(",")

    if args.scenario not in SCENARIO_MAP:
        parser.error("valid scanarios:" + str(list(SCENARIO_MAP.keys())))
    return args


def get_backend(backend):
    if backend == "tensorflow":
        from backend_tf import BackendTensorflow
        backend = BackendTensorflow()
    elif backend == "onnxruntime":
        from backend_onnxruntime import BackendOnnxruntime
        backend = BackendOnnxruntime()
    elif backend == "null":
        from backend_null import BackendNull
        backend = BackendNull()
    elif backend == "pytorch":
        from backend_pytorch import BackendPytorch
        backend = BackendPytorch()
    elif backend == "pytorch-native":
        from backend_pytorch_native import BackendPytorchNative
        backend = BackendPytorchNative()      
    elif backend == "tflite":
        from backend_tflite import BackendTflite
        backend = BackendTflite()
    elif backend == "tfserving":
        from backend_tfserving import BackendTfserving
        backend = BackendTfserving()
    elif backend == "seldon":
        from backend_seldon import BackendSeldon
        backend = BackendSeldon()
    elif backend == "tflocal":
        from backend_tflocal import Backendtflocal
        backend = Backendtflocal()
    else:
        raise ValueError("unknown backend: " + backend)
    return backend


class Item:
    """An item that we queue for processing by the thread pool."""

    def __init__(self, query_id, content_id, img, label=None):
        self.query_id = query_id
        self.content_id = content_id
        self.img = img
        self.label = label
        self.start = time.time()


class RunnerBase:
    def __init__(self, model, ds, threads, post_proc=None, max_batchsize=128):
        self.take_accuracy = False
        self.ds = ds
        self.model = model
        self.post_process = post_proc
        self.threads = threads
        self.take_accuracy = False
        self.max_batchsize = max_batchsize
        self.result_timing = []

    def handle_tasks(self, tasks_queue):
        pass

    def start_run(self, result_dict, take_accuracy):
        self.result_dict = result_dict
        self.result_timing = []
        self.take_accuracy = take_accuracy
        self.post_process.start()

    def run_one_item(self, qitem):
        # run the prediction
        processed_results = []
        #log.info("PEINI: run prediction qitem: img={}, label={}, content_id={}, query_id={}".format(None, qitem.label, qitem.content_id, qitem.query_id))
        #log.info("PEINI: run prediction qitem: img={}, label={}, content_id={}, query_id={}".format(qitem.img, None, None, None))
        #log.info("PEINI: run prediction qitem: img={}, label={}, content_id={}, query_id={}".format(qitem.img, qitem.label, qitem.content_id, qitem.query_id))
        try:
            if self.model.name() == "tfserving":
                #log.info("Call tfserving predict")
                results = self.model.predict(qitem.img)
                #log.info(results)
                #"predict list"
                processed_results = self.post_process(results, qitem.content_id, qitem.label, self.result_dict)
                log.info(processed_results)
            elif self.model.name() == "seldon":
                log.info("Call seldon predict")
                results = self.model.predict(qitem.img)
                #log.info(results)
                #log.info(qitem.content_id)
                #"predict list"
                processed_results = self.post_process(results, qitem.content_id, qitem.label, self.result_dict)
                log.info(processed_results)
            elif self.model.name() == "tflocal":
                log.info("Call tensorflow local batch inference")
                results = self.model.predict(qitem.img)
                #log.info(results)
                #"predict list"
                processed_results = self.post_process(results, qitem.content_id, qitem.label, self.result_dict)
                log.info(processed_results)
                #raise ValueError("stop here")
            else:
                results = self.model.predict({self.model.inputs[0]: qitem.img})
                #print(results)
                #[array([ 74, 952, 250, 333,  38, 595, 803, 568, 312, 158, 375, 670, 668,493, 854, 123, 214, 186, 583, 424, 326, 952, 510, 123, 920, 393, 532, 794, 901, 349, 285, 157])]
                processed_results = self.post_process(results, qitem.content_id, qitem.label, self.result_dict)
                #print("processed_results")
                print(processed_results)

            if self.take_accuracy:
                self.post_process.add_results(processed_results)
                self.result_timing.append(time.time() - qitem.start)
        except Exception as ex:  # pylint: disable=broad-except
            src = [self.ds.get_item_loc(i) for i in qitem.content_id]
            log.error("thread: failed on contentid=%s, %s", src, ex)
            # since post_process will not run, fake empty responses
            processed_results = [[]] * len(qitem.query_id)
        finally:
            response_array_refs = []
            response = []
            for idx, query_id in enumerate(qitem.query_id):
                response_array = array.array("B", np.array(processed_results[idx], np.float32).tobytes())
                response_array_refs.append(response_array)
                bi = response_array.buffer_info()
                response.append(lg.QuerySampleResponse(query_id, bi[0], bi[1]))
            lg.QuerySamplesComplete(response)

    def enqueue(self, query_samples):
        idx = [q.index for q in query_samples]
        query_id = [q.id for q in query_samples]
        if len(query_samples) < self.max_batchsize:
            data, label = self.ds.get_samples(idx)
            self.run_one_item(Item(query_id, idx, data, label))
        else:
            bs = self.max_batchsize
            for i in range(0, len(idx), bs):
                data, label = self.ds.get_samples(idx[i:i+bs])
                self.run_one_item(Item(query_id[i:i+bs], idx[i:i+bs], data, label))

    def finish(self):
        pass


class QueueRunner(RunnerBase):
    def __init__(self, model, ds, threads, post_proc=None, max_batchsize=128):
        super().__init__(model, ds, threads, post_proc, max_batchsize)
        self.tasks = Queue(maxsize=threads * 4)
        self.workers = []
        self.result_dict = {}

        for _ in range(self.threads):
            worker = threading.Thread(target=self.handle_tasks, args=(self.tasks,))
            worker.daemon = True
            self.workers.append(worker)
            worker.start()

    def handle_tasks(self, tasks_queue):
        """Worker thread."""
        while True:
            qitem = tasks_queue.get()
            if qitem is None:
                # None in the queue indicates the parent want us to exit
                tasks_queue.task_done()
                break
            self.run_one_item(qitem)
            tasks_queue.task_done()

    def enqueue(self, query_samples):
        idx = [q.index for q in query_samples]
        query_id = [q.id for q in query_samples]
        if len(query_samples) < self.max_batchsize:
            data, label = self.ds.get_samples(idx)
            self.tasks.put(Item(query_id, idx, data, label))
        else:
            bs = self.max_batchsize
            for i in range(0, len(idx), bs):
                ie = i + bs
                data, label = self.ds.get_samples(idx[i:ie])
                self.tasks.put(Item(query_id[i:ie], idx[i:ie], data, label))

    def finish(self):
        # exit all threads
        for _ in self.workers:
            self.tasks.put(None)
        for worker in self.workers:
            worker.join()


def add_results(final_results, name, result_dict, result_list, took, show_accuracy=False):
    percentiles = [50., 80., 90., 95., 99., 99.9]
    buckets = np.percentile(result_list, percentiles).tolist()
    buckets_str = ",".join(["{}:{:.4f}".format(p, b) for p, b in zip(percentiles, buckets)])

    if result_dict["total"] == 0:
        result_dict["total"] = len(result_list)

    # this is what we record for each run
    result = {
        "took": took,
        "mean": np.mean(result_list),
        "percentiles": {str(k): v for k, v in zip(percentiles, buckets)},
        "qps": len(result_list) / took,
        "count": len(result_list),
        "good_items": result_dict["good"],
        "total_items": result_dict["total"],
    }
    acc_str = ""
    if show_accuracy:
        result["accuracy"] = 100. * result_dict["good"] / result_dict["total"]
        acc_str = ", acc={:.3f}%".format(result["accuracy"])
        if "mAP" in result_dict:
            result["mAP"] = 100. * result_dict["mAP"]
            acc_str += ", mAP={:.3f}%".format(result["mAP"])

    # add the result to the result dict
    final_results[name] = result

    # to stdout
    print("{} qps={:.2f}, mean={:.4f}, time={:.3f}{}, queries={}, tiles={}".format(
        name, result["qps"], result["mean"], took, acc_str,
        len(result_list), buckets_str))


def main():
  global last_timeing
  args = get_args()

  log.info(args)

  # find backend
  backend = get_backend(args.backend)

  # override image format if given
  image_format = args.data_format if args.data_format else backend.image_format()

  # --count applies to accuracy mode only and can be used to limit the number of images
  # for testing. For perf model we always limit count to 200.
  count_override = False
  count = args.count
  if count:
      count_override = True

  # dataset to use
  #    "imagenet":
  #    (imagenet.Imagenet, dataset.pre_process_vgg, dataset.PostProcessCommon(offset=-1),
  #     {"image_size": [224, 224, 3]}),
  wanted_dataset, pre_proc, post_proc, kwargs = SUPPORTED_DATASETS[args.dataset]
  log.info("PEINI: Load DATASET: datapath={} imagelist={}, name={}, imageformat={}, pre_process={}, use_cache={}, count={}".format(
        args.dataset_path,
        args.dataset_list,
        args.dataset,
        image_format,
        pre_proc,
        args.cache,
        count)
  )
  ds = wanted_dataset(data_path=args.dataset_path,
                      image_list=args.dataset_list,
                      name=args.dataset,
                      image_format=image_format,
                      pre_process=pre_proc,
                      use_cache=args.cache,
                      count=count, cache_dir=args.cache_dir, **kwargs)
  log.info("ds count".format(ds.get_item_count))

  if args.preprocess != 1:
      # load model to backend
      if args.backend == "tfserving":
          log.info("PEINI:  Load TFX: server={} model={}, inputs={}, outputs={}".format(
          args.server,args.model,args.inputs,args.outputs))
          model = backend.load(inputs=args.inputs, outputs=args.outputs, server=args.server)
      elif args.backend == "seldon":
          log.info("PEINI:  Load seldon: server={} model={}, inputs={}, outputs={}".format(
          args.server,args.model,args.inputs,args.outputs))
          model = backend.load(namespace=args.namespace, deployment_name=args.deployment_name, inputs=args.inputs, outputs=args.outputs, server=args.server)
      elif args.backend == "tflocal":
          log.info("PEINI:  Load tf as batch: server={} model={}, inputs={}, outputs={}, preprocess={}".format(
          args.server,args.model,args.inputs,args.outputs, args.preprocess))
          model = backend.load(args.model, inputs=args.inputs, outputs=args.outputs, preprocess=args.preprocess)
      else:
          model = backend.load(args.model, inputs=args.inputs, outputs=args.outputs)

      final_results = {
          "runtime": model.name(),
          "version": model.version(),
          "time": int(time.time()),
          "cmdline": str(args),
      }

      mlperf_conf = os.path.abspath(args.mlperf_conf)
      if not os.path.exists(mlperf_conf):
          log.error("{} not found".format(mlperf_conf))
          sys.exit(1)

      user_conf = os.path.abspath(args.user_conf)
      if not os.path.exists(user_conf):
          log.error("{} not found".format(user_conf))
          sys.exit(1)

      if args.output:
          output_dir = os.path.abspath(args.output)
          os.makedirs(output_dir, exist_ok=True)
          os.chdir(output_dir)

      #
      # make one pass over the dataset to validate accuracy
      #
      count = ds.get_item_count()

      if args.backend == "tfserving" or args.backend == "seldon":
  #       ds.load_query_samples([0])
  #       for _ in range(5):
  #           img, _ = ds.get_samples([0])
  #           #log.info("PEINI: get_sample{}".format(img))
  #           _ = backend.predict(img)
  #       ds.unload_query_samples(None)
         log.info("PEINI: args.backend".format(args.backend))
      elif args.backend == "tflocal":
         ds.load_query_samples([0])
         for _ in range(5):
             img, _ = ds.get_samples([0])
             #log.info("PEINI: get_sample{}".format(img.shape))
             _ = backend.predict(img)
         ds.unload_query_samples(None)
      else:
         # warmup
         ds.load_query_samples([0])
         for _ in range(5):
             img, _ = ds.get_samples([0])
             _ = backend.predict({backend.inputs[0]: img})
         ds.unload_query_samples(None)


      scenario = SCENARIO_MAP[args.scenario]
      runner_map = {
          lg.TestScenario.SingleStream: RunnerBase,
          lg.TestScenario.MultiStream: QueueRunner,
          lg.TestScenario.Server: QueueRunner,
          lg.TestScenario.Offline: QueueRunner
      }
      runner = runner_map[scenario](model, ds, args.threads, post_proc=post_proc, max_batchsize=args.max_batchsize)

      def issue_queries(query_samples):
          runner.enqueue(query_samples)

      def flush_queries():
          pass

      def process_latencies(latencies_ns):
          # called by loadgen to show us the recorded latencies
          global last_timeing
          last_timeing = [t / NANO_SEC for t in latencies_ns]

      settings = lg.TestSettings()
      settings.FromConfig(mlperf_conf, args.model_name, args.scenario)
      settings.FromConfig(user_conf, args.model_name, args.scenario)
      settings.scenario = scenario
      settings.mode = lg.TestMode.PerformanceOnly
      if args.accuracy:
          settings.mode = lg.TestMode.AccuracyOnly
      if args.find_peak_performance:
          settings.mode = lg.TestMode.FindPeakPerformance

      if args.time:
          # override the time we want to run
          settings.min_duration_ms = args.time * MILLI_SEC
          settings.max_duration_ms = args.time * MILLI_SEC

      if args.qps:
          qps = float(args.qps)
          settings.server_target_qps = qps
          settings.offline_expected_qps = qps

      if count_override:
          settings.min_query_count = count
          settings.max_query_count = count

      if args.samples_per_query:
          settings.multi_stream_samples_per_query = args.samples_per_query
      if args.max_latency:
          settings.server_target_latency_ns = int(args.max_latency * NANO_SEC)
          settings.multi_stream_target_latency_ns = int(args.max_latency * NANO_SEC)

      sut = lg.ConstructSUT(issue_queries, flush_queries, process_latencies)
      qsl = lg.ConstructQSL(count, min(count, 500), ds.load_query_samples, ds.unload_query_samples)

      log.info("starting {}".format(scenario))
      result_dict = {"good": 0, "total": 0, "scenario": str(scenario)}
      runner.start_run(result_dict, args.accuracy)
      lg.StartTest(sut, qsl, settings)

      if not last_timeing:
          last_timeing = runner.result_timing
      if args.accuracy:
          post_proc.finalize(result_dict, ds, output_dir=args.output)
      add_results(final_results, "{}".format(scenario),
                  result_dict, last_timeing, time.time() - ds.last_loaded, args.accuracy)

      runner.finish()
      lg.DestroyQSL(qsl)
      lg.DestroySUT(sut)

      #
      # write final results
      #
      if args.output:
          with open("results.json", "w") as f:
              json.dump(final_results, f, sort_keys=True, indent=4)



if __name__ == "__main__":
    main()
