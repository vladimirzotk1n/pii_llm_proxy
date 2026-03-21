import grpc
import numpy as np
import tritonclient.grpc.aio as grpcclient
from transformers import AutoTokenizer
from tritonclient.grpc import service_pb2, service_pb2_grpc
from tritonclient.utils import triton_to_np_dtype

from src.config import get_settings
from src.logger_config import logger

settings = get_settings()
tokenizer = AutoTokenizer.from_pretrained("VladimirFireBall/distilbert")


class InferenceServer:
    def __init__(self) -> None:
        self.url = settings.triton_server_url
        self.triton_client = grpcclient.InferenceServerClient(url=self.url)
        self.channel = grpc.aio.insecure_channel(self.url)
        self.grpc_stub = service_pb2_grpc.GRPCInferenceServiceStub(self.channel)

    async def close(self):
        await self.channel.close()

    async def infer_text(
        self,
        text: str,
        model_name: str = "ner_onnx",
    ) -> dict:

        logger.info("Getting model metadata")
        model_meta = await self.parse_model_metadata(model_name)

        logger.info("Tokenizing text")
        tokenized = tokenizer(
            text,
            truncation=True,
            padding=True,
            return_tensors="np",
        )

        input_ids = tokenized["input_ids"]
        attention_mask = tokenized["attention_mask"]

        tokens = tokenizer.convert_ids_to_tokens(input_ids[0].tolist())

        logger.info("Creating Triton inputs")

        inputs = []

        inputs.append(
            grpcclient.InferInput(
                model_meta.inputs[0].name,
                input_ids.shape,
                model_meta.inputs[0].datatype,
            )
        )

        inputs.append(
            grpcclient.InferInput(
                model_meta.inputs[1].name,
                attention_mask.shape,
                model_meta.inputs[1].datatype,
            )
        )

        inputs[0].set_data_from_numpy(
            input_ids.astype(triton_to_np_dtype(model_meta.inputs[0].datatype))
        )

        inputs[1].set_data_from_numpy(
            attention_mask.astype(triton_to_np_dtype(model_meta.inputs[1].datatype))
        )

        outputs = [grpcclient.InferRequestedOutput(model_meta.outputs[0].name)]

        logger.info("Sending request to Triton")

        results = await self.triton_client.infer(
            model_name=model_name,
            inputs=inputs,
            outputs=outputs,
        )

        logger.info("Got response from triton")
        logits = results.as_numpy(model_meta.outputs[0].name)

        predictions = np.argmax(logits, axis=-1)[0].tolist()

        return {
            "predictions": predictions,
            "tokens": tokens,
        }

    async def parse_model_metadata(self, model_name: str):
        metadata_request = service_pb2.ModelMetadataRequest(name=model_name)
        metadata_response = await self.grpc_stub.ModelMetadata(metadata_request)
        return metadata_response
