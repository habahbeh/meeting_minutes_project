# ===========================================
# meetings/services.py
# ===========================================

import openai
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import Document
from django.conf import settings


class MeetingProcessor:
    """معالج الاجتماعات"""

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.llm = ChatOpenAI(
            model="gpt-4o",
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0.3
        )

    def audio_to_text(self, audio_file_path):
        """تحويل الصوت إلى نص باستخدام Whisper"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ar"  # يمكن تركه فارغ للكشف التلقائي
                )
            return transcript.text
        except Exception as e:
            raise Exception(f"خطأ في تحويل الصوت إلى نص: {str(e)}")

    def create_summary(self, text):
        """إنشاء تلخيص للنص"""
        try:
            # تقسيم النص إلى أجزاء صغيرة
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000,
                chunk_overlap=200
            )

            docs = [Document(page_content=text)]
            split_docs = text_splitter.split_documents(docs)

            # قالب التلخيص
            summary_prompt = PromptTemplate(
                template="""
                قم بتلخيص هذا الجزء من محادثة الاجتماع بطريقة واضحة ومفيدة:

                {text}

                التلخيص:
                """,
                input_variables=["text"]
            )

            # إنشاء سلسلة التلخيص
            summary_chain = load_summarize_chain(
                self.llm,
                chain_type="map_reduce",
                map_prompt=summary_prompt,
                combine_prompt=summary_prompt
            )

            summary = summary_chain.run(split_docs)
            return summary

        except Exception as e:
            raise Exception(f"خطأ في إنشاء التلخيص: {str(e)}")

    def create_minutes(self, text):
        """إنشاء محضر اجتماع منظم"""
        try:
            minutes_prompt = f"""
            قم بإنشاء محضر اجتماع منظم ومفصل من النص التالي:

            {text}

            يجب أن يتضمن المحضر الأقسام التالية:

            📋 **ملخص عام للاجتماع:**

            🔸 **النقاط الرئيسية المناقشة:**

            ✅ **القرارات المتخذة:**

            📝 **المهام والمسؤوليات:**

            ⏭️ **الخطوات التالية:**

            اكتب المحضر بشكل احترافي ومنظم باللغة العربية:
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": minutes_prompt}],
                temperature=0.3,
                max_tokens=2000
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"خطأ في إنشاء محضر الاجتماع: {str(e)}")

    def process_meeting(self, meeting):
        """معالجة الاجتماع كاملة"""
        try:
            # 1. تحويل الصوت إلى نص
            transcript = self.audio_to_text(meeting.audio_file.path)
            meeting.transcript = transcript
            meeting.save()

            # 2. إنشاء التلخيص
            summary = self.create_summary(transcript)
            meeting.summary = summary
            meeting.save()

            # 3. إنشاء المحضر
            minutes = self.create_minutes(transcript)
            meeting.minutes = minutes
            meeting.save()

            return True, "تم معالجة الاجتماع بنجاح"

        except Exception as e:
            return False, f"خطأ في معالجة الاجتماع: {str(e)}"