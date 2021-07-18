from transformers import pipeline

generator = pipeline('text-generation', model='EleutherAI/gpt-neo-125M')