# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import unittest
import tempfile
import paddle
import paddle.inference as paddle_infer
from paddle.fluid.framework import program_guard, Program
import numpy as np

paddle.enable_static()


class UnittestBase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.init_info()

    def tearDwon(self):
        self.temp_dir.cleanup()

    def init_info(self):
        self.shapes = None
        self.save_path = None

    def infer_prog(self):
        config = paddle_infer.Config(self.save_path + '.pdmodel',
                                     self.save_path + '.pdiparams')
        predictor = paddle_infer.create_predictor(config)
        input_names = predictor.get_input_names()
        for i, shape in enumerate(self.shapes):
            input_handle = predictor.get_input_handle(input_names[i])
            fake_input = np.random.randn(*shape).astype("float32")
            input_handle.reshape(shape)
            input_handle.copy_from_cpu(fake_input)
        predictor.run()
        output_names = predictor.get_output_names()
        output_handle = predictor.get_output_handle(output_names[0])
        output_data = output_handle.copy_to_cpu()

        return output_data


class TestDropout(UnittestBase):

    def init_info(self):
        self.shapes = [[10, 10]]
        self.save_path = os.path.join(self.temp_dir.name, 'dropout')

    def test_static(self):
        main_prog = Program()
        starup_prog = Program()
        with program_guard(main_prog, starup_prog):
            fc = paddle.nn.Linear(10, 10)
            x = paddle.randn(self.shapes[0])
            x.stop_gradient = False
            feat = fc(x)
            # p is a Variable
            p = paddle.randn([1])
            out = paddle.nn.functional.dropout(feat, p=p)
            sgd = paddle.optimizer.SGD()
            sgd.minimize(paddle.mean(out))
            # test _to_string
            self.assertTrue("Var[" in str(main_prog))

            exe = paddle.static.Executor()
            exe.run(starup_prog)
            res = exe.run(fetch_list=[x, out])
            # export model
            paddle.static.save_inference_model(self.save_path, [x], [out], exe)

            # Test for Inference Predictor
            infer_out = self.infer_prog()
            self.assertEqual(infer_out.shape, (10, 10))


class TestTileTensorList(UnittestBase):

    def init_info(self):
        self.shapes = [[2, 3, 4]]
        self.save_path = os.path.join(self.temp_dir.name, 'tile_tensors')

    def _test_static(self):
        main_prog = Program()
        starup_prog = Program()
        with program_guard(main_prog, starup_prog):
            fc = paddle.nn.Linear(4, 10)
            x = paddle.randn([2, 3, 4])
            x.stop_gradient = False
            feat = fc(x)
            shape0 = paddle.full([1], 1, dtype='int32')
            shape1 = paddle.full([1], 2, dtype='int32')
            shape = [3, shape1, shape0]
            out = paddle.tile(feat, shape)

            sgd = paddle.optimizer.SGD()
            sgd.minimize(paddle.mean(out))
            self.assertTrue("Vars[" in str(main_prog))

            exe = paddle.static.Executor()
            exe.run(starup_prog)
            res = exe.run(fetch_list=[x, out])
            self.assertEqual(res[1].shape, (6, 6, 10))

            paddle.static.save_inference_model(self.save_path, [x], [out], exe)
            # Test for Inference Predictor
            infer_out = self.infer_prog()
            self.assertEqual(infer_out.shape, (6, 6, 10))


class TestTileTensor(UnittestBase):

    def init_info(self):
        self.shapes = [[2, 3, 4]]
        self.save_path = os.path.join(self.temp_dir.name, 'tile_tensor')

    def _test_static(self):
        main_prog = Program()
        starup_prog = Program()
        with program_guard(main_prog, starup_prog):
            fc = paddle.nn.Linear(4, 10)
            x = paddle.randn([2, 3, 4])
            x.stop_gradient = False
            feat = fc(x)
            # shape is a Variable
            shape = paddle.assign([3, 2, 1])
            out = paddle.tile(feat, shape)

            sgd = paddle.optimizer.SGD()
            sgd.minimize(paddle.mean(out))
            self.assertTrue("Var[" in str(main_prog))

            exe = paddle.static.Executor()
            exe.run(starup_prog)
            res = exe.run(fetch_list=[x, out])
            self.assertEqual(res[1].shape, (6, 6, 10))

            paddle.static.save_inference_model(self.save_path, [x], [out], exe)
            # Test for Inference Predictor
            infer_out = self.infer_prog()
            self.assertEqual(infer_out.shape, (6, 6, 10))


if __name__ == '__main__':
    unittest.main()