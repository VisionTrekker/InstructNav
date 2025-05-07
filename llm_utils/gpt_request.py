import os
from openai import AzureOpenAI,OpenAI
import requests
import base64
import cv2
import numpy as np
from mimetypes import guess_type
os.environ['GPT4_API_KEY'] = "sk-218fa7efec66472d9671986c181fdeef"  # sk-86b3c68cbfd9463683e0e070be3b94cc
os.environ['GPT4_API_BASE'] = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # https://api.deepseek.com/v1
os.environ['GPT4_API_DEPLOY'] = "qwen2.5-32b-instruct"  # deepseek-chat、deepseek-reasoner

os.environ['GPT4V_API_KEY'] = "sk-srmcfmbcwepibwmqjlngjowbfzbkbhetzdouxtfzgvvwtppb"
os.environ['GPT4V_API_BASE'] = "https://api.siliconflow.cn/v1"
os.environ['GPT4V_API_DEPLOY'] = "Qwen/Qwen2.5-VL-32B-Instruct"

gpt4_api_base = os.environ['GPT4_API_BASE']
gpt4_api_key = os.environ['GPT4_API_KEY']
deployment_name = os.environ['GPT4_API_DEPLOY']

gpt4v_api_base = os.environ['GPT4V_API_BASE']
gpt4v_api_key = os.environ['GPT4V_API_KEY']
deployment_name_vision = os.environ['GPT4V_API_DEPLOY']

gpt4_client = OpenAI(
    api_key=gpt4_api_key,
    base_url=gpt4_api_base,
)
gpt4v_client = OpenAI(
    api_key=gpt4v_api_key,
    base_url=gpt4v_api_base,
)

def local_image_to_data_url(image):
    if isinstance(image,str):
        mime_type, _ = guess_type(image)
        with open(image, "rb") as image_file:
            base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:{mime_type};base64,{base64_encoded_data}"
    elif isinstance(image,np.ndarray):
        base64_encoded_data = base64.b64encode(cv2.imencode('.jpg',image)[1]).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_encoded_data}"

def gptv_response(text_prompt,image_prompt,system_prompt=""):
    prompt = [{'role':'system','content':system_prompt},
             {'role':'user','content':[{'type':'text','text':text_prompt},
                                       {'type':'image_url','image_url':{'url':local_image_to_data_url(image_prompt)}}]}]
    response = gpt4v_client.chat.completions.create(model=deployment_name_vision,
                                                    messages=prompt,
                                                    max_tokens=1000)
    return response.choices[0].message.content

def gpt_response(text_prompt,system_prompt=""):
    prompt = [{'role':'system','content':system_prompt},
              {'role':'user','content':[{'type':'text','text':text_prompt}]}]
    response = gpt4_client.chat.completions.create(model=deployment_name,
                                              messages=prompt,
                                              max_tokens=1000)
    return response.choices[0].message.content


if __name__ == "__main__":
    try:
        print("Start text model testing...")
        question = "你好，请简单介绍一下通义千问和DeepSeek的区别？"
        answer = gpt_response(question, system_prompt="You are a helpful assistant.")
        print("Text Model response:", answer)

        print("\nStart text-vision model testing...")
        test_image = np.zeros((512, 512, 3), dtype=np.uint8)
        cv2.putText(test_image, "test test", (150, 256),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        vision_question = "图片中有什么文字？背景是什么颜色？"
        vision_answer = gptv_response(vision_question, test_image, system_prompt="你是一个视觉助手，请回答关于图片的问题")
        print("Vision-Text Model response:", vision_answer)
    except Exception as e:
        print("Error occurred:", e)
