from fastapi import APIRouter
from app.responses.base_response import BaseResponse
from database.mongodb_connection import mongo_db
from review_analysis.preprocessing.kyobo_processor import KyoboProcessor
from review_analysis.preprocessing.yes24_processor import Yes24Processor
from review_analysis.preprocessing.aladin_processor import AladinProcessor

import pandas as pd
import io

review = APIRouter(prefix="/review")

@review.post("/preprocess/{site_name}")
def preprocess_reviews(site_name: str):
    """
    주어진 사이트의 크롤링 데이터를 MongoDB에서 불러와 전처리하고, 
    전처리된 데이터를 다시 MongoDB에 저장하는 API

    Parameters:
    - site_name (str): 전처리할 대상 사이트 이름. 예) "kyobo", "yes24", "aladin"

    Returns:
    - BaseResponse: 전처리 성공 여부 및 전처리된 데이터 개수를 포함한 응답
    """
    collection = mongo_db[site_name]
    raw_data = list(collection.find({}, {"_id": 0}))  
    print("raw_data:", raw_data[:2])
    if not raw_data:
        return BaseResponse(status="fail", data=None, message="No data found")

    df = pd.DataFrame(raw_data)
    print("초기 DF shape:", df.shape)

    temp_input_path = f"temp_raw_{site_name}.csv"
    df.to_csv(temp_input_path, index=False)

    if site_name == "kyobo":
        processor = KyoboProcessor(input_path=temp_input_path, output_path="output")
    elif site_name == "yes24":
        processor = Yes24Processor(input_path=temp_input_path, output_path="output")
    elif site_name == "aladin":
        processor = AladinProcessor(input_path=temp_input_path, output_path="output")
    else:
        return BaseResponse(status="fail", data=None, message=f"Unsupported site: {site_name}")
    
    processor.preprocess()
    processor.feature_engineering()
    print("전처리 후 DF shape:", processor.df.shape)

    result = processor.df.to_dict(orient="records")
    print("✅ 전처리 결과 개수:", len(result))
    result_collection = mongo_db[f"{site_name}_processed"]
    result_collection.delete_many({})  
    result_collection.insert_many(result)

    return BaseResponse(status="success", data={"count": len(result)}, message="Preprocessing completed.")
