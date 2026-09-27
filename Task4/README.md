curl -L 'https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf?download=true' -O

docker run --rm -p 8000:8000 -v .:/models ghcr.io/ggml-org/llama.cpp:server -m /models/qwen2.5-1.5b-instruct-q4_k_m.gguf --host 0.0.0.0 --port 8000 -c 4096 --repeat-penalty 1.15 --repeat-last-n 256 --dry-multiplier 0.8

./rag_query.sh --openai-embeddings --openai-llm "С кем взаимодействовал Мышь?"

./bot.sh
