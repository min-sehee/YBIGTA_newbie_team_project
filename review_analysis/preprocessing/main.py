import os
import glob
from argparse import ArgumentParser
from typing import Dict, Type
from review_analysis.preprocessing.base_processor import BaseDataProcessor
from review_analysis.preprocessing.kyobo_processor import KyoboProcessor
from review_analysis.preprocessing.yes24_processor import Yes24Processor
from review_analysis.preprocessing.aladin_processor import AladinProcessor

PREPROCESS_CLASSES: Dict[str, Type[BaseDataProcessor]] = {
    # csv basename : 전처리 클래스(클래스명을 대문자로 적기)
    "reviews_aladin": AladinProcessor,
    "reviews_kyobo": KyoboProcessor,
    "reviews_yes24": Yes24Processor
    # "reviews_example": ExampleProcessor,
}

REVIEW_COLLECTIONS = glob.glob(os.path.join("database", "reviews_*.csv"))

def create_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('-o', '--output_dir', type=str, required=False, default="database",
                        help="Output file dir. Example: database")
    parser.add_argument('-c', '--preprocessor', type=str, required=False, choices=PREPROCESS_CLASSES.keys(),
                        help=f"Which processor to use. Choices: {', '.join(PREPROCESS_CLASSES.keys())}")
    parser.add_argument('-a', '--all', action='store_true', help="Run all data preprocessors. Default to False.")
    return parser

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    if args.all: 
        for csv_file in REVIEW_COLLECTIONS:
            base_name = os.path.splitext(os.path.basename(csv_file))[0]
            if base_name in PREPROCESS_CLASSES:
                preprocessor_class = PREPROCESS_CLASSES[base_name]
                preprocessor = preprocessor_class(csv_file, args.output_dir)
                preprocessor.preprocess()
                preprocessor.feature_engineering()
                preprocessor.save_to_database()
    elif args.preprocessor:
        base_name = args.preprocessor
        found = False
        for csv_file in REVIEW_COLLECTIONS:
            if os.path.splitext(os.path.basename(csv_file))[0] == base_name:
                preprocessor_class = PREPROCESS_CLASSES[base_name]
                preprocessor = preprocessor_class(csv_file, args.output_dir)
                preprocessor.preprocess()
                preprocessor.feature_engineering()
                preprocessor.save_to_database()
                found = True
                break
        if not found:
            raise FileNotFoundError(f"해당 csv 파일({base_name}.csv)을 찾을 수 없습니다.")
    else:
        raise ValueError("No preprocessors selected. '-a' 또는 '-c [key]' 옵션을 사용하세요.")
