from rknnlite.api import RKNNLite


class RKNN_model_container():
    def __init__(self, model_path, target=None, device_id=None) -> None:
        rknn = RKNNLite()

        rknn.load_rknn(model_path)

        print('--> Init runtime environment')
        ret = rknn.init_runtime()
        if ret != 0:
            print('Init runtime environment failed')
            exit(ret)
        print('done')

        self.rknn = rknn

    def run(self, inputs):
        if isinstance(inputs, list) or isinstance(inputs, tuple):
            pass
        else:
            inputs = [inputs]
        print(f"inputs: {inputs}")

        result = self.rknn.inference(inputs=inputs)

        return result


print("main run")
