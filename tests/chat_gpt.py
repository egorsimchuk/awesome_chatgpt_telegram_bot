import json
import time

from pathlib import Path

from chat_gpt.model import ChatGPT

with open(Path(__file__).parents[1]/"configs/config.json", "rb")as f:
    config = json.load(f)

def test_response():
    chat_gpt = ChatGPT(config["openai_token"])
    start_time = time.time()
    output = chat_gpt.get_response("Hello!")
    print(f"\nGet responce for {round(time.time()-start_time,1)} seconds")
    print(output)
    assert len(output)>0
