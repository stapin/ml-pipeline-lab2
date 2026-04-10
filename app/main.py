from fastapi import FastAPI
from app.schemas import ReviewRequest, ReviewResponse
from app.model import Predictor

app = FastAPI(
    title="Amazon Beauty Rating Predictor API",
    description="API для предсказания рейтинга товара по тексту отзыва",
)

predictor = Predictor()

@app.post("/predict", response_model=ReviewResponse)
def predict_rating(request: ReviewRequest):
    input_dict = request.model_dump() 
    rating = predictor.predict(input_dict)

    return ReviewResponse(predicted_rating=rating)