import torch
import torchvision.transforms as T
from PIL import Image

class ReIDEncoder:
    def __init__(self, device=None):
        self.device = device or ('mps' if torch.backends.mps.is_available() else 'cuda' if torch.cuda.is_available() else 'cpu')
        
        try:
            import torchreid
            self.model = torchreid.models.build_model(
                name='osnet_x1_0',
                num_classes=751, # Market1501
                loss='softmax',
                pretrained=True
            )
            # Embedding dim is 512
            self.embedding_dim = 512
        except ImportError:
            import torchvision.models as models
            self.model = models.resnet18(pretrained=True)
            self.model.fc = torch.nn.Identity() # remove classification head
            print("WARNING: torchreid not found, using ResNet18 placeholder")
            self.embedding_dim = 512

        self.model.eval()
        self.model.to(self.device)
        
        self.transform = T.Compose([
            T.Resize((256, 128)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def encode(self, frame_crop):
        """
        frame_crop: numpy array (H, W, C) in BGR (from OpenCV)
        returns: normalized numpy array embedding
        """
        rgb_crop = frame_crop[:, :, ::-1]
        pil_img = Image.fromarray(rgb_crop)
        
        input_tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            features = self.model(input_tensor)
            
        features = torch.nn.functional.normalize(features, p=2, dim=1)
        return features.cpu().numpy()[0]
