import json
import os
import re
import textwrap
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from typing import Union

import httpx
from Levenshtein import distance
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompt_values import StringPromptValue
from langchain_core.prompts import ChatPromptTemplate

import src.strings as strings
from loguru import logger

load_dotenv()

# Lớp trừu tượng định nghĩa giao diện chung cho các mô hình AI
class AIModel(ABC):
    @abstractmethod
    def invoke(self, prompt: str) -> str:
        pass

# Lớp cụ thể cho mô hình OpenAI
class OpenAIModel(AIModel):
    def __init__(self, api_key: str, llm_model: str):
        from langchain_openai import ChatOpenAI
        self.model = ChatOpenAI(model_name=llm_model, openai_api_key=api_key,
                                temperature=0.4)

    def invoke(self, prompt: str) -> BaseMessage:
        logger.debug("Đang gọi API OpenAI")
        response = self.model.invoke(prompt)
        return response

# Lớp cụ thể cho mô hình Claude
class ClaudeModel(AIModel):
    def __init__(self, api_key: str, llm_model: str):
        from langchain_anthropic import ChatAnthropic
        self.model = ChatAnthropic(model=llm_model, api_key=api_key,
                                   temperature=0.4)

    def invoke(self, prompt: str) -> BaseMessage:
        response = self.model.invoke(prompt)
        logger.debug("Đang gọi API Claude")
        return response

# Lớp cụ thể cho mô hình Ollama
class OllamaModel(AIModel):
    def __init__(self, llm_model: str, llm_api_url: str):
        from langchain_ollama import ChatOllama

        if len(llm_api_url) > 0:
            logger.debug(f"Sử dụng Ollama với URL API: {llm_api_url}")
            self.model = ChatOllama(model=llm_model, base_url=llm_api_url)
        else:
            self.model = ChatOllama(model=llm_model)

    def invoke(self, prompt: str) -> BaseMessage:
        response = self.model.invoke(prompt)
        return response

# Lớp cụ thể cho mô hình Gemini
class GeminiModel(AIModel):
    def __init__(self, api_key:str, llm_model: str):
        from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
        self.model = ChatGoogleGenerativeAI(model=llm_model, google_api_key=api_key,safety_settings={
        HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DEROGATORY: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_TOXICITY: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_VIOLENCE: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUAL: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_MEDICAL: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
        })

    def invoke(self, prompt: str) -> BaseMessage:
        response = self.model.invoke(prompt)
        return response

# Lớp cụ thể cho mô hình HuggingFace
class HuggingFaceModel(AIModel):
    def __init__(self, api_key: str, llm_model: str):
        from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
        self.model = HuggingFaceEndpoint(repo_id=llm_model, huggingfacehub_api_token=api_key,
                                   temperature=0.4)
        self.chatmodel=ChatHuggingFace(llm=self.model)

    def invoke(self, prompt: str) -> BaseMessage:
        response = self.chatmodel.invoke(prompt)
        logger.debug("Đang gọi Model từ API Hugging Face")
        print(response,type(response))
        return response

# Lớp Adapter để chọn và khởi tạo mô hình AI phù hợp
class AIAdapter:
    def __init__(self, config: dict, api_key: str):
        self.model = self._create_model(config, api_key)

    def _create_model(self, config: dict, api_key: str) -> AIModel:
        llm_model_type = config['llm_model_type']
        llm_model = config['llm_model']

        llm_api_url = config.get('llm_api_url', "")

        logger.debug(f"Sử dụng {llm_model_type} với {llm_model}")

        if llm_model_type == "openai":
            return OpenAIModel(api_key, llm_model)
        elif llm_model_type == "claude":
            return ClaudeModel(api_key, llm_model)
        elif llm_model_type == "ollama":
            return OllamaModel(llm_model, llm_api_url)
        elif llm_model_type == "gemini":
            return GeminiModel(api_key, llm_model)
        elif llm_model_type == "huggingface":
            return HuggingFaceModel(api_key, llm_model)        
        else:
            raise ValueError(f"Loại mô hình không được hỗ trợ: {llm_model_type}")

    def invoke(self, prompt: str) -> str:
        return self.model.invoke(prompt)

# Lớp để ghi log các tương tác với mô hình LLM
class LLMLogger:

    def __init__(self, llm: Union[OpenAIModel, OllamaModel, ClaudeModel, GeminiModel]):
        self.llm = llm
        logger.debug(f"LLMLogger đã được khởi tạo thành công với LLM: {llm}")

    @staticmethod
    def log_request(prompts, parsed_reply: Dict[str, Dict]):
        logger.debug("Bắt đầu phương thức log_request")
        logger.debug(f"Prompts nhận được: {prompts}")
        logger.debug(f"Phản hồi đã phân tích nhận được: {parsed_reply}")

        try:
            calls_log = os.path.join(
                Path("data_folder/output"), "open_ai_calls.json")
            logger.debug(f"Đường dẫn ghi log đã được xác định: {calls_log}")
        except Exception as e:
            logger.error(f"Lỗi khi xác định đường dẫn ghi log: {str(e)}")
            raise

        if isinstance(prompts, StringPromptValue):
            logger.debug("Prompts có kiểu StringPromptValue")
            prompts = prompts.text
            logger.debug(f"Prompts đã được chuyển đổi thành văn bản: {prompts}")
        elif isinstance(prompts, Dict):
            logger.debug("Prompts có kiểu Dict")
            try:
                prompts = {
                    f"prompt_{i + 1}": prompt.content
                    for i, prompt in enumerate(prompts.messages)
                }
                logger.debug(f"Prompts đã được chuyển đổi thành từ điển: {prompts}")
            except Exception as e:
                logger.error(f"Lỗi khi chuyển đổi prompts thành từ điển: {str(e)}")
                raise
        else:
            logger.debug("Prompts có kiểu không xác định, đang thử chuyển đổi mặc định")
            try:
                prompts = {
                    f"prompt_{i + 1}": prompt.content
                    for i, prompt in enumerate(prompts.messages)
                }
                logger.debug(f"Prompts đã được chuyển đổi thành từ điển bằng phương thức mặc định: {prompts}")
            except Exception as e:
                logger.error(f"Lỗi khi chuyển đổi prompts bằng phương thức mặc định: {str(e)}")
                raise

        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.debug(f"Thời gian hiện tại đã được lấy: {current_time}")
        except Exception as e:
            logger.error(f"Lỗi khi lấy thời gian hiện tại: {str(e)}")
            raise

        try:
            token_usage = parsed_reply["usage_metadata"]
            output_tokens = token_usage["output_tokens"]
            input_tokens = token_usage["input_tokens"]
            total_tokens = token_usage["total_tokens"]
            logger.debug(f"Sử dụng token - Đầu vào: {input_tokens}, Đầu ra: {output_tokens}, Tổng: {total_tokens}")
        except KeyError as e:
            logger.error(f"Lỗi KeyError trong cấu trúc parsed_reply: {str(e)}")
            raise

        try:
            model_name = parsed_reply["response_metadata"]["model_name"]
            logger.debug(f"Tên mô hình: {model_name}")
        except KeyError as e:
            logger.error(f"Lỗi KeyError trong response_metadata: {str(e)}")
            raise

        try:
            prompt_price_per_token = 0.00000015
            completion_price_per_token = 0.0000006
            total_cost = (input_tokens * prompt_price_per_token) + \
                (output_tokens * completion_price_per_token)
            logger.debug(f"Tổng chi phí đã được tính toán: {total_cost}")
        except Exception as e:
            logger.error(f"Lỗi khi tính toán tổng chi phí: {str(e)}")
            raise

        try:
            log_entry = {
                "model": model_name,
                "time": current_time,
                "prompts": prompts,
                "replies": parsed_reply["content"],
                "total_tokens": total_tokens,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_cost": total_cost,
            }
            logger.debug(f"Mục ghi log đã được tạo: {log_entry}")
        except KeyError as e:
            logger.error(f"Lỗi khi tạo mục ghi log: thiếu khóa {str(e)} trong parsed_reply")
            raise

        try:
            with open(calls_log, "a", encoding="utf-8") as f:
                json_string = json.dumps(
                    log_entry, ensure_ascii=False, indent=4)
                f.write(json_string + "\n")
                logger.debug(f"Mục ghi log đã được ghi vào tệp: {calls_log}")
        except Exception as e:
            logger.error(f"Lỗi khi ghi mục log vào tệp: {str(e)}")
            raise

# Lớp để ghi log và xử lý các tương tác với mô hình chat
class LoggerChatModel:

    def __init__(self, llm: Union[OpenAIModel, OllamaModel, ClaudeModel, GeminiModel]):
        self.llm = llm
        logger.debug(f"LoggerChatModel đã được khởi tạo thành công với LLM: {llm}")

    def __call__(self, messages: List[Dict[str, str]]) -> str:
        logger.debug(f"Đang vào phương thức __call__ với messages: {messages}")
        while True:
            try:
                logger.debug("Đang cố gắng gọi LLM với messages")

                reply = self.llm.invoke(messages)
                logger.debug(f"Đã nhận được phản hồi từ LLM: {reply}")

                parsed_reply = self.parse_llmresult(reply)
                logger.debug(f"Phản hồi LLM đã được phân tích: {parsed_reply}")

                LLMLogger.log_request(
                    prompts=messages, parsed_reply=parsed_reply)
                logger.debug("Yêu cầu đã được ghi log thành công")

                return reply

            except httpx.HTTPStatusError as e:
                logger.error(f"Đã gặp HTTPStatusError: {str(e)}")
                if e.response.status_code == 429:
                    retry_after = e.response.headers.get('retry-after')
                    retry_after_ms = e.response.headers.get('retry-after-ms')

                    if retry_after:
                        wait_time = int(retry_after)
                        logger.warning(
                            f"Đã vượt quá giới hạn tốc độ. Đang đợi {wait_time} giây trước khi thử lại (trích xuất từ header 'retry-after')...")
                        time.sleep(wait_time)
                    elif retry_after_ms:
                        wait_time = int(retry_after_ms) / 1000.0
                        logger.warning(
                            f"Đã vượt quá giới hạn tốc độ. Đang đợi {wait_time} giây trước khi thử lại (trích xuất từ header 'retry-after-ms')...")
                        time.sleep(wait_time)
                    else:
                        wait_time = 30
                        logger.warning(
                            f"Không tìm thấy header 'retry-after'. Đang đợi {wait_time} giây trước khi thử lại (mặc định)...")
                        time.sleep(wait_time)
                else:
                    logger.error(f"Đã xảy ra lỗi HTTP với mã trạng thái: {e.response.status_code}, đang đợi 30 giây trước khi thử lại")
                    time.sleep(30)

            except Exception as e:
                logger.error(f"Đã xảy ra lỗi không mong đợi: {str(e)}")
                logger.info(
                    "Đang đợi 30 giây trước khi thử lại do lỗi không mong đợi.")
                time.sleep(30)
                continue

    def parse_llmresult(self, llmresult: AIMessage) -> Dict[str, Dict]:
        logger.debug(f"Đang phân tích kết quả LLM: {llmresult}")

        try:
            if hasattr(llmresult, 'usage_metadata'):
                content = llmresult.content
                response_metadata = llmresult.response_metadata
                id_ = llmresult.id
                usage_metadata = llmresult.usage_metadata

                parsed_result = {
                    "content": content,
                    "response_metadata": {
                        "model_name": response_metadata.get("model_name", ""),
                        "system_fingerprint": response_metadata.get("system_fingerprint", ""),
                        "finish_reason": response_metadata.get("finish_reason", ""),
                        "logprobs": response_metadata.get("logprobs", None),
                    },
                    "id": id_,
                    "usage_metadata": {
                        "input_tokens": usage_metadata.get("input_tokens", 0),
                        "output_tokens": usage_metadata.get("output_tokens", 0),
                        "total_tokens": usage_metadata.get("total_tokens", 0),
                    },
                }
            else :  
                content = llmresult.content
                response_metadata = llmresult.response_metadata
                id_ = llmresult.id
                token_usage = response_metadata['token_usage']

                parsed_result = {
                    "content": content,
                    "response_metadata": {
                        "model_name": response_metadata.get("model", ""),
                        "finish_reason": response_metadata.get("finish_reason", ""),
                    },
                    "id": id_,
                    "usage_metadata": {
                        "input_tokens": token_usage.prompt_tokens,
                        "output_tokens": token_usage.completion_tokens,
                        "total_tokens": token_usage.total_tokens,
                    },
                }                  
            logger.debug(f"Đã phân tích kết quả LLM thành công: {parsed_result}")
            return parsed_result

        except KeyError as e:
            logger.error(
                f"Lỗi KeyError khi phân tích kết quả LLM: thiếu khóa {str(e)}")
            raise

        except Exception as e:
            logger.error(
                f"Lỗi không mong đợi khi phân tích kết quả LLM: {str(e)}")
            raise

# Lớp chính để xử lý các câu hỏi và tạo câu trả lời từ GPT


class GPTAnswerer:

    def __init__(self, config, llm_api_key):
        # Khởi tạo đối tượng AIAdapter và LoggerChatModel
        self.ai_adapter = AIAdapter(config, llm_api_key)
        self.llm_cheap = LoggerChatModel(self.ai_adapter)

    @property
    def job_description(self):
        # Trả về mô tả công việc
        return self.job.description

    @staticmethod
    def find_best_match(text: str, options: list[str]) -> str:
        # Tìm sự trùng khớp tốt nhất giữa văn bản và các tùy chọn
        logger.debug(f"Tìm sự trùng khớp tốt nhất cho văn bản: '{text}' trong các tùy chọn: {options}")
        distances = [
            (option, distance(text.lower(), option.lower())) for option in options
        ]
        best_option = min(distances, key=lambda x: x[1])[0]
        logger.debug(f"Tìm thấy sự trùng khớp tốt nhất: {best_option}")
        return best_option

    @staticmethod
    def _remove_placeholders(text: str) -> str:
        # Xóa các placeholder khỏi văn bản
        logger.debug(f"Đang xóa các placeholder khỏi văn bản: {text}")
        text = text.replace("PLACEHOLDER", "")
        return text.strip()

    @staticmethod
    def _preprocess_template_string(template: str) -> str:
        # Tiền xử lý chuỗi mẫu
        logger.debug("Đang tiền xử lý chuỗi mẫu")
        return textwrap.dedent(template)

    def set_resume(self, resume):
        # Thiết lập thông tin sơ yếu lý lịch
        logger.debug(f"Đang thiết lập sơ yếu lý lịch: {resume}")
        self.resume = resume

    def set_job(self, job):
        # Thiết lập thông tin công việc và tóm tắt mô tả công việc
        logger.debug(f"Đang thiết lập công việc: {job}")
        self.job = job
        self.job.set_summarize_job_description(
            self.summarize_job_description(self.job.description))

    def set_job_application_profile(self, job_application_profile):
        # Thiết lập hồ sơ ứng tuyển công việc
        logger.debug(f"Đang thiết lập hồ sơ ứng tuyển công việc: {job_application_profile}")
        self.job_application_profile = job_application_profile

    def summarize_job_description(self, text: str) -> str:
        # Tóm tắt mô tả công việc
        logger.debug(f"Đang tóm tắt mô tả công việc: {text}")
        strings.summarize_prompt_template = self._preprocess_template_string(
            strings.summarize_prompt_template
        )
        prompt = ChatPromptTemplate.from_template(
            strings.summarize_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({"text": text})
        logger.debug(f"Đã tạo bản tóm tắt: {output}")
        return output

    def _create_chain(self, template: str):
        # Tạo chuỗi xử lý từ mẫu
        logger.debug(f"Đang tạo chuỗi xử lý với mẫu: {template}")
        prompt = ChatPromptTemplate.from_template(template)
        return prompt | self.llm_cheap | StrOutputParser()

    def answer_question_textual_wide_range(self, question: str) -> str:
        # Trả lời câu hỏi văn bản với phạm vi rộng
        logger.debug(f"Đang trả lời câu hỏi văn bản: {question}")
        chains = {
            "personal_information": self._create_chain(strings.personal_information_template),
            "self_identification": self._create_chain(strings.self_identification_template),
            "legal_authorization": self._create_chain(strings.legal_authorization_template),
            "work_preferences": self._create_chain(strings.work_preferences_template),
            "education_details": self._create_chain(strings.education_details_template),
            "experience_details": self._create_chain(strings.experience_details_template),
            "projects": self._create_chain(strings.projects_template),
            "availability": self._create_chain(strings.availability_template),
            "salary_expectations": self._create_chain(strings.salary_expectations_template),
            "certifications": self._create_chain(strings.certifications_template),
            "languages": self._create_chain(strings.languages_template),
            "interests": self._create_chain(strings.interests_template),
            "cover_letter": self._create_chain(strings.coverletter_template),
        }
        section_prompt = """You are assisting a bot designed to automatically apply for jobs on AIHawk. The bot receives various questions about job applications and needs to determine the most relevant section of the resume to provide an accurate response.

        For the following question: '{question}', determine which section of the resume is most relevant. 
        Respond with exactly one of the following options:
        - Personal information
        - Self Identification
        - Legal Authorization
        - Work Preferences
        - Education Details
        - Experience Details
        - Projects
        - Availability
        - Salary Expectations
        - Certifications
        - Languages
        - Interests
        - Cover letter

        Here are detailed guidelines to help you choose the correct section:

        1. **Personal Information**:
        - **Purpose**: Contains your basic contact details and online profiles.
        - **Use When**: The question is about how to contact you or requests links to your professional online presence.
        - **Examples**: Email address, phone number, AIHawk profile, GitHub repository, personal website.

        2. **Self Identification**:
        - **Purpose**: Covers personal identifiers and demographic information.
        - **Use When**: The question pertains to your gender, pronouns, veteran status, disability status, or ethnicity.
        - **Examples**: Gender, pronouns, veteran status, disability status, ethnicity.

        3. **Legal Authorization**:
        - **Purpose**: Details your work authorization status and visa requirements.
        - **Use When**: The question asks about your ability to work in specific countries or if you need sponsorship or visas.
        - **Examples**: Work authorization in EU and US, visa requirements, legally allowed to work.

        4. **Work Preferences**:
        - **Purpose**: Specifies your preferences regarding work conditions and job roles.
        - **Use When**: The question is about your preferences for remote work, in-person work, relocation, and willingness to undergo assessments or background checks.
        - **Examples**: Remote work, in-person work, open to relocation, willingness to complete assessments.

        5. **Education Details**:
        - **Purpose**: Contains information about your academic qualifications.
        - **Use When**: The question concerns your degrees, universities attended, GPA, and relevant coursework.
        - **Examples**: Degree, university, GPA, field of study, exams.

        6. **Experience Details**:
        - **Purpose**: Details your professional work history and key responsibilities.
        - **Use When**: The question pertains to your job roles, responsibilities, and achievements in previous positions.
        - **Examples**: Job positions, company names, key responsibilities, skills acquired.

        7. **Projects**:
        - **Purpose**: Highlights specific projects you have worked on.
        - **Use When**: The question asks about particular projects, their descriptions, or links to project repositories.
        - **Examples**: Project names, descriptions, links to project repositories.

        8. **Availability**:
        - **Purpose**: Provides information on your availability for new roles.
        - **Use When**: The question is about how soon you can start a new job or your notice period.
        - **Examples**: Notice period, availability to start.

        9. **Salary Expectations**:
        - **Purpose**: Covers your expected salary range.
        - **Use When**: The question pertains to your salary expectations or compensation requirements.
        - **Examples**: Desired salary range.

        10. **Certifications**:
            - **Purpose**: Lists your professional certifications or licenses.
            - **Use When**: The question involves your certifications or qualifications from recognized organizations.
            - **Examples**: Certification names, issuing bodies, dates of validity.

        11. **Languages**:
            - **Purpose**: Describes the languages you can speak and your proficiency levels.
            - **Use When**: The question asks about your language skills or proficiency in specific languages.
            - **Examples**: Languages spoken, proficiency levels.

        12. **Interests**:
            - **Purpose**: Details your personal or professional interests.
            - **Use When**: The question is about your hobbies, interests, or activities outside of work.
            - **Examples**: Personal hobbies, professional interests.

        13. **Cover Letter**:
            - **Purpose**: Contains your personalized cover letter or statement.
            - **Use When**: The question involves your cover letter or specific written content intended for the job application.
            - **Examples**: Cover letter content, personalized statements.

        Provide only the exact name of the section from the list above with no additional text.
        """
        prompt = ChatPromptTemplate.from_template(section_prompt)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({"question": question})

        # Tìm phần phù hợp nhất từ kết quả
        match = re.search(
            r"(Personal information|Self Identification|Legal Authorization|Work Preferences|Education "
            r"Details|Experience Details|Projects|Availability|Salary "
            r"Expectations|Certifications|Languages|Interests|Cover letter)",
            output, re.IGNORECASE)
        if not match:
            raise ValueError(
                "Không thể trích xuất tên phần từ phản hồi.")

        section_name = match.group(1).lower().replace(" ", "_")

        # Xử lý trường hợp đặc biệt cho thư xin việc
        if section_name == "cover_letter":
            chain = chains.get(section_name)
            output = chain.invoke(
                {"resume": self.resume, "job_description": self.job_description})
            logger.debug(f"Đã tạo thư xin việc: {output}")
            return output

        # Lấy thông tin từ sơ yếu lý lịch hoặc hồ sơ ứng tuyển
        resume_section = getattr(self.resume, section_name, None) or getattr(self.job_application_profile, section_name,
                                                                             None)
        if resume_section is None:
            logger.error(
                f"Không tìm thấy phần '{section_name}' trong sơ yếu lý lịch hoặc hồ sơ ứng tuyển.")
            raise ValueError(f"Không tìm thấy phần '{section_name}' trong sơ yếu lý lịch hoặc hồ sơ ứng tuyển.")
        
        # Tạo và thực thi chuỗi xử lý
        chain = chains.get(section_name)
        if chain is None:
            logger.error(f"Không định nghĩa chuỗi xử lý cho phần '{section_name}'")
            raise ValueError(f"Không định nghĩa chuỗi xử lý cho phần '{section_name}'")
        output = chain.invoke(
            {"resume_section": resume_section, "question": question})
        logger.debug(f"Đã trả lời câu hỏi: {output}")
        return output

    def answer_question_numeric(self, question: str, default_experience: int = 3) -> int:
        # Trả lời câu hỏi số
        logger.debug(f"Đang trả lời câu hỏi số: {question}")
        func_template = self._preprocess_template_string(
            strings.numeric_question_template)
        prompt = ChatPromptTemplate.from_template(func_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output_str = chain.invoke(
            {"resume_educations": self.resume.education_details, "resume_jobs": self.resume.experience_details,
             "resume_projects": self.resume.projects, "question": question})
        logger.debug(f"Kết quả thô cho câu hỏi số: {output_str}")
        try:
            output = self.extract_number_from_string(output_str)
            logger.debug(f"Số đã trích xuất: {output}")
        except ValueError:
            logger.warning(
                f"Không thể trích xuất số, sử dụng kinh nghiệm mặc định: {default_experience}")
            output = default_experience
        return output

    def extract_number_from_string(self, output_str):
        # Trích xuất số từ chuỗi
        logger.debug(f"Đang trích xuất số từ chuỗi: {output_str}")
        numbers = re.findall(r"\d+", output_str)
        if numbers:
            logger.debug(f"Đã tìm thấy số: {numbers}")
            return int(numbers[0])
        else:
            logger.error("Không tìm thấy số trong chuỗi")
            raise ValueError("Không tìm thấy số trong chuỗi")

    def answer_question_from_options(self, question: str, options: list[str]) -> str:
        # Trả lời câu hỏi từ các tùy chọn
        logger.debug(f"Đang trả lời câu hỏi từ các tùy chọn: {question}")
        func_template = self._preprocess_template_string(
            strings.options_template)
        prompt = ChatPromptTemplate.from_template(func_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output_str = chain.invoke(
            {"resume": self.resume, "question": question, "options": options})
        logger.debug(f"Kết quả thô cho câu hỏi tùy chọn: {output_str}")
        best_option = self.find_best_match(output_str, options)
        logger.debug(f"Tùy chọn tốt nhất đã xác định: {best_option}")
        return best_option

    def resume_or_cover(self, phrase: str) -> str:
        # Xác định xem cụm từ đề cập đến sơ yếu lý lịch hay thư xin việc
        logger.debug(
            f"Đang xác định xem cụm từ đề cập đến sơ yếu lý lịch hay thư xin việc: {phrase}")
        prompt_template = """
                Given the following phrase, respond with only 'resume' if the phrase is about a resume, or 'cover' if it's about a cover letter.
                If the phrase contains only one word 'upload', consider it as 'cover'.
                If the phrase contains 'upload resume', consider it as 'resume'.
                Do not provide any additional information or explanations.

                phrase: {phrase}
                """
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        response = chain.invoke({"phrase": phrase})
        logger.debug(f"Phản hồi cho resume_or_cover: {response}")
        if "resume" in response:
            return "resume"
        elif "cover" in response:
            return "cover"
        else:
            return "resume"