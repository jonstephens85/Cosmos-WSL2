import subprocess
import gradio as gr

# Define aspect ratios with corresponding width and height
aspect_ratios = [
    {"label": "1:1", "width": 960, "height": 960},
    {"label": "4:3", "width": 960, "height": 704},
    {"label": "3:4", "width": 704, "height": 960},
    {"label": "16:9", "width": 1280, "height": 704},
    {"label": "9:16", "width": 704, "height": 1280},
]

# Map GPU types to offload options
def get_gpu_offload_map(model_size):
    if model_size == "7B":
        return {
            "3090/4090/5090": [
                "--offload_prompt_upsampler",
                "--offload_guardrail_models",
                "--offload_tokenizer",
                "--offload_diffusion_transformer",
                "--offload_text_encoder_model",
            ],
            "A6000/6000 Ada": [
                "--offload_prompt_upsampler",
                "--offload_guardrail_models",
                "--offload_text_encoder_model",
            ],
            "H100": [],
        }
    elif model_size == "14B":
        return {
            "A6000/6000 Ada": [
                "--offload_prompt_upsampler",
                "--offload_guardrail_models",
                "--offload_tokenizer",
                "--offload_diffusion_transformer",
                "--offload_text_encoder_model",
            ],
            "H100": [
                "--offload_prompt_upsampler",
            ],
        }
    return {}

# Function to generate arguments based on GPU type and model size
def get_offload_args(gpu_type, model_size):
    gpu_offload_map = get_gpu_offload_map(model_size)
    return gpu_offload_map.get(gpu_type, [])

# Function to run text2world.py
def generate_text2world(
    prompt,
    model_size,
    gpu_type,
    seed,
    aspect_ratio,
    fps,
    video_save_name,
    disable_prompt_upsampler,
):
    # Get width and height based on aspect ratio
    selected_ar = next(ar for ar in aspect_ratios if ar["label"] == aspect_ratio)
    width = selected_ar["width"]
    height = selected_ar["height"]

    args = [
        "PYTHONPATH=$(pwd) python cosmos1/models/diffusion/inference/text2world.py",
        "--checkpoint_dir checkpoints",
        f"--diffusion_transformer_dir Cosmos-1.0-Diffusion-{model_size}-Text2World",
        f'--prompt "{prompt}"',
        f"--video_save_name {video_save_name}",
        f"--seed {seed}",
        f"--height {height}",
        f"--width {width}",
        f"--fps {fps}",
    ]

    if disable_prompt_upsampler:
        args.append("--disable_prompt_upsampler")
        if prompt:
            args.extend([f'--prompt "{prompt}"'])
        else:
            raise ValueError("Prompt is required when prompt upsampler is disabled.")

    args.extend(get_offload_args(gpu_type, model_size))

    command = " ".join(args)
    subprocess.run(command, shell=True)

    video_path = f"outputs/{video_save_name}.mp4"
    return video_path

# Function to run video2world.py
def generate_video2world(
    input_file,
    model_size,
    gpu_type,
    num_input_frames,
    prompt,
    disable_prompt_upsampler,
    seed,
    aspect_ratio,
    fps,
    video_save_name,
):
    # Get width and height based on aspect ratio
    selected_ar = next(ar for ar in aspect_ratios if ar["label"] == aspect_ratio)
    width = selected_ar["width"]
    height = selected_ar["height"]

    args = [
        "PYTHONPATH=$(pwd) python cosmos1/models/diffusion/inference/video2world.py",
        "--checkpoint_dir checkpoints",
        f"--diffusion_transformer_dir Cosmos-1.0-Diffusion-{model_size}-Video2World",
        f"--input_image_or_video_path {input_file}",
        f"--video_save_name {video_save_name}",
        f"--seed {seed}",
        f"--num_input_frames {num_input_frames}",
        f"--height {height}",
        f"--width {width}",
        f"--fps {fps}",
    ]

    if disable_prompt_upsampler:
        args.append("--disable_prompt_upsampler")
        if prompt:
            args.extend([f'--prompt "{prompt}"'])
        else:
            raise ValueError("Prompt is required when prompt upsampler is disabled.")

    args.extend(get_offload_args(gpu_type, model_size))

    command = " ".join(args)
    subprocess.run(command, shell=True)

    video_path = f"outputs/{video_save_name}.mp4"
    return video_path

# Create Gradio interface
with gr.Blocks(theme="dark") as demo:
    gr.Markdown("# Cosmos Diffusion-based World Foundation Models Demo", elem_id="title")

    def update_gpu_options(model_size):
        if model_size == "7B":
            return gr.update(choices=["3090/4090/5090", "A6000/6000 Ada", "H100"], value="3090/4090/5090")
        elif model_size == "14B":
            return gr.update(choices=["A6000/6000 Ada", "H100"], value="A6000/6000 Ada")

    with gr.Tab("Text2World"):
        with gr.Row():
            with gr.Column():
                text_prompt = gr.Textbox(label="Text Prompt", lines=5)
                model_size_text = gr.Radio(["7B", "14B"], label="Model Size", value="7B")
                gpu_type_text = gr.Dropdown(label="GPU Type", choices=["3090/4090/5090", "A6000/6000 Ada", "H100"], value="3090/4090/5090")

                model_size_text.change(
                    update_gpu_options,
                    inputs=[model_size_text],
                    outputs=[gpu_type_text]
                )

                output_file_name_text = gr.Textbox(
                    label="Output File Name",
                    lines=1,
                    info="Specify the name of the output video file (optional, default: output_text2world)",
                )
                seed_text = gr.Number(label="Seed", value=1)
                disable_prompt_upsampler_text = gr.Checkbox(label="Disable Prompt Upsampler")
                aspect_ratio_text = gr.Dropdown(
                    choices=[ar["label"] for ar in aspect_ratios], label="Aspect Ratio", value="16:9"
                )
                fps_text = gr.Number(label="FPS", value=24, info="From 12 to 40 possible fps is supported")
                generate_button_text = gr.Button("Generate Video")

            with gr.Column():
                output_video_text = gr.Video(label="Generated Video")

            generate_button_text.click(
                generate_text2world,
                inputs=[
                    text_prompt,
                    model_size_text,
                    gpu_type_text,
                    seed_text,
                    aspect_ratio_text,
                    fps_text,
                    output_file_name_text,
                    disable_prompt_upsampler_text,
                ],
                outputs=output_video_text,
            )

    with gr.Tab("Video2World"):
        with gr.Row():
            with gr.Column():
                input_file = gr.File(label="Input Image/Video")
                model_size_video = gr.Radio(["7B", "14B"], label="Model Size", value="7B")
                gpu_type_video = gr.Dropdown(label="GPU Type", choices=["3090/4090/5090", "A6000/6000 Ada", "H100"], value="3090/4090/5090")

                model_size_video.change(
                    update_gpu_options,
                    inputs=[model_size_video],
                    outputs=[gpu_type_video]
                )

                num_input_frames_video = gr.Slider(1, 9, step=1, label="Number of Input Frames", value=1)
                text_prompt_video = gr.Textbox(label="Text Prompt (Optional)", lines=5)
                disable_prompt_upsampler_video = gr.Checkbox(label="Disable Prompt Upsampler")
                seed_video = gr.Number(label="Seed", value=1)
                aspect_ratio_video = gr.Dropdown(
                    choices=[ar["label"] for ar in aspect_ratios], label="Aspect Ratio", value="16:9"
                )
                fps_video = gr.Number(label="FPS", value=24, info="From 12 to 40 possible fps is supported")
                output_file_name_video = gr.Textbox(
                    label="Output File Name",
                    lines=1,
                    info="Specify the name of the output video file (optional, default: output_video2world)",
                )
                generate_button_video = gr.Button("Generate Video")

            with gr.Column():
                output_video_video = gr.Video(label="Generated Video")

            generate_button_video.click(
                generate_video2world,
                inputs=[
                    input_file,
                    model_size_video,
                    gpu_type_video,
                    num_input_frames_video,
                    text_prompt_video,
                    disable_prompt_upsampler_video,
                    seed_video,
                    aspect_ratio_video,
                    fps_video,
                    output_file_name_video,
                ],
                outputs=output_video_video,
            )

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0", server_port=7860)