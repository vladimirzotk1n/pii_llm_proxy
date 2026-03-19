import re

from src.config import get_settings

settings = get_settings()


def create_mask(tag_ids: list[int], tokens: list[str]) -> dict[str, str]:
    masking_map = {}

    current_word = ""
    current_tag = None

    for tag_id, token in zip(tag_ids, tokens):
        tag = settings.tags[tag_id]

        if tag.startswith("B-") or tag.startswith("I-"):
            tag = tag[2:]

        if token.startswith("##"):
            current_word += token[2:]
        else:
            if current_word:
                masking_map[current_word] = current_tag
            current_word = token
            current_tag = tag

    # остаток
    if current_word:
        masking_map[current_word] = current_tag

    return masking_map


def mask_prompt(prompt: str, mask_mapping: dict[str, str]) -> str:
    masked_prompt = prompt
    unmasking_mapping = {}
    sorted_mapping = sorted(mask_mapping.items(), key=lambda x: len(x[0]), reverse=True)

    placeholder_counter = {p: 1 for p in set(mask_mapping.values())}

    for key, placeholder in sorted_mapping:
        while key in masked_prompt:
            index = placeholder_counter[placeholder]
            mask = f"[[{placeholder}_{index}]]"
            masked_prompt = masked_prompt.replace(key, mask, 1)
            unmasking_mapping[mask] = key
            placeholder_counter[placeholder] += 1

    return masked_prompt, unmasking_mapping


TOKEN_RE = re.compile(r"\[\[(\w+?)_(\d+)\]\]")


class Unmasker:
    def __init__(self, unmapping: dict[str, str]):
        self.unmapping = unmapping
        self.buffer = ""

    def process(self, chunk: str) -> str:
        """[[NAME_i]] - ключ такой будет"""
        self.buffer += chunk
        output = ""

        while match := TOKEN_RE.search(self.buffer):
            start, end = match.span()
            output += self.buffer[:start]

            tag = match.group(0)
            if tag in self.unmapping:
                output += self.unmapping[tag]
            else:
                output += tag

            self.buffer = self.buffer[end:]

        return output
