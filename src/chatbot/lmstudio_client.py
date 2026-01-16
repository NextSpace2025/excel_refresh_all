"""
LM Studio API 클라이언트
LM Studio는 OpenAI 호환 API를 제공하므로 동일한 방식으로 호출 가능
"""
import json
from typing import List, Dict, Any, Optional, Generator

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class LMStudioClient:
    """LM Studio API 클라이언트"""

    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        model: str = "local-model",
        timeout: int = 120
    ):
        """
        Args:
            base_url: LM Studio 서버 URL (기본값: http://localhost:1234/v1)
            model: 모델 이름 (LM Studio에서는 보통 무시됨)
            timeout: 요청 타임아웃 (초)
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests가 설치되어 있지 않습니다. pip install requests")

        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.system_prompt = """당신은 엑셀 데이터를 분석하고 질문에 답변하는 도우미입니다.
사용자가 제공한 데이터를 기반으로 정확하고 유용한 답변을 제공하세요.
한국어로 답변하세요."""

    def set_system_prompt(self, prompt: str):
        """시스템 프롬프트 설정"""
        self.system_prompt = prompt

    def check_connection(self) -> Dict[str, Any]:
        """LM Studio 연결 확인"""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                timeout=5
            )
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "models": response.json().get("data", [])
                }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}"
                }
        except requests.exceptions.ConnectionError:
            return {
                "status": "disconnected",
                "message": "LM Studio에 연결할 수 없습니다. LM Studio가 실행 중인지 확인하세요."
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def chat(
        self,
        message: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        채팅 메시지 전송

        Args:
            message: 사용자 메시지
            context: 추가 컨텍스트 (예: 검색된 데이터)
            conversation_history: 이전 대화 내역
            temperature: 창의성 (0.0 ~ 1.0)
            max_tokens: 최대 토큰 수

        Returns:
            응답 결과
        """
        messages = []

        # 시스템 프롬프트
        system_content = self.system_prompt
        if context:
            system_content += f"\n\n참고 데이터:\n{context}"

        messages.append({
            "role": "system",
            "content": system_content
        })

        # 대화 내역 추가
        if conversation_history:
            messages.extend(conversation_history)

        # 현재 메시지
        messages.append({
            "role": "user",
            "content": message
        })

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False
                },
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                assistant_message = data["choices"][0]["message"]["content"]
                return {
                    "status": "success",
                    "message": assistant_message,
                    "usage": data.get("usage", {})
                }
            else:
                return {
                    "status": "error",
                    "message": f"API 오류: HTTP {response.status_code}",
                    "detail": response.text
                }

        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": "요청 시간 초과"
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "message": "LM Studio에 연결할 수 없습니다"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def chat_stream(
        self,
        message: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Generator[str, None, None]:
        """
        스트리밍 채팅 (실시간 응답)

        Args:
            message: 사용자 메시지
            context: 추가 컨텍스트
            conversation_history: 이전 대화 내역
            temperature: 창의성
            max_tokens: 최대 토큰 수

        Yields:
            응답 텍스트 조각
        """
        messages = []

        system_content = self.system_prompt
        if context:
            system_content += f"\n\n참고 데이터:\n{context}"

        messages.append({
            "role": "system",
            "content": system_content
        })

        if conversation_history:
            messages.extend(conversation_history)

        messages.append({
            "role": "user",
            "content": message
        })

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True
                },
                timeout=self.timeout,
                stream=True
            )

            for line in response.iter_lines():
                if line:
                    line_text = line.decode("utf-8")
                    if line_text.startswith("data: "):
                        data_str = line_text[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            yield f"\n[오류: {str(e)}]"

    def generate_sql_query(
        self,
        question: str,
        table_info: str
    ) -> Dict[str, Any]:
        """
        자연어 질문을 SQL 쿼리로 변환

        Args:
            question: 사용자 질문
            table_info: 테이블 스키마 정보

        Returns:
            생성된 SQL 쿼리
        """
        prompt = f"""주어진 테이블 정보를 바탕으로 사용자 질문에 답하는 SQL SELECT 쿼리를 생성하세요.

테이블 정보:
{table_info}

사용자 질문: {question}

규칙:
1. SELECT 쿼리만 생성하세요
2. 쿼리만 출력하세요, 설명은 필요없습니다
3. SQL 쿼리를 ```sql 코드 블록으로 감싸세요

SQL 쿼리:"""

        response = self.chat(prompt, temperature=0.1)

        if response["status"] == "success":
            # SQL 코드 블록 추출
            content = response["message"]
            if "```sql" in content:
                sql = content.split("```sql")[1].split("```")[0].strip()
            elif "```" in content:
                sql = content.split("```")[1].split("```")[0].strip()
            else:
                sql = content.strip()

            return {
                "status": "success",
                "sql": sql
            }
        else:
            return response


# 사용 예시
if __name__ == "__main__":
    client = LMStudioClient()

    # 연결 확인
    status = client.check_connection()
    print(f"연결 상태: {status}")

    if status["status"] == "connected":
        # 간단한 테스트
        response = client.chat("안녕하세요, 테스트 메시지입니다.")
        print(f"응답: {response}")
