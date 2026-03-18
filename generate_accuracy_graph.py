import sys
import os
import matplotlib.pyplot as plt
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.valkyrie_decoder import ValkyrieDecoder
from training.trainer import ValkyrieTrainer
from utils.vocab import create_demo_vocabulary, vocab_size as get_vocab_size

def main():
    print("Initializing model to generate accuracy graph...")
    vocab = create_demo_vocabulary()
    vsize = get_vocab_size(vocab)
    model = ValkyrieDecoder(
        vocab_size = vsize,
        d_model    = 128,
        n_heads    = 4,
        n_layers   = 2,
        d_ff       = 256,
        dropout    = 0.1,
    )
    trainer = ValkyrieTrainer(model, lr=1e-3)

    epochs = 20
    accuracies = []
    losses = []

    print(f"Simulating training for {epochs} epochs...")
    for epoch in range(1, epochs + 1):
        # Simulate training batch
        bi = torch.randint(3, vsize, (4, 12))
        bt = torch.randint(3, vsize, (4, 12))
        train_metrics = trainer.train_step(bi, bt)
        
        # Simulate evaluation batch to get accuracy (verification_%)
        eval_metrics = trainer.evaluate_step(bi, bt)
        
        loss = train_metrics['loss']
        acc = eval_metrics['verification_%']
        
        losses.append(loss)
        accuracies.append(acc)
        print(f"Epoch {epoch}: Loss = {loss:.4f}, Verification Accuracy = {acc}%")

    # Plot
    plt.figure(figsize=(10, 5))
    
    # Subplot 1: Accuracy
    plt.subplot(1, 2, 1)
    plt.plot(range(1, epochs + 1), accuracies, marker='o', color='blue', label='Verification Accuracy (%)')
    plt.title('Accuracy over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    plt.grid(True)
    plt.legend()
    
    # Subplot 2: Loss
    plt.subplot(1, 2, 2)
    plt.plot(range(1, epochs + 1), losses, marker='o', color='red', label='Total Loss')
    plt.title('Loss over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    output_path = "accuracy_graph.png"
    plt.savefig(output_path)
    print(f"Graph saved successfully to {output_path}")

if __name__ == '__main__':
    main()
