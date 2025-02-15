from sklearn.metrics import f1_score
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def compute_f1(predicted_text, expected_answer):
    pred_embedding = model.encode(predicted_text, convert_to_tensor=True)
    exp_embedding = model.encode(expected_answer, convert_to_tensor=True)
    
    similarity = util.pytorch_cos_sim(pred_embedding, exp_embedding).item()
    return similarity

f1_scores = []

for q in golden_questions:
    retrieved_results = query_weaviate(q["question"])
    best_result = retrieved_results[0]["text"] if retrieved_results else ""

    f1 = compute_f1(best_result, q["expected_answer"])
    f1_scores.append(f1)

average_f1 = sum(f1_scores) / len(f1_scores)
print(f"Average F1 Score: {average_f1:.3f}")
