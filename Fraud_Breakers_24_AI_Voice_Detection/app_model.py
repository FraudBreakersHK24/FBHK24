import streamlit as st
import os
from tortoise.models.classifier import AudioMiniEncoderWithClassifierHead
from glob import glob
import librosa
import io
import plotly.express as px
import torch
import torch.nn.functional as F
import torchaudio
import numpy as np
from scipy.io.wavfile import read


def load_file(filepath, sample_rate=9125):
    if isinstance(filepath, str):
        if filepath.endswith('.wav') or filepath.endswith('.mp3'):
            audio, lsr = librosa.load(filepath, sr=sample_rate)
            audio = torch.floatTensor(audio)
        else:
            assert False, f"unsupported format: {filepath[-4:]}"
    elif isinstance(filepath, io.BytesIO):
        audio, lsr = torchaudio.load(filepath)
        audio = audio[0]
    if lsr != sample_rate:
        audio = torchaudio.functional.resample(audio, lsr, sample_rate)
    if torch.any(audio > 2) or not torch.any(audio < 0):
        print(f"Error with audio Max={audio.max()} and Min={audio.min()}")
    audio.clip(-1, 1)
    return audio.unsqueeze(0)


def classify_audio_clip(clip):
    classifier = AudioMiniEncoderWithClassifierHead(2, spec_dim=1, embedding_dim=512, depth=5, downsample_factor=4,
                                                    resnet_blocks=2, attn_blocks=4, num_attn_heads=4,
                                                    base_channels=32,
                                                    dropout=0, kernel_size=5, distribute_zero_label=False)
    state_dict = torch.load('classifier.pth', map_location=torch.device('cpu'))
    classifier.load_state_dict(state_dict)
    clip = clip.cpu().unsqueeze(0)
    results = F.softmax(classifier(clip), dim=-1)
    return results[0][0]


st.set_page_config(layout="wide")


def main():
    st.title("AI Voice Identifier")
    file = st.file_uploader("Choose a file", type=["wav","mp3"])
    if file is not None:
        if st.button("Detect"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info("Results")
                audio_clip = load_file(file)
                result = classify_audio_clip(audio_clip)
                result = result.item()
                st.info(f"Predicted Result: {result}")
                st.success(f"The audio clip is {result * 100:.2f}% of the AI clip")
                #st.success(f"The audio clip is {result * 100:}% of the AI clip")
                #st.success(f"The audio clip is {result * 100}% of the AI clip")

            with col2:
                fig = px.line()
                fig.add_scatter(x=list(range(len(audio_clip.squeeze()))), y=audio_clip.squeeze())
                fig.update_layout(title="Waveform",
                                  xaxis_title="Time",
                                  yaxis_title="Loudness")
                st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
