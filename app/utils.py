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
# - Added save_markdown_file method

import re
from datetime import datetime
from typing import Any

from jinja2 import Template


def split_markdown_code(string: str) -> str:
    """ Split a multiline block of markdown code (triple-quotes) into
    line-sized sub-blocks to make newlines stay where they belong.
    This transformation is a workaround to a known Gradio bug:
    https://github.com/gradio-app/gradio/issues/3531

    Args:
        string (str): markdown string incompatible with gr.Chatbot

    Returns:
        str: markdown string which is compatible with gr.Chatbot
    """
    substr_list = string.split("```")
    out = []
    for i_subs, subs in enumerate(substr_list):
        if i_subs % 2 == 0:  # outsize code, don't change
            out.append(subs)
        else:  # inside code
            br_done = re.sub(r"<br>", "\n", subs)

            def repl(m):
                return "```{}```".format(m.group(0))

            new_subs = re.sub(r"\n+", repl, br_done)
            out.append(new_subs)
    out_str = "```".join(out)
    out_str_cleanup = re.sub(r"``````", "", out_str)
    return out_str_cleanup


def save_markdown_file(
    data: Any,
    template_file: str = "app\\template.md",
) -> None:
    """ Save a markdown file with the given data.
    """
    with open(template_file, "r") as file:
        template = Template(file.read())

    for i in range(len(data["debate_history"])):
        data["debate_history"][i].content = data["debate_history"][
            i].content.replace('\n', '\n\n> ')

    filled_template = template.render(**data)

    time_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    output_file = f"app\\cases\\{data['catagory']}\\{time_str}.md"
    with open(output_file, "w") as file:
        file.write(filled_template)
