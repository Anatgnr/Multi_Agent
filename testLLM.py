from LLM.local_model import load_llm
from LLM.local_provider import LocalLLM
import torch

raw_llm = load_llm()
llm = LocalLLM(raw_llm)


while True:
    prompt = input("💡 Answer :\n> ")
    if prompt.lower() in ["quit", "exit"]:
        break
    response = llm.call(prompt)
    print("\n📝 Answer is :\n", response['output'], "\n")


# print(torch.__version__)
# print(torch.version.cuda)
# print(torch.cuda.is_available())
# print(torch.cuda.get_device_name(0))