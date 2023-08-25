# Copyright © Microsoft Corporation.
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

from colorama import Fore

from wada.debate import Debate
from wada.topic import Topic


def main() -> None:

    content = "Living in Beijing or Chengdu?"
    topic_pro = "Living in Beijing"
    topic_con = "Living in Chengdu"
    background = "Beijing, as China's capital, offers a higher number of job opportunities, especially in the technology and finance sectors. However, the cost of living is also higher than in Chengdu. The climate is characterized by hot, humid summers and cold, dry winters. Though Beijing boasts an international atmosphere and a large expat community, it also faces challenges with air pollution. The city, however, provides a wide range of high-quality education and healthcare facilities. Chengdu, while having a smaller job market, has a lower cost of living and is becoming a growing tech hub, attracting global companies. The climate is mild and humid, with relatively mild winters and moderate summers. Chengdu offers a relaxed pace of life and is famous for its leisurely teahouses and close proximity to nature, such as the Panda Research Base and Jiuzhaigou. Additionally, Chengdu's education and healthcare facilities are also improving, though not as abundant as those in Beijing."
    preference = "The person prioritizes a larger number of job options and am willing to compromise on the cost of living for better job prospects or social life. And he prefers a milder, more temperate climate and favor a more relaxed and nature-oriented social environment. Additionally, He is seeking top-tier education and healthcare institutions."
    specified_aspects = "1. Job opportunities; 2. Cost of living; 3. Quality of life; 4. Transportation and infrastructure; 5. Climate and environment"

    topic = Topic(content=content, pro=topic_pro, con=topic_con,
                  background=background, preference=preference,
                  specified_aspects=specified_aspects)

    print(Fore.YELLOW + f"Original Topic:\n{content}\n")
    print(Fore.GREEN + f"Pro side:\n{topic_pro}\n")
    print(Fore.BLUE + f"Con side:\n{topic_con}\n")
    print(Fore.GREEN + f"Background:\n{background}\n")
    print(Fore.BLUE + f"Preference:\n{preference}\n")

    debate_session = Debate(topic=topic, with_host_in_the_loop=False)

    print(
        Fore.GREEN +
        f"{debate_session.debater_a_name} sys message:\n{debate_session.debater_a_sys_msg.content}\n"
    )
    print(
        Fore.BLUE +
        f"{debate_session.debater_b_name} sys message:\n{debate_session.debater_b_sys_msg.content}\n"
    )

    chat_turn_limit, n = 50, 0

    while n < chat_turn_limit:
        n += 1
        if n == 1:
            debater_a_return, debater_b_return = debate_session.init_chat()
        else:
            debater_a_return, debater_b_return = debate_session.step(
                debater_b_reply)

        debater_a_reply, debater_a_terminated, debater_a_info = debater_a_return
        debater_b_reply, debater_b_terminated, debater_b_info = debater_b_return

        if debater_a_terminated:
            print(Fore.GREEN +
                  (f"{debate_session.debater_a_name} terminated. "
                   f"Reason: {debater_a_info['termination_reasons']}."))
            break
        if debater_b_terminated:
            print(Fore.GREEN +
                  (f"{debate_session.debater_b_name} terminated. "
                   f"Reason: {debater_b_info['termination_reasons']}."))
            break

        print(Fore.YELLOW + f"Round {n}\n")
        debater_a_reply_str = f"{debate_session.debater_a_name}:\n\n{debater_a_reply.content}\n"
        debater_b_reply_str = f"{debate_session.debater_b_name}:\n\n{debater_b_reply.content}\n"
        print(Fore.GREEN + debater_a_reply_str)
        print(Fore.BLUE + debater_b_reply_str)

        if "DEBATE_TOPIC_DONE" in debater_b_reply.content or "DEBATE_TOPIC_DONE" in debater_a_reply.content:
            break


if __name__ == "__main__":
    main()
