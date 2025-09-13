# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("tencent/Hunyuan-0.5B-Instruct")
model = AutoModelForCausalLM.from_pretrained("tencent/Hunyuan-0.5B-Instruct")
messages = [
    {"role": "user", "content": "introduce react?"},
]

inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
)

# 移除 token_type_ids
if "token_type_ids" in inputs:
    del inputs["token_type_ids"]

# 放到模型设备
inputs = {k: v.to(model.device) for k, v in inputs.items()}

# 生成
outputs = model.generate(**inputs, max_new_tokens=100)

# 输出回答
print(tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:]))
