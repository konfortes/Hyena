import json
import logging
import time
import urllib


class Transcribe:
    def __init__(self, client):
        self.client = client
        self.logger = logging.getLogger(__name__)

    def transcribe(self, s3_file_name: str, bucket_name: str) -> str:
        self.logger.info(f"Transcribing...")
        job_name = self.__start_transcribe_job(s3_file_name, bucket_name)

        return self.__get_transcribe_result(job_name)

    def __start_transcribe_job(self, s3_file_name: str, bucket_name: str) -> str:
        job_name = s3_file_name
        job_uri = f"s3://{bucket_name}/{s3_file_name}"

        self.client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": job_uri},
            MediaFormat="ogg",
            LanguageCode="en-US",
        )

        return job_name

    def __get_transcribe_result(self, job_name: str) -> str:

        status = self.__wait_for_job(job_name)

        if status and status["TranscriptionJob"]["TranscriptionJobStatus"] == "COMPLETED":
            self.logger.info("fetching result url")
            response = urllib.request.urlopen(status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"])
            data = json.loads(response.read())
            text = data["results"]["transcripts"][0]["transcript"]
            return text
        else:
            self.logger.warn(f"Transcription job {job_name} finished with FAILED status. status: {status}")

    def __wait_for_job(self, job_name: str):
        self.logger.info("Waiting for transcribe result")
        while True:
            status = self.client.get_transcription_job(TranscriptionJobName=job_name)
            if status["TranscriptionJob"]["TranscriptionJobStatus"] in ["COMPLETED", "FAILED"]:
                break
            self.logger.debug("Not ready yet")
            time.sleep(5)
        return status
