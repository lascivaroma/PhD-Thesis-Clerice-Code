import torch.nn as nn
import torch.nn.functional as functional
import torch


from .data import Vocabulary


# See https://github.com/endymecy/pytorch-nlp/blob/master/nlp/word_embeddings/model.py
#       for better impl


class CBOW_b(nn.Module):
    def __init__(self, vocabulary: Vocabulary, embedding_size: int=100):
        super(CBOW_b, self).__init__()
        self.embeddings = nn.Embedding(vocabulary.size(), embedding_size)
        self.linear1 = nn.Linear(embedding_size, vocabulary.size())

    def forward(self, inputs):
        lookup_embeds = self.embeddings(inputs)
        embeds = lookup_embeds.sum(dim=0)
        out = self.linear1(embeds)
        out = functional.log_softmax(out, dim=0)
        return out


class CBOW(nn.Module):
    """
    def __init__(self, vocabulary: Vocabulary, embedding_size: int=100):
        super(CBOW, self).__init__()
        vocab_size = vocabulary.size()
        self.embeddings = nn.Embedding(vocab_size, embedding_size)
        self.linear = nn.Linear(embedding_size, vocab_size)
        print(self.embeddings, self.linear)

    def forward(self, inputs):
        embeds = self.embeddings(inputs)
        bow = torch.sum(embeds, 1)
        logits = self.linear(bow)
        return logits
    """

    def __init__(self, vocab_size, embedding_dim):
        super(CBOW, self).__init__()
        """
        Args:
            vocab_size (int): size of vocabulary.
            embed_dim (int): dimension of embedding.
        """
        super(CBOW, self).__init__()

        self.embeddings = nn.Embedding(vocab_size, embedding_dim)
        self.linear_proj = nn.Linear(embedding_dim, vocab_size)

    def forward(self, X):
        """Embed sequence and get word distribution of prediction.
        Args:
            X: inputs, shape of (batch_size, sequence)
        Returns:
            tensor, word distribution
        """

        # (batch_size, sequence) -> (batch_size, sequence, embedding)
        embed = self.embeddings(X)
        embed = torch.sum(embed, dim=1)
        out = self.linear_proj(embed)
        word_dist = functional.log_softmax(out, dim=1)

        return word_dist


"""
        # out: 1 x emdedding_dim
        self.embeddings = nn.Embedding(vocab_size, embedding_dim)

        self.linear1 = nn.Linear(embedding_dim, output_dim)

        self.activation_function1 = nn.ReLU()

        # out: 1 x vocab_size
        self.linear2 = nn.Linear(output_dim, vocab_size)

        self.activation_function2 = nn.LogSoftmax(dim=-1)

    def forward(self, inputs):
        embeds = sum(self.embeddings(inputs)).view(1, -1)
        out = self.linear1(embeds)
        out = self.activation_function1(out)
        out = self.linear2(out)
        out = self.activation_function2(out)
        return out
"""