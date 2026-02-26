import gzip
import html
import os
from functools import lru_cache
from typing import List, Tuple, Dict, Set, Optional, Any

import ftfy
import regex as re


@lru_cache()
def default_bpe() -> str:
    """Returns the default BPE vocabulary file path."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "bpe_simple_vocab_16e6.txt.gz")


@lru_cache()
def bytes_to_unicode() -> Dict[int, str]:
    """
    Returns a mapping from byte values (0-255) to Unicode characters.
    
    This mapping is used to convert between bytes and Unicode characters,
    avoiding issues with whitespace and control characters.
    """
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
    cs = bs[:]
    n = 0
    for b in range(2**8):
        if b not in bs:
            bs.append(b)
            cs.append(2**8 + n)
            n += 1
    cs = [chr(n) for n in cs]
    return dict(zip(bs, cs))


def get_pairs(word: Tuple[str, ...]) -> Set[Tuple[str, str]]:
    """Return set of symbol pairs in a word.
    
    Args:
        word: A tuple of symbols (strings).
        
    Returns:
        A set of tuples representing adjacent symbol pairs.
    """
    pairs = set()
    prev_char = word[0]
    for char in word[1:]:
        pairs.add((prev_char, char))
        prev_char = char
    return pairs


def basic_clean(text: str) -> str:
    """Clean text by fixing encoding and unescaping HTML entities."""
    text = ftfy.fix_text(text)
    text = html.unescape(html.unescape(text))
    return text.strip()


def whitespace_clean(text: str) -> str:
    """Normalize whitespace in text."""
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


class SimpleTokenizer:
    """A BPE-based tokenizer for text processing.
    
    This tokenizer is based on the GPT-2 tokenizer implementation.
    It converts text into token IDs using Byte Pair Encoding.
    """
    
    def __init__(self, bpe_path: str = default_bpe()) -> None:
        """Initialize the tokenizer.
        
        Args:
            bpe_path: Path to the BPE vocabulary file.
        """
        self.byte_encoder = bytes_to_unicode()
        self.byte_decoder = {v: k for k, v in self.byte_encoder.items()}
        
        # Load BPE merges
        with gzip.open(bpe_path, 'rt', encoding='utf-8') as f:
            merges = f.read().split('\n')
        merges = merges[1:49152 - 256 - 2 + 1]
        merges = [tuple(merge.split()) for merge in merges]
        
        # Build vocabulary
        vocab = list(bytes_to_unicode().values())
        vocab = vocab + [v + '</w>' for v in vocab]
        for merge in merges:
            vocab.append(''.join(merge))
        vocab.extend(['<|startoftext|>', '<|endoftext|>'])
        
        self.encoder = dict(zip(vocab, range(len(vocab))))
        self.decoder = {v: k for k, v in self.encoder.items()}
        self.bpe_ranks = dict(zip(merges, range(len(merges))))
        self.cache = {'<|startoftext|>': '<|startoftext|>', '<|endoftext|>': '<|endoftext|>'}
        self.pat = re.compile(r"""<\|startoftext\|>|<\|endoftext\|>|'s|'t|'re|'ve|'m|'ll|'d|[\p{L}]+|[\p{N}]|[^\s\p{L}\p{N}]+""", re.IGNORECASE)

    def bpe(self, token: str) -> str:
        """Apply BPE encoding to a token.
        
        Args:
            token: Input token to encode.
            
        Returns:
            Encoded token string.
        """
        if token in self.cache:
            return self.cache[token]
        
        word = tuple(token[:-1]) + (token[-1] + '</w>',)
        pairs = get_pairs(word)

        if not pairs:
            return token + '</w>'

        # Add max iterations to prevent infinite loops
        max_iterations = 1000
        iteration = 0
        while pairs and iteration < max_iterations:
            bigram = min(pairs, key=lambda pair: self.bpe_ranks.get(pair, float('inf')))
            if bigram not in self.bpe_ranks:
                break
            first, second = bigram
            new_word = []
            i = 0
            while i < len(word):
                try:
                    j = word.index(first, i)
                    new_word.extend(word[i:j])
                    i = j
                except ValueError:
                    new_word.extend(word[i:])
                    break

                if word[i] == first and i < len(word) - 1 and word[i + 1] == second:
                    new_word.append(first + second)
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            word = tuple(new_word)
            if len(word) == 1:
                break
            pairs = get_pairs(word)
            iteration += 1

        word = ' '.join(word)
        self.cache[token] = word
        return word

    def encode(self, text: str) -> List[int]:
        """Encode text into token IDs.
        
        Args:
            text: Input text to encode.
            
        Returns:
            List of token IDs.
        """
        bpe_tokens = []
        text = whitespace_clean(basic_clean(text)).lower()
        for token in re.findall(self.pat, text):
            token = ''.join(self.byte_encoder[b] for b in token.encode('utf-8'))
            bpe_tokens.extend(self.encoder[bpe_token] for bpe_token in self.bpe(token).split(' '))
        return bpe_tokens

    def decode(self, tokens: List[int]) -> str:
        """Decode token IDs back into text.
        
        Args:
            tokens: List of token IDs to decode.
            
        Returns:
            Decoded text.
        """
        text = ''.join([self.decoder[token] for token in tokens])
        text = bytearray([self.byte_decoder[c] for c in text]).decode('utf-8', errors="replace").replace('</w>', ' ')
        return text
