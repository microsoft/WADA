# Copyright © Microsoft Corporation.
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
#
# Modifications:
# - Added DebaterPromptGenerator and DebaterPromptTemplateGenerator

import warnings
from typing import Dict, Tuple

from wada.messages import SystemMessage
from wada.prompts.base import TextPrompt
from wada.prompts.debate import DebatePromptTemplateDict
from wada.typing import RoleType


class SystemMessageGenerator:
    r"""System message generator for agents."""

    def __init__(self) -> None:
        self.prompt_dict = DebatePromptTemplateDict()

    def validate_meta_dict_keys(self, sys_prompt: TextPrompt,
                                meta_dict: Dict[str, str]) -> None:
        if not set(meta_dict.keys()).issubset(sys_prompt.key_words):
            raise ValueError("The keys of the meta_dict should be in "
                             f"{sys_prompt.key_words}. "
                             f"Got {set(meta_dict.keys())} instead.")

    def from_dict(
        self,
        meta_dict: Dict[str, str],
        role_tuple: Tuple[str, RoleType] = ("", RoleType.DEFAULT),
    ) -> SystemMessage:
        role_name, role_type = role_tuple
        try:
            sys_prompt = self.prompt_dict[role_type]
            self.validate_meta_dict_keys(sys_prompt, meta_dict)
            sys_prompt = sys_prompt.format(**meta_dict)
        except KeyError:
            sys_prompt = TextPrompt("You are a helpful assistant.")
            warnings.warn("Failed to get system prompt template for "
                          f"role: {role_type.value}. "
                          f"Set template to: {sys_prompt}")
        return SystemMessage(role_name=role_name, role_type=role_type,
                             meta_dict=meta_dict, content=sys_prompt)


class DebatePromptGenerator:
    r"""Debate prompt generator for agents."""

    def __init__(self) -> None:
        self.prompt_dict = DebatePromptTemplateDict()

    def get_topic_break_down_prompt(self, topic: str) -> str:
        return self.prompt_dict['topic_break_down'].format(**dict(topic=topic))

    def get_topic_specify_prompt(self, topic: str) -> str:
        return self.prompt_dict['topic_specify'].format(**dict(topic=topic))

    def get_topic_abbreviate_prompt(self, topic: str) -> str:
        return self.prompt_dict['topic_abbreviate'].format(**dict(topic=topic))

    def get_collect_bg_prompt(self) -> str:
        return self.prompt_dict['topic_collect_bg']

    def get_collect_info_prompt(self) -> str:
        return self.prompt_dict['topic_collect_info']

    def get_rephrase_sum_prompt(self) -> str:
        return self.prompt_dict['topic_rephrase_sum']

    def get_host_decision_prompt(self) -> str:
        return self.prompt_dict['host_decision']

    def get_judge_prompt(self, aspects: str) -> str:
        return self.prompt_dict['host_judge'].format(**dict(aspect=aspects))


class DebatePromptTemplateGenerator:
    r"""Debate prompt template generator for agents."""

    def __init__(self) -> None:
        self.prompt_dict = DebatePromptTemplateDict()

    def get_sys_msg_prompt_template(self) -> str:
        return self.prompt_dict['langchain_sys_msg']

    def get_hmn_msg_prompt_template(self) -> str:
        return self.prompt_dict['langchain_hmn_msg']
