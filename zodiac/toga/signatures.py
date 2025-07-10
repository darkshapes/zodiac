# SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# <!-- // /*  d a r k s h a p e s */ -->

import dspy


class Active(dspy.streaming.StatusMessageProvider):
    def lm_start_status_message(self):
        return "Processing.."

    def lm_end_status_message(self):
        return "Complete."


class QATask(dspy.Signature):
    """Reply with short responses within 60-90 word/10k character code limits"""

    question: str = dspy.InputField(desc="The question to respond to")
    answer = dspy.OutputField(desc="Often between 60 and 90 words and limited to 10000 character code blocks")


class QuestionAnswer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(QATask)

    def forward(self, question, **kwargs):
        self.predict(question=question, **kwargs)
        return self.predict(question=question, **kwargs)


qa_program = dspy.streamify(
    QuestionAnswer(),
    stream_listeners=[
        dspy.streaming.StreamListener(signature_field_name="answer"),  # allow_reuse=True),
    ],
)


# class VisionTask(dspy.Signature):
#     """Describe the image in detail."""

#     image: dspy.Image = dspy.InputField(desc="An image")
#     description: str = dspy.OutputField(desc="Detailed description of the image.")


# image_path="image.png"
# minicpm = dspy.LM('openai/gemma3:12b-it-qat', base_url='http://localhost:11454/v1', api_key='ollama', cache=False)

# predictor = dspy.Predict(signature)
# predictor.set_lm(minicpm)
# result = predictor(image=dspy.Image.from_url(image_path))
# print(result.description)

# dspy.Audio


# class SpeechTask(dspy.Signature):
#     f"""{bqa_sysprompt}"""

#     message: str = dspy.InputField(desc="The message to respond to")
#     # history: dspy.History = dspy.InputField()
#     answer = dspy.OutputField(desc="Often between 60 and 90 words and limited to 10000 character code blocks")


# class T2ASignature(dspy.Signature):
#     f"""Reply with short responses within 60-90 word/10k character code limits"""

#     audio: dspy.Image = dspy.InputField(desc="An image")

#     message: str = dspy.InputField(desc="The message to respond to")
#     # history: dspy.History = dspy.InputField()
#     answer = dspy.OutputField(desc="Often between 60 and 90 words and limited to 10000 character code blocks")

# class A2TSignature(dspy.Signature):
#     f"""Reply with short responses within 60-90 word/10k character code limits"""

#     audio: dspy.Image = dspy.InputField(desc="An image")

#     message: str = dspy.InputField(desc="The message to respond to")
#     # history: dspy.History = dspy.InputField()
#     answer = dspy.OutputField(desc="Often between 60 and 90 words and limited to 10000 character code blocks")

# class T2ISignature(dspy.Signature):
#     message: str = dspy.InputField(desc=is_msg)
#     image_output: dspy.Image = dspy.OutputField(desc=is_out)


# class I2ISignature(dspy.Signature):
#     f"""{ps_sysprompt}"""
#     image_input: dspy.Image = dspy.InputField(desc="An image")
#     answer: str = dspy.OutputField(desc="The nature of the image.")
#     image_output: dspy.Image = dspy.OutputField(desc="Edited input image.")


# ps_sysprompt = "Provide x for Y"
# bqa_sysprompt =

# is_msg: str = "Description x of the image to generate"
# is_out: str = "An image matching the description x"


# class ControlNetSignature(dspy.Signature):


# class SequenceSignature(dspy.Signature

# class VisionSignature(dspy.Signature:

# class ImageToImageSignature(dspy.Signature:

# class InpaintSignature(dspy.Signature:

# CasualLM
# PAG
