/* Copyright (c) 2016 PaddlePaddle Authors. All Rights Reserve.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. */

#ifndef __PADDLE_CAPI_GRADIENT_MACHINE_H__
#define __PADDLE_CAPI_GRADIENT_MACHINE_H__
#include "arguments.h"
#include "config.h"
#include "error.h"

#ifdef __cplusplus
extern "C" {
#endif
/**
 * @brief GradientMachine means a neural network.
 */
typedef void* paddle_gradient_machine;

/**
 * @brief Create a gradient machine used for model inference.
 * @param [out] machine that used for model inference.
 * @param [in] modelConfigProtobuf
 * @param [in] size
 * @return paddle_error
 */
PD_API paddle_error paddle_gradient_machine_create_for_inference(
    paddle_gradient_machine* machine, void* modelConfigProtobuf, int size);

/**
 * @brief Load parameter from disk.
 * @param machine Gradient Machine.
 * @param path local directory path.
 * @return paddle_error
 */
PD_API paddle_error paddle_gradient_machine_load_parameter_from_disk(
    paddle_gradient_machine machine, const char* path);

/**
 * @brief Forward a gradient machine
 * @param machine Gradient machine
 * @param inArgs input arguments
 * @param outArgs output arguments
 * @param isTrain is train or not
 * @return paddle_error
 */
PD_API paddle_error
paddle_gradient_machine_forward(paddle_gradient_machine machine,
                                paddle_arguments inArgs,
                                paddle_arguments outArgs,
                                bool isTrain);

/**
 * @brief Create a gradient machine, which parameters are shared from another
 *        gradient machine.
 * @param [in] origin gradient machine
 * @param [in] modelConfigProtobuf model config protobuf
 * @param [in] size of model config buffer.
 * @param [out] slave gradient machine, the output value.
 * @return paddle_error
 */
PD_API paddle_error
paddle_gradient_machine_create_shared_param(paddle_gradient_machine origin,
                                            void* modelConfigProtobuf,
                                            int size,
                                            paddle_gradient_machine* slave);

/**
 * @brief Destroy a gradient machine
 * @param machine that need to destroy
 * @return paddle_error
 */
PD_API paddle_error
paddle_gradient_machine_destroy(paddle_gradient_machine machine);

#ifdef __cplusplus
}
#endif
#endif
