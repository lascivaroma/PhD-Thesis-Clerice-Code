import typing
import time

from tqdm import tqdm  # Progress bar

import torch
import torch.nn as nn
import torch.utils.data as torch_data
import numpy

from .data import Vocabulary, WordContextDataset
from .modules import CBOW

__all__ = [
    "Model"
]


DEVICE = torch.device('cpu')
if torch.cuda.is_available():
    DEVICE = torch.device('cuda')


class Model:
    def __init__(
            self,
            vocabulary: Vocabulary,
            embedding_size: int=100,
            window: typing.Tuple[int, int]=(5, 5)
    ):
        self.vocabulary = vocabulary
        self.embedding_size = embedding_size
        self.window = window
        self.model = CBOW(
            vocab_size=self.vocabulary.size(),
            embedding_dim=embedding_size
        )
        self.embeddings = None

    def train(
        self,
        dataset: WordContextDataset,
        epochs: int=100,
        lr: float= 0.001,
        batch_size: int=256,
        shuffle: bool= True,
        seed: typing.Optional[int]= None,
        verbose_iterval: int=1,
        device: str= DEVICE
    ):  # Mainly from https://github.com/goddoe/word2vec-pytorch/blob/c4f97a3a8fbeab577db24eec74fa8f61c1cc5c87/train.py
        # Set-up the device
        self.model.to(device)
        if seed:
            torch.manual_seed(seed)

        # Set-up the training optimized and loss
        loss_function = nn.NLLLoss()
        loss_list = []
        optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=lr
        )

        #  Set-up the dataset
        data_loader = torch_data.DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

        # sentences_size = len(dataset)
        for epoch in range(epochs):

            for context, target in tqdm(
                    data_loader,
                    desc="[Epoch %s/%s]" % (epoch+1, epochs)
            ):
                # If the current batch is too small
                if context.size()[0] != batch_size:
                    continue

                context = context.to(device)
                target = target.squeeze(1).to(device)

                # Emptying
                self.model.zero_grad()

                # Forward pass
                prediction = self.model(context)

                # Loss
                loss = loss_function(prediction, target)
                loss.backward()
                loss_list.append(float(loss.to("cpu").data.numpy()))

                # Optimizer
                optimizer.step()

            if epoch % verbose_iterval == 0:
                continue#print("loss : {:.3f}".format(loss_list[-1]))

        self.embeddings = self.model.embeddings.weight.detach().cpu().numpy()

    def n_closest(self, word, n=10)-> typing.List[str]:
        word_id = self.vocabulary.get_index(word)
        dists = numpy.dot(
            (self.embeddings - self.embeddings[word_id]) ** 2,
            numpy.ones(self.embeddings.shape[1])
        )
        closests = numpy.argsort(dists)[:n]
        return [self.vocabulary.get_word(idx) for idx in closests]
