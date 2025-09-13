# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import uvicorn  # 用来在脚本内直接启动 HTTP 服务

# -------------------------------
# 1. 初始化模型
# -------------------------------
tokenizer = AutoTokenizer.from_pretrained("tencent/Hunyuan-0.5B-Instruct")
model = AutoModelForCausalLM.from_pretrained("tencent/Hunyuan-0.5B-Instruct")
device = "mps" if torch.backends.mps.is_available() else "cpu"  # 或 "cuda" / "cpu"
model.to(device)

# -------------------------------
# 2. FastAPI 初始化
# -------------------------------
app = FastAPI()

# 请求参数定义
class Query(BaseModel):
    question: str

# -------------------------------
# 3. 问答接口
# -------------------------------
@app.post("/chat")
def chat(query: Query):
    messages = [{"role": "user", "content": query.question}]
    
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    )

    if "token_type_ids" in inputs:
        del inputs["token_type_ids"]

    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    outputs = model.generate(**inputs, max_new_tokens=200)
    
    answer = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:])
    return {"answer": answer}

# -------------------------------
# 4. 允许 uv run app.py 启动 HTTP 服务
# -------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
