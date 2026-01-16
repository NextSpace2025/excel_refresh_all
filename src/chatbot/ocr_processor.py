import os
import re
import sys
from datetime import datetime
import easyocr
from typing import List, Dict, Any

# Windows 환경에서의 인코딩 문제 해결
if sys.stdout.encoding.lower() == 'utf-8':
    pass
else:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

class OnDeviceOCR:
    """온디바이스에서 한글/영어 OCR을 수행하고 결과를 필터링 및 저장하는 클래스"""

    def __init__(self, languages: List[str] = ['ko', 'en'], gpu: bool = False):
        """
        OCR 엔진 초기화
        :param languages: 인식할 언어 리스트
        :param gpu: GPU(CUDA) 사용 여부
        """
        print(f"OCR 엔진 초기화 중... (언어: {languages})")
        self.reader = easyocr.Reader(languages, gpu=gpu)
        # 추출할 정규표현식 패턴 정의
        self.patterns = {
            "biz_num": r'\d{3}-\d{2}-\d{5}',      # 사업자 번호
            "phone": r'\d{2,3}-\d{3,4}-\d{4}'     # 전화번호
        }
        print("OCR 엔진 준비 완료.")

    def extract_filtered_text(self, image_path: str, min_confidence: float = 0.5) -> List[Dict[str, Any]]:
        """
        이미지에서 텍스트를 추출하고 신뢰도에 따라 필터링
        :param image_path: 이미지 파일 경로
        :param min_confidence: 최소 신뢰도 임계값 (0.0 ~ 1.0)
        :return: 필터링된 결과 리스트 (텍스트, 신뢰도 포함)
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")

        # OCR 수행: 결과는 [[좌표], 텍스트, 신뢰도] 형태의 리스트로 반환됨
        raw_results = self.reader.readtext(image_path)
        
        filtered_results = []
        for bbox, text, confidence in raw_results:
            if confidence >= min_confidence:
                filtered_results.append({
                    "text": text,
                    "confidence": round(float(confidence), 4),
                    "bbox": bbox
                })
        
        return filtered_results

    def save_to_excel(self, results: List[Dict[str, Any]], output_path: str):
        """
        OCR 결과를 엑셀 파일로 저장
        :param results: 필터링된 OCR 결과 리스트
        :param output_path: 저장할 엑셀 파일 경로
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas와 openpyxl 라이브러리가 필요합니다. 'pip install pandas openpyxl'을 실행하세요.")

        if not results:
            print("저장할 데이터가 없습니다.")
            return

        # 패턴 추출을 위해 전체 텍스트 결합
        full_text = " ".join([r['text'] for r in results])
        
        df = pd.DataFrame(results)

        # 정의된 패턴별로 검색하여 컬럼 추가
        for col_name, pattern in self.patterns.items():
            match = re.search(pattern, full_text)
            df[col_name] = match.group(0) if match else ""

        # 엑셀 저장 시 좌표(bbox) 데이터는 문자열로 변환하여 저장
        if 'bbox' in df.columns:
            df['bbox'] = df['bbox'].apply(lambda x: str(x))
            
        df.to_excel(output_path, index=False)
        print(f"결과가 성공적으로 저장되었습니다 (패턴 추출 포함): {output_path}")

    def organize_file_by_ocr(self, image_path: str, max_length: int = 30) -> str:
        """
        OCR 결과를 바탕으로 파일명을 변경하여 정리
        :param image_path: 원본 이미지 경로
        :param max_length: 파일명의 최대 길이
        :return: 변경된 파일 경로
        """
        # 1. 텍스트 추출 (신뢰도 0.6 이상)
        results = self.extract_filtered_text(image_path, min_confidence=0.6)
        
        if not results:
            print(f"텍스트를 추출할 수 없어 파일명을 변경하지 않습니다: {image_path}")
            return image_path

        # 2. 파일명 후보 생성 (상위 3개 텍스트 결합)
        combined_text = " ".join([r['text'] for r in results[:3]])
        
        # 3. 파일명 사용 불가능한 특수문자 제거 및 정규화
        clean_name = re.sub(r'[\\/*?:"<>|]', "", combined_text)
        clean_name = " ".join(clean_name.split())  # 중복 공백 제거
        clean_name = clean_name[:max_length].strip()

        if not clean_name:
            clean_name = "unnamed_ocr_result"

        # 4. 경로 및 확장자 처리
        directory = os.path.dirname(image_path)
        extension = os.path.splitext(image_path)[1]
        new_path = os.path.join(directory, f"{clean_name}{extension}")

        # 5. 동일 파일명 존재 시 번호 부여
        counter = 1
        base_new_path = os.path.join(directory, clean_name)
        while os.path.exists(new_path):
            new_path = f"{base_new_path}_{counter}{extension}"
            counter += 1

        # 6. 파일명 변경 실행
        os.rename(image_path, new_path)
        print(f"파일명 정리 완료: {os.path.basename(image_path)} -> {os.path.basename(new_path)}")
        return new_path

    def batch_organize_images(self, folder_path: str, max_length: int = 30, log_filename: str = "ocr_batch_process.log"):
        """
        특정 폴더 내의 모든 이미지 파일을 OCR 기반으로 일괄 이름 변경
        :param folder_path: 대상 폴더 경로
        :param max_length: 파일명의 최대 길이
        :param log_filename: 생성할 로그 파일 이름
        """
        if not os.path.isdir(folder_path):
            print(f"에러: '{folder_path}'는 유효한 폴더 경로가 아닙니다.")
            return

        # 처리 가능한 이미지 확장자 정의
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)]

        if not files:
            print(f"폴더 내에 처리할 이미지 파일이 없습니다.")
            return

        print(f"총 {len(files)}개의 파일을 처리를 시작합니다...")
        log_entries = [f"=== OCR Batch Process Started at {datetime.now()} ==="]
        
        for i, filename in enumerate(files, 1):
            file_path = os.path.join(folder_path, filename)
            print(f"[{i}/{len(files)}] 처리 중: {filename}")
            try:
                new_path = self.organize_file_by_ocr(file_path, max_length)
                new_filename = os.path.basename(new_path)
                
                if filename != new_filename:
                    log_entries.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SUCCESS: {filename} -> {new_filename}")
                else:
                    log_entries.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SKIPPED: {filename} (No text detected or name unchanged)")
                    
            except Exception as e:
                error_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: {filename} - {str(e)}"
                print(error_msg)
                log_entries.append(error_msg)

        log_entries.append(f"=== Process Finished at {datetime.now()} ===\n")
        
        # 로그 파일 저장
        log_path = os.path.join(folder_path, log_filename)
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write("\n".join(log_entries) + "\n")

        print(f"모든 배치 작업이 완료되었습니다. 로그 확인: {log_path}")

if __name__ == "__main__":
    # 사용 예시
    ocr = OnDeviceOCR(gpu=False)
    
    # 특정 폴더 내 이미지 일괄 정리 (폴더 경로를 실제 경로로 수정하세요)
    target_folder = "./sample_images" 
    ocr.batch_organize_images(target_folder)