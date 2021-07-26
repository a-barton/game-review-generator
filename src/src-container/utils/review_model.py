from .aws_utils import download_s3_file, download_s3_folder, upload_s3_file, upload_s3_folder
from .logging import LOGGER
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments

class ReviewModel:

    def __init__(self, model_checkpoint=None, tokenizer_name=None, 
        location='aws', bucket=None, block_size=128, **kwargs):
        default_model = 'EleutherAI/gpt-neo-125M' if location=='aws' else 'gpt2'
        default_tokenizer = 'gpt2'
        self.model_checkpoint = model_checkpoint or default_model
        self.tokenizer_name = tokenizer_name or default_tokenizer
        self.location = location
        self.bucket = bucket
        self.block_size = block_size

    def predict(self, prompt_input_path, prompt_output_path, max_length):
        LOGGER.info("Downloading model and input prompt")
        if self.location == 'aws':
            download_s3_folder(self.bucket, self.model_checkpoint, self.model_checkpoint)
            download_s3_file(self.bucket, prompt_input_path, prompt_input_path)
        prompt = open(prompt_input_path).read()
        tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_name)
        model = AutoModelForCausalLM.from_pretrained(self.model_checkpoint)
        LOGGER.info("Tokenizing prompt input")
        input = tokenizer.encode(prompt, return_tensors="pt")
        LOGGER.info("Running model inference on prompt")
        generated = model.generate(input, max_length=max_length)
        resulting_string = tokenizer.decode(generated.tolist()[0])
        LOGGER.info("Saving generated output")
        open(prompt_output_path, mode='w').write(resulting_string)
        if self.location == 'aws':
            upload_s3_file(self.bucket, self.prompt_output_path, self.promp_output_path)
        return

    def fine_tune(self, data_path, model_save_path):
        dataset = self._load_fine_tuning_data(data_path)
        LOGGER.info("Dataset loaded")
        tokenized_dataset = self._tokenize_dataset(dataset)
        LOGGER.info("Dataset tokenized")
        lm_dataset = tokenized_dataset.map(
            self._group_texts,
            batched=True,
            batch_size=1000,
            num_proc=4
        )
        LOGGER.info("Dataset prepared for training")
        model = AutoModelForCausalLM.from_pretrained(self.model_checkpoint)
        training_args = TrainingArguments(
            "model-training",
            evaluation_strategy = "epoch",
            learning_rate=2e-5,
            weight_decay=0.01
        )
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=lm_dataset["train"],
            eval_dataset=lm_dataset["train"] # Not concerned with evaluation metrics
        )
        LOGGER.info("Commencing training")
        trainer.train()
        LOGGER.info("Saving and uploading fine tuned model")
        trainer.save_model(model_save_path)
        if self.location == 'aws':
            upload_s3_folder(self.bucket, model_save_path, model_save_path)
        return


    def _load_fine_tuning_data(self, data_path):
        if self.location == 'aws':
            download_s3_file(self.bucket, data_path, data_path)
        dataset = load_dataset('csv', data_files=data_path)
        return dataset

    def _tokenize_function(self, data, tokenizer):
        return tokenizer(data["review"])

    def _tokenize_dataset(self, dataset):
        tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_name, use_fast=True)
        tokenized_dataset = dataset.map(
            self._tokenize_function,
            fn_kwargs={'tokenizer':tokenizer},
            batched=True, 
            num_proc=4, 
            remove_columns=["review"])
        return tokenized_dataset

    def _group_texts(self, dataset):
        # Concatenate all texts.
        concatenated_examples = {k: sum(dataset[k], []) for k in dataset.keys()}
        total_length = len(concatenated_examples[list(dataset.keys())[0]])
        # We drop the small remainder, we could add padding if the model supported it instead of this drop, you can
            # customize this part to your needs.
        total_length = (total_length // self.block_size) * self.block_size
        # Split by chunks of max_len.
        result = {
            k: [t[i : i + self.block_size] for i in range(0, total_length, self.block_size)]
            for k, t in concatenated_examples.items()
        }
        result["labels"] = result["input_ids"].copy()
        return result
