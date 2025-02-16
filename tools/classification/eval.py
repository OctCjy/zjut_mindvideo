# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""MindSpore Vision Video infer script."""
import os
import sys

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(__dir__, "../..")))

from mindspore import context, nn, load_checkpoint, load_param_into_net
from mindspore.train import Model

from mindvideo.utils.check_param import Validator, Rel
from mindvideo.utils.config import parse_args, Config
from mindvideo.utils.load import load_model
from mindvideo.loss.builder import build_loss
from mindvideo.data.builder import build_dataset, build_transforms
from mindvideo.models import build_model


def eval_classification(pargs):
    # set config context
    config = Config(pargs.config)
    context.set_context(**config.context)

    # perpare dataset
    transforms = build_transforms(config.data_loader.eval.map.operations)
    data_set = build_dataset(config.data_loader.eval.dataset)
    data_set.transform = transforms
    dataset_eval = data_set.run()
    Validator.check_int(dataset_eval.get_dataset_size(), 0, Rel.GT)

    # set loss
    network_loss = build_loss(config.loss)

    # set network and load pretrain model
    ckpt_path = config.infer.pretrained_model
    network = None
    if os.path.splitext(ckpt_path)[-1] == '.ckpt':
        network = build_model(config.model)
    
    network = load_model(ckpt_path, network)

    # Define eval_metrics.
    eval_metrics = {'Top_1_Accuracy': nn.Top1CategoricalAccuracy(),
                    'Top_5_Accuracy': nn.Top5CategoricalAccuracy()}
    # init the whole Model
    model = Model(network,
                  network_loss,
                  metrics=eval_metrics)

    # Begin to eval.
    result = model.eval(dataset_eval)

    return result


if __name__ == '__main__':
    args = parse_args()
    result = eval_classification(args)
    print(result)
