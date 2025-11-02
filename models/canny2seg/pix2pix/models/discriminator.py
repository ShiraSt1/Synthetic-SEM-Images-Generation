import torch.nn as nn

class PatchDiscriminator(nn.Module):
    def __init__(self, in_ch=4, base=64):
        super().__init__()
        def C(ic, oc, norm=True):
            seq = [nn.Conv2d(ic, oc, 4, 2, 1, bias=False)]
            if norm: seq.append(nn.BatchNorm2d(oc))
            seq.append(nn.LeakyReLU(0.2, inplace=True))
            return nn.Sequential(*seq)
        self.net = nn.Sequential(
            C(in_ch, base, norm=False),
            C(base, base*2),
            C(base*2, base*4),
            nn.Conv2d(base*4, 1, 4, 1, 1)
        )

    def forward(self, x):
        return self.net(x)
