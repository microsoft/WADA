# Copyright 2023 @ CAMEL-AI.org. All Rights Reserved.
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

import os
from functools import wraps
from typing import Any, Callable, List

import tiktoken

from wada.messages import OpenAIMessage
from wada.typing import ModelType


def count_tokens_openai_chat_models(
    messages: List[OpenAIMessage],
    encoding: Any,
) -> int:
    r"""Counts the number of tokens required to generate an OpenAI chat based
    on a given list of messages.

    Args:
        messages (List[OpenAIMessage]): The list of messages.
        encoding (Any): The encoding method to use.

    Returns:
        int: The number of tokens required.
    """
    num_tokens = 0
    for message in messages:
        # message follows <im_start>{role/name}\n{content}<im_end>\n
        num_tokens += 4
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":  # if there's a name, the role is omitted
                num_tokens += -1  # role is always 1 token
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens


def num_tokens_from_messages(
    messages: List[OpenAIMessage],
    model: ModelType,
) -> int:
    r"""Returns the number of tokens used by a list of messages.

    Args:
        messages (List[OpenAIMessage]): The list of messages to count the
            number of tokens for.
        model (ModelType): The OpenAI model used to encode the messages.

    Returns:
        int: The total number of tokens used by the messages.

    Raises:
        NotImplementedError: If the specified `model` is not implemented.

    References:
        - https://github.com/openai/openai-python/blob/main/chatml.md
        - https://platform.openai.com/docs/models/gpt-4
        - https://platform.openai.com/docs/models/gpt-3-5
    """
    try:
        encoding = tiktoken.encoding_for_model(model.value)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == ModelType.GPT_3_5_TURBO:
        return count_tokens_openai_chat_models(messages, encoding)
    elif model == ModelType.GPT_4:
        return count_tokens_openai_chat_models(messages, encoding)
    elif model == ModelType.GPT_4_32k:
        return count_tokens_openai_chat_models(messages, encoding)
    else:
        raise NotImplementedError(
            f"`num_tokens_from_messages`` is not presently implemented "
            f"for model {model}. "
            f"See https://github.com/openai/openai-python/blob/main/chatml.md "
            f"for information on how messages are converted to tokens. "
            f"See https://platform.openai.com/docs/models/gpt-4"
            f"or https://platform.openai.com/docs/models/gpt-3-5"
            f"for information about openai chat models.")


def get_model_token_limit(model: ModelType) -> int:
    if model == ModelType.GPT_3_5_TURBO:
        return 4096
    if model == ModelType.GPT_4:
        return 8192
    if model == ModelType.GPT_4_32k:
        return 32768


def openai_api_env_required(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Callable[..., Any]:
        if 'OPENAI_API_KEY' in os.environ and 'OPENAI_API_BASE' in os.environ and 'OPENAI_API_VERSION' in os.environ:
            return func(*args, **kwargs)
        else:
            raise ValueError('OpenAI API environment variables not found.')

    return wrapper
